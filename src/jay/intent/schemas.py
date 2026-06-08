from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class IntentNodeType(StrEnum):
    mission = "mission"
    value = "value"
    goal = "goal"
    non_negotiable = "non_negotiable"
    anti_goal = "anti_goal"


class IntentNodeCreate(BaseModel):
    node_type: IntentNodeType
    title: str = Field(min_length=1)
    description: str | None = None
    status: str = Field(default="active")


class IntentNodeRead(BaseModel):
    id: str
    node_type: IntentNodeType
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class IntentEdgeCreate(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str = Field(default="supports")


class IntentEdgeRead(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    created_at: datetime
