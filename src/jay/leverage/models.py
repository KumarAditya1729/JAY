from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from jay.db import Base


class LeverageLedger(Base):
    __tablename__ = "leverage_ledger"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    hours_saved: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=0.0
    )
    knowledge_preserved_score: Mapped[float] = mapped_column(
        Numeric(4, 3), nullable=False, default=0.0
    )
    decisions_improved_score: Mapped[float] = mapped_column(
        Numeric(4, 3), nullable=False, default=0.0
    )
    risks_avoided_score: Mapped[float] = mapped_column(
        Numeric(4, 3), nullable=False, default=0.0
    )
    opportunities_captured_score: Mapped[float] = mapped_column(
        Numeric(4, 3), nullable=False, default=0.0
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_leverage_ledger_entity_orm", "entity_type", "entity_id"),
    )
