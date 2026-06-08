from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class DecisionCreate(BaseModel):
    statement: str
    decision_type: str
    maker: str
    options_considered: list[dict] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    assumptions: list[dict] = Field(default_factory=list)
    risks: list[dict] = Field(default_factory=list)
    expected_outcome: str | None = None
    success_criteria: str | None = None
    reversibility_score: float = 0.5
    intent_alignment_score: float = 0.5
    trust_envelope: str | None = None
    linked_entity_ids: list[str] = Field(default_factory=list)

class DecisionOutcome(BaseModel):
    outcome_status: str # "Success", "Partial Success", "Failure", "Unknown"
    actual_outcome: str | None = None
    lessons_learned: str | None = None

class DecisionResponse(BaseModel):
    id: UUID
    statement: str
    decision_type: str
    decision_date: datetime
    maker: str
    options_considered: list[dict]
    evidence: list[dict]
    assumptions: list[dict]
    risks: list[dict]
    expected_outcome: str | None
    success_criteria: str | None
    reversibility_score: float
    intent_alignment_score: float
    trust_envelope: str | None
    outcome_status: str
    actual_outcome: str | None
    lessons_learned: str | None
    outcome_date: datetime | None
    linked_entity_ids: list[str]
    created_at: datetime
    updated_at: datetime
