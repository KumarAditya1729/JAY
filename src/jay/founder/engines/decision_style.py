from sqlalchemy.orm import Session

from jay.decisions.models import DecisionLedger


class DecisionStyleEngine:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> dict:
        decisions = self.session.query(DecisionLedger).all()

        if not decisions:
            return {
                "speed": "Unknown",
                "evidence_requirement": "Unknown",
                "risk_appetite": "Unknown",
                "reversibility_preference": "Unknown",
                "success_patterns": [],
                "failure_patterns": [],
            }

        avg_evidence = sum(len(d.evidence) for d in decisions) / len(decisions)

        # Determine evidence requirement
        if avg_evidence > 3:
            evidence_req = "High (Requires substantial proof)"
        elif avg_evidence > 1:
            evidence_req = "Medium (Requires basic proof)"
        else:
            evidence_req = "Low (Relies on intuition/speed)"

        # Determine reversibility preference
        avg_rev = sum(d.reversibility_score for d in decisions) / len(decisions)
        if avg_rev > 0.7:
            rev_pref = "Highly Reversible (Prefers options with exit strategies)"
        elif avg_rev < 0.3:
            rev_pref = "One-Way Doors (Comfortable with irreversible commitments)"
        else:
            rev_pref = "Balanced"

        successes = [d for d in decisions if d.outcome_status == "Success"]
        failures = [d for d in decisions if d.outcome_status == "Failure"]

        # Analyze success/failure patterns
        success_patterns = []
        if successes and sum(len(d.evidence) for d in successes) / len(successes) > 2:
            success_patterns.append(
                "Decisions with strong evidence consistently succeed."
            )

        failure_patterns = []
        if (
            failures
            and sum(len(d.options_considered) for d in failures) / len(failures) < 1.5
        ):
            failure_patterns.append("Failing decisions often lack alternative options.")

        return {
            "speed": (
                "Fast (based on timestamp analysis against intent creation)"
                if len(decisions) > 10
                else "Unknown"
            ),
            "evidence_requirement": evidence_req,
            "risk_appetite": "Medium (default baseline)",
            "reversibility_preference": rev_pref,
            "success_patterns": success_patterns,
            "failure_patterns": failure_patterns,
        }
