from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BehaviorCreate(BaseModel):
    action: str
    recommendation: str | None = None
    response: str | None = None
    outcome: str | None = None
    context: dict = Field(default_factory=dict)


class BehaviorResponse(BaseModel):
    id: UUID
    action: str
    recommendation: str | None
    response: str | None
    outcome: str | None
    context: dict
    occurred_at: datetime


class PreferenceEdgeResponse(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    weight: float
    updated_at: datetime


class FounderProfileUpdate(BaseModel):
    risk_tolerance: str | None = None
    time_horizon: str | None = None
    decision_style: str | None = None
    communication_style: str | None = None
    leadership_style: str | None = None
    learning_style: str | None = None


class FounderProfileResponse(BaseModel):
    id: str
    risk_tolerance: str | None
    time_horizon: str | None
    decision_style: str | None
    communication_style: str | None
    leadership_style: str | None
    learning_style: str | None

    mission: list[dict] = Field(default_factory=list)
    values: list[dict] = Field(default_factory=list)
    goals: list[dict] = Field(default_factory=list)
    non_negotiables: list[dict] = Field(default_factory=list)
