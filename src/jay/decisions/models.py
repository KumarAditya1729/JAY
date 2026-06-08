from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jay.db import Base

class DecisionLedger(Base):
    __tablename__ = "decision_ledger"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    decision_type: Mapped[str] = mapped_column(Text, nullable=False)
    decision_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    maker: Mapped[str] = mapped_column(Text, nullable=False)
    
    options_considered: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    evidence: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    assumptions: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    risks: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    
    expected_outcome: Mapped[str | None] = mapped_column(Text)
    success_criteria: Mapped[str | None] = mapped_column(Text)
    
    reversibility_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False, default=0.5)
    intent_alignment_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False, default=0.5)
    trust_envelope: Mapped[str | None] = mapped_column(Text)
    
    outcome_status: Mapped[str] = mapped_column(Text, nullable=False, default="Pending")
    actual_outcome: Mapped[str | None] = mapped_column(Text)
    lessons_learned: Mapped[str | None] = mapped_column(Text)
    outcome_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    linked_entity_ids: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_decision_ledger_maker_orm", "maker"),
        Index("idx_decision_ledger_date_orm", "decision_date"),
        Index("idx_decision_ledger_outcome_orm", "outcome_status"),
    )
