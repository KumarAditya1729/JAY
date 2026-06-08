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
