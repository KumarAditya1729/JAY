from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jay.db import Base


class EventLog(Base):
    __tablename__ = "event_log"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    stream_id: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(Text)
    entity_id: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    causation_id: Mapped[UUID | None]
    correlation_id: Mapped[UUID | None]
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    trust: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("idx_event_log_stream_orm", "stream_id", "occurred_at"),
        Index("idx_event_log_entity_orm", "entity_type", "entity_id"),
    )


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False, default=0.7)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    linked_entity_ids: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)

    __table_args__ = (
        Index("idx_memory_items_kind_orm", "kind"),
        Index("idx_memory_items_occurred_orm", "occurred_at"),
    )

