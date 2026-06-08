import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from jay.events.projector import Projector
from jay.memory.models import EventLog, MemoryItem

logger = logging.getLogger(__name__)


class MemoryProjector(Projector):
    @property
    def name(self) -> str:
        return "memory"

    def handle(self, event: EventLog, session: Session) -> None:
        if event.event_type != "memory.item_recorded":
            return
            
        payload = event.payload
        item_id = event.entity_id

        # Idempotency check
        existing = session.query(MemoryItem).filter_by(id=item_id).first()
        if existing:
            return

        item = MemoryItem(
            id=item_id,
            kind=payload["kind"],
            title=payload["title"],
            body=payload["body"],
            source=payload["source"],
            importance=payload["importance"],
            confidence=payload["confidence"],
            occurred_at=payload.get("occurred_at"),
            tags=payload.get("tags", []),
            linked_entity_ids=payload.get("linked_entity_ids", []),
        )
        session.add(item)

    def reset(self, session: Session) -> None:
        """Truncate the memory_items table."""
        if session.bind.dialect.name == "postgresql":
            session.execute(text("TRUNCATE TABLE memory_items;"))
        else:
            session.execute(text("DELETE FROM memory_items;"))
        logger.info("Truncated memory_items table.")
