from jay.db import SessionLocal
from jay.engines.models import DeviceAwarenessLedger

class DeviceAwarenessEngine:
    @staticmethod
    def get_current_context() -> dict | None:
        """
        Retrieves the active real-time context of the founder.
        In a production system, this reads from an active event stream.
        """
        with SessionLocal() as db:
            active = db.query(DeviceAwarenessLedger).filter(
                DeviceAwarenessLedger.is_active == True
            ).order_by(DeviceAwarenessLedger.timestamp.desc()).first()
            
            if active:
                return {
                    "id": str(active.id),
                    "device_name": active.device_name,
                    "active_app": active.active_app,
                    "context_payload": active.context_payload or {},
                    "location": active.location,
                    "timestamp": active.timestamp.isoformat() if active.timestamp else None
                }
            return None
