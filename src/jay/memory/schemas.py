from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class MemoryKind(StrEnum):
    project = "project"
    person = "person"
    meeting = "meeting"
    idea = "idea"
    task = "task"
    lesson = "lesson"
    commitment = "commitment"
    document = "document"
    decision = "decision"


class TrustEnvelope(BaseModel):
    confidence_score: float = Field(default=0.7, ge=0, le=1)
    risk_score: float = Field(default=0.0, ge=0, le=1)
    impact_score: float = Field(default=0.5, ge=0, le=1)
    reversibility_score: float = Field(default=0.8, ge=0, le=1)
    evidence_score: float = Field(default=0.5, ge=0, le=1)
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    aligned_intent_ids: list[str] = Field(default_factory=list)


class MemoryCreate(BaseModel):
    kind: MemoryKind
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    source: str = Field(default="manual")
    importance: int = Field(default=3, ge=1, le=5)
    confidence: float = Field(default=0.7, ge=0, le=1)
    occurred_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    linked_entity_ids: list[str] = Field(default_factory=list)
    trust: TrustEnvelope = Field(default_factory=TrustEnvelope)


class MemoryRead(BaseModel):
    id: str
    kind: MemoryKind
    title: str
    body: str
    source: str
    importance: int
    confidence: float
    occurred_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[str]
    linked_entity_ids: list[str]


class SearchResult(BaseModel):
    item: MemoryRead
    reason: str

