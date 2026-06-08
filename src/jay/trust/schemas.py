from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TrustLedgerRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: str
    confidence_score: float
    risk_score: float
    impact_score: float
    reversibility_score: float
    evidence_score: float
    assumptions: list[str]
    evidence: list[str]
    created_at: datetime


class TrustDashboardStats(BaseModel):
    total_entries: int
    average_confidence: float
    average_risk: float
    average_impact: float
    average_reversibility: float
    average_evidence: float
