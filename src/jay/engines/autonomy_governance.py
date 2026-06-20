from jay.db import SessionLocal
from jay.engines.models import AutonomyLedger

class AutonomyGovernanceEngine:
    @staticmethod
    def get_governance_state() -> list[dict]:
        """
        Retrieves the Autonomy Governance matrix.
        """
        with SessionLocal() as db:
            domains = db.query(AutonomyLedger).order_by(AutonomyLedger.domain).all()
            
            results = []
            for d in domains:
                results.append({
                    "id": str(d.id),
                    "domain": d.domain,
                    "autonomy_level": d.autonomy_level,
                    "trust_score": d.trust_score,
                    "success_rate": d.success_rate,
                    "failure_rate": d.failure_rate,
                    "requires_approval": d.requires_approval
                })
            return results

    @staticmethod
    def check_permission(domain: str, requested_level: int) -> bool:
        """
        Trust Gate: Verifies if a given domain allows execution at the requested level.
        """
        with SessionLocal() as db:
            record = db.query(AutonomyLedger).filter(AutonomyLedger.domain == domain).first()
            if not record:
                return False # Default Deny
            return requested_level <= record.autonomy_level
