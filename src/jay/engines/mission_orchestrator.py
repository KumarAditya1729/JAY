from jay.db import SessionLocal
from jay.engines.models import MissionAutonomyLedger

class MissionOrchestratorEngine:
    @staticmethod
    def get_active_missions() -> list[dict]:
        """
        Retrieves active multi-agent mission workflows.
        """
        with SessionLocal() as db:
            missions = db.query(MissionAutonomyLedger).order_by(MissionAutonomyLedger.created_at.desc()).all()
            return [
                {
                    "id": str(m.id),
                    "mission_name": m.mission_name,
                    "status": m.status,
                    "current_stage": m.current_stage,
                    "workflow_pipeline": m.workflow_pipeline
                } for m in missions
            ]
