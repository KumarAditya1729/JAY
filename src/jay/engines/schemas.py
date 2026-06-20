from pydantic import BaseModel


class Risk(BaseModel):
    risk_type: str
    entity_id: str
    entity_title: str
    score: float
    reason: str
    evidence: str
    recommended_action: str


class Opportunity(BaseModel):
    opportunity_type: str
    entity_id: str
    entity_title: str
    impact_score: float
    confidence_score: float
    evidence: str
    recommended_action: str


class Relationship(BaseModel):
    entity_id: str
    name: str
    health_score: float
    last_contacted_days_ago: int | None
    status: str


class Priority(BaseModel):
    entity_id: str
    entity_title: str
    attention_score: float
    why_it_matters: str
    evidence: str
    risk_of_delay: str
    expected_leverage_gain: str

from pydantic import Field
from typing import Optional, Dict, Any, Literal

class AgentAction(BaseModel):
    thought: str = Field(..., description="The internal reasoning and step-by-step logic before acting.")
    action: Literal["tool", "done", "wait_approval", "error"] = Field(..., description="The type of action to take. Use 'tool' to execute a function, or 'wait_approval' if blocked.")
    tool_name: Optional[str] = Field(None, description="The name of the tool to execute.")
    tool_arguments: Optional[Dict[str, Any]] = Field(None, description="The JSON arguments for the tool.")
    result: Optional[str] = Field(None, description="The final outcome or answer, if action is done.")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0 that this action will succeed.")
