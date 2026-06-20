from jay.db import SessionLocal
from jay.engines.models import AgentLedger

class AgentWorkforceEngine:
    @staticmethod
    def get_active_agents() -> list[dict]:
        """
        Retrieves the active workforce.
        In a production system, this would poll the orchestrator for Swarm state.
        """
        with SessionLocal() as db:
            agents = db.query(AgentLedger).all()
            
            results = []
            for a in agents:
                results.append({
                    "id": str(a.id),
                    "role": a.agent_role,
                    "status": a.status,
                    "current_task_id": a.current_task_id,
                    "current_action": a.current_action,
                    "updated_at": a.updated_at.isoformat() if a.updated_at else None
                })
            return results
