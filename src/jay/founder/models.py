from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jay.db import Base


class FounderProfile(Base):
    __tablename__ = "founder_profile"

    id: Mapped[str] = mapped_column(String, primary_key=True, default="default")
    risk_tolerance: Mapped[str | None] = mapped_column(Text)
    time_horizon: Mapped[str | None] = mapped_column(Text)
    decision_style: Mapped[str | None] = mapped_column(Text)
    communication_style: Mapped[str | None] = mapped_column(Text)
    leadership_style: Mapped[str | None] = mapped_column(Text)
    learning_style: Mapped[str | None] = mapped_column(Text)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BehaviorLedger(Base):
    __tablename__ = "behavior_ledger"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text)
    response: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)

    context: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PreferenceEdge(Base):
    __tablename__ = "preference_edges"

    source_id: Mapped[str] = mapped_column(String, primary_key=True)
    target_id: Mapped[str] = mapped_column(String, primary_key=True)
    relationship_type: Mapped[str] = mapped_column(Text, primary_key=True)

    weight: Mapped[float] = mapped_column(Numeric(5, 3), nullable=False, default=1.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
