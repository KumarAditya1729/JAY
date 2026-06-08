from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from jay.db import Base


class TrustLedger(Base):
    __tablename__ = "trust_ledger"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    impact_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    reversibility_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    evidence_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    assumptions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    evidence: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_trust_ledger_entity_orm", "entity_type", "entity_id"),
        Index("idx_trust_ledger_created_orm", "created_at"),
    )
