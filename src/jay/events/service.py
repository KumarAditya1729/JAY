from typing import Any, Dict

from sqlalchemy.orm import Session

from jay.memory.models import EventLog


class EventService:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        stream_id: str,
        event_type: str,
        actor_id: str,
        entity_type: str,
        entity_id: str,
        payload: Dict[str, Any],
        trust: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> EventLog:
        event = EventLog(
            stream_id=stream_id,
            event_type=event_type,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            trust=trust or {},
            metadata=metadata or {},
        )
        self.session.add(event)
        # Flush to get generated id and occurred_at if needed
        self.session.flush()
        return event
