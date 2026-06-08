from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from jay.db import Base


class IntentNode(Base):
    __tablename__ = "intent_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    node_type: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("idx_intent_nodes_type_orm", "node_type"),)


class IntentEdge(Base):
    __tablename__ = "intent_edges"

    source_id: Mapped[str] = mapped_column(String, ForeignKey("intent_nodes.id", ondelete="CASCADE"), primary_key=True)
    target_id: Mapped[str] = mapped_column(String, ForeignKey("intent_nodes.id", ondelete="CASCADE"), primary_key=True)
    relationship_type: Mapped[str] = mapped_column(Text, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
