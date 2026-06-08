from typing import Any
from pydantic import BaseModel

class HighestLeverageAction(BaseModel):
    statement: str
    reason: str
    impact_score: float
    estimated_leverage: str
    confidence_score: float

class TopPriority(BaseModel):
    entity_id: str
    entity_title: str
    attention_score: float
    why_it_matters: str

class CriticalRisk(BaseModel):
    risk_type: str
    entity_title: str
    score: float
    reason: str
    recommended_action: str

class OpenCommitment(BaseModel):
    commitment: str
    owner: str
    days_overdue: int
    suggested_action: str

class RelationshipAlert(BaseModel):
    person: str
    score: float
    last_contact_days_ago: int
    recommendation: str

class DecisionReview(BaseModel):
    decision: str
    age_days: int
    risk: str
    recommended_review_date: str

class ProjectHealth(BaseModel):
    project_id: str
    momentum_score: float
    trust_score: float
    intent_alignment_score: float
    activity_score: float
    status: str

class CommandCenterResponse(BaseModel):
    highest_leverage_action: HighestLeverageAction | None = None
    top_priorities: list[TopPriority] = []
    critical_risks: list[CriticalRisk] = []
    open_commitments: list[OpenCommitment] = []
    relationship_alerts: list[RelationshipAlert] = []
    decision_reviews: list[DecisionReview] = []
    project_health: list[ProjectHealth] = []
    alignment_score: float = 0.0
    leverage_score: float = 0.0
