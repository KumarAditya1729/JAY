from sqlalchemy.orm import Session

from jay.decisions.models import DecisionLedger


class DecisionAnalytics:
    def __init__(self, session: Session):
        self.session = session

    def get_metrics(self) -> dict:
        decisions = self.session.query(DecisionLedger).all()
        total = len(decisions)

        resolved = [
            d for d in decisions if d.outcome_status in ("Success", "Partial Success", "Failure")
        ]
        total_resolved = len(resolved)

        successes = len([d for d in resolved if d.outcome_status == "Success"])
        failures = len([d for d in resolved if d.outcome_status == "Failure"])

        success_rate = (successes / total_resolved) if total_resolved > 0 else 0.0

        reversible = len([d for d in decisions if d.reversibility_score >= 0.7])
        irreversible = len([d for d in decisions if d.reversibility_score < 0.3])

        return {
            "total_decisions": total,
            "resolved_decisions": total_resolved,
            "success_rate": round(success_rate, 2),
            "highly_reversible_count": reversible,
            "highly_irreversible_count": irreversible,
            "successes": successes,
            "failures": failures,
        }
