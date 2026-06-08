from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LeverageLedgerCreate(BaseModel):
    entity_type: str
    entity_id: str
    hours_saved: float = 0.0
    knowledge_preserved_score: float = 0.0
    decisions_improved_score: float = 0.0
    risks_avoided_score: float = 0.0
    opportunities_captured_score: float = 0.0
    notes: str | None = None


class LeverageLedgerRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: str
    hours_saved: float
    knowledge_preserved_score: float
    decisions_improved_score: float
    risks_avoided_score: float
    opportunities_captured_score: float
    notes: str | None
    created_at: datetime


class LeverageRatio(BaseModel):
    total_hours_saved: float
    avg_knowledge_preserved: float
    avg_decisions_improved: float
    avg_risks_avoided: float
    avg_opportunities_captured: float
    ratio: float
