from sqlalchemy.orm import Session

from jay.decisions.models import DecisionLedger


class DecisionPatternDetector:
    def __init__(self, session: Session):
        self.session = session

    def detect(self) -> list[dict]:
        patterns = []
        decisions = (
            self.session.query(DecisionLedger)
            .filter(
                DecisionLedger.outcome_status.in_(
                    ["Success", "Partial Success", "Failure"]
                )
            )
            .all()
        )

        failures = [d for d in decisions if d.outcome_status == "Failure"]
        successes = [d for d in decisions if d.outcome_status == "Success"]

        # 1. Repeated Mistake (No evidence provided)
        no_evidence_failures = [d for d in failures if not d.evidence]
        if len(no_evidence_failures) >= 2:
            patterns.append(
                {
                    "pattern_type": "Repeated Mistake",
                    "description": f"{len(no_evidence_failures)} decisions failed where no evidence was considered.",
                    "severity": "High",
                }
            )

        # 2. Repeated Successes
        strong_evidence_successes = [d for d in successes if len(d.evidence) >= 2]
        if len(strong_evidence_successes) >= 2:
            patterns.append(
                {
                    "pattern_type": "Repeated Success",
                    "description": f"{len(strong_evidence_successes)} successful decisions had 2 or more pieces of evidence.",
                    "severity": "Low",
                }
            )

        # 3. Decision Biases (Single option)
        single_option_failures = [d for d in failures if len(d.options_considered) <= 1]
        if len(single_option_failures) >= 2:
            patterns.append(
                {
                    "pattern_type": "Decision Bias",
                    "description": f"{len(single_option_failures)} failed decisions considered 1 or fewer alternative options.",
                    "severity": "Medium",
                }
            )

        return patterns
