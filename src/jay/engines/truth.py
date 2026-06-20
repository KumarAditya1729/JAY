from jay.db import SessionLocal
from jay.engines.models import EpistemologyLedger

class TruthEngine:
    @staticmethod
    def get_active_audits() -> list[dict]:
        """
        Retrieves the epistemological baseline: verified, debunked, and unverified claims.
        """
        with SessionLocal() as db:
            audits = db.query(EpistemologyLedger).order_by(EpistemologyLedger.created_at.desc()).all()
            return [
                {
                    "id": str(a.id),
                    "claim": a.claim,
                    "source": a.source,
                    "evidence": a.evidence,
                    "confidence_score": a.confidence_score,
                    "verification_status": a.verification_status,
                    "auditor_notes": a.auditor_notes,
                    "expiry_date": a.expiry_date.isoformat() if a.expiry_date else None
                } for a in audits
            ]
