from jay.db import SessionLocal
from jay.engines.models import SimulationTimelineLedger

class SimulationSandboxEngine:
    @staticmethod
    def get_active_timelines() -> list[dict]:
        """
        Retrieves the isolated alternate realities.
        """
        with SessionLocal() as db:
            timelines = db.query(SimulationTimelineLedger).order_by(SimulationTimelineLedger.created_at.desc()).all()
            return [
                {
                    "id": str(t.id),
                    "timeline_name": t.timeline_name,
                    "injected_event": t.injected_event,
                    "cascading_effects": t.cascading_effects,
                    "terminal_state": t.terminal_state
                } for t in timelines
            ]
