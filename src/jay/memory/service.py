from uuid import uuid4

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from jay.config import get_settings
from jay.memory.models import EventLog, MemoryItem
from jay.memory.schemas import MemoryCreate


class MemoryService:
    def __init__(self, session: Session):
        self.session = session
        self.settings = get_settings()

    def record(self, memory: MemoryCreate) -> MemoryItem:
        if memory.kind in ("decision", "idea", "project"):
            if not memory.trust.aligned_intent_ids:
                raise ValueError(
                    f"Every {memory.kind} must reference Founder Intent "
                    "(aligned_intent_ids cannot be empty)."
                )

        item_id = f"{memory.kind.value}_{uuid4().hex}"
        event = EventLog(
            stream_id=f"memory:{item_id}",
            event_type="memory.item_recorded",
            actor_id=self.settings.founder_id,
            entity_type="memory_item",
            entity_id=item_id,
            payload=memory.model_dump(mode="json"),
            trust=memory.trust.model_dump(mode="json"),
            event_metadata={"projection": "memory_items"},
        )
        self.session.add(event)

        from jay.memory.projector import MemoryProjector

        MemoryProjector().handle(event, self.session)

        from jay.trust.projector import TrustProjector

        TrustProjector().handle(event, self.session)

        self.session.commit()

        return self.session.query(MemoryItem).filter_by(id=item_id).one()

    def list_timeline(self, limit: int = 50) -> list[MemoryItem]:
        statement = select(MemoryItem).order_by(
            desc(MemoryItem.occurred_at).nullslast(), desc(MemoryItem.created_at)
        )
        return list(self.session.scalars(statement.limit(limit)))

    def search(self, query: str, limit: int = 10) -> list[MemoryItem]:
        if not query.strip():
            return self.list_timeline(limit=limit)

        pattern = f"%{query.strip()}%"
        statement = (
            select(MemoryItem)
            .where(or_(MemoryItem.title.ilike(pattern), MemoryItem.body.ilike(pattern)))
            .order_by(
                desc(MemoryItem.importance),
                desc(func.coalesce(MemoryItem.occurred_at, MemoryItem.created_at)),
            )
            .limit(limit)
        )
        return list(self.session.scalars(statement))
