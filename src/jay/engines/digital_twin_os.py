from jay.db import SessionLocal
from jay.engines.models import DigitalTwinDecisionLedger

class DigitalTwinOSEngine:
    @staticmethod
    def get_active_predictions() -> list[dict]:
        """
        Retrieves the Founder's predicted decisions and cognitive blind spots.
        """
        with SessionLocal() as db:
            predictions = db.query(DigitalTwinDecisionLedger).order_by(DigitalTwinDecisionLedger.created_at.desc()).all()
            return [
                {
                    "id": str(p.id),
                    "scenario": p.scenario,
                    "predicted_decision": p.predicted_decision,
                    "reasoning": p.reasoning,
                    "alignment_confidence": p.alignment_confidence,
                    "cognitive_blind_spots": p.cognitive_blind_spots
                } for p in predictions
            ]
