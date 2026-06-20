from typing import Any, Optional
from pydantic import BaseModel


class ExpertAdvice(BaseModel):
    expert_name: str
    framework_name: str
    advice: str


class HighestLeverageAction(BaseModel):
    recommendation_id: Optional[str] = None
    statement: str
    reason: str
    impact_score: float
    estimated_leverage: str
    confidence_score: float
    expert_advice: Optional[ExpertAdvice] = None
    constraint_reason: Optional[str] = None


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


class ProjectNode(BaseModel):
    id: str
    title: str
    momentum_score: float
    open_tasks_count: int
    forecast: str = "Stable"
    velocity: float = 0.0

class BottleneckNode(BaseModel):
    task_id: str
    statement: str
    blocks_count: int
    blast_radius_impact: float

class MissionNode(BaseModel):
    id: str
    title: str
    status: str
    progress_percentage: float
    health_score: float
    active_projects: int
    momentum_forecast: str
    constraint: str | None = None


class FounderIntelligence(BaseModel):
    peak_performance_window: str
    primary_failure_cause: str
    energy_vampires: list[Any] = []
    stop_doing_list: list[Any] = []


class RelationshipIntelligenceData(BaseModel):
    relationships_at_risk: list[Any] = []
    pending_commitments: list[Any] = []
    top_strategic_contacts: list[Any] = []

class BusinessIntelligenceData(BaseModel):
    mrr: float
    runway_months: float
    monthly_burn_rate: float
    founder_roi_score: float
    hours_tracked: float

class OpportunityData(BaseModel):
    id: str
    opportunity_score: float
    title: str
    revenue_potential: str
    recommended_action: str

class ConstraintData(BaseModel):
    id: str
    type: str
    severity: str
    evidence: str
    recommended_action: str

class ResearchData(BaseModel):
    id: str
    query: str
    trigger_source: str
    status: str
    synthesis_report: str | None = None
    sources_cited: list[str]

class PreferenceData(BaseModel):
    preference_key: str
    preferred: str
    rejected: str
    weight: float

class EnergyStateData(BaseModel):
    current_time: str
    energy_level: str
    optimal_task: str

class DecisionPredictionData(BaseModel):
    situation: str
    prediction: str
    confidence: float
    reason: str

class DigitalTwinData(BaseModel):
    active_prediction: DecisionPredictionData
    preferences: list[PreferenceData] = []
    energy_state: EnergyStateData

class AgentWorkforceData(BaseModel):
    id: str
    role: str
    status: str
    active_task: str | None = None
    tasks_completed: int

class MissionPipelineStage(BaseModel):
    stage: int
    agent: str
    task: str
    status: str

class MissionAutonomyData(BaseModel):
    id: str
    mission_name: str
    status: str
    current_stage: int
    workflow_pipeline: list[MissionPipelineStage]

class ExecutiveArgumentData(BaseModel):
    executive: str
    stance: str
    argument: str

class ExecutiveDebateData(BaseModel):
    id: str
    topic: str
    status: str
    arguments: list[ExecutiveArgumentData]
    founder_decision: str | None = None

class SimulationOutcomeData(BaseModel):
    financial: str
    velocity: str
    risk: str
    summary: str

class StrategicSimulationData(BaseModel):
    id: str
    scenario: str
    best_case: SimulationOutcomeData
    expected_case: SimulationOutcomeData
    worst_case: SimulationOutcomeData

class AdvisorCritiqueData(BaseModel):
    advisor: str
    critique: str

class BoardAdvisoryData(BaseModel):
    id: str
    topic: str
    advice: list[AdvisorCritiqueData]

class EpistemologyData(BaseModel):
    id: str
    claim: str
    source: str
    evidence: list[str]
    confidence_score: float
    verification_status: str
    auditor_notes: str | None = None
    expiry_date: str | None = None

class SimulationEffectData(BaseModel):
    month: int
    financial_impact: str
    operational_impact: str

class SimulationTimelineData(BaseModel):
    id: str
    timeline_name: str
    injected_event: str
    cascading_effects: list[SimulationEffectData]
    terminal_state: str

class DigitalTwinPredictionData(BaseModel):
    id: str
    scenario: str
    predicted_decision: str
    reasoning: str
    alignment_confidence: float
    cognitive_blind_spots: list[str]

class SystemAccuracyAggregateData(BaseModel):
    engine: str
    accuracy: float
    calibration: float
    trust_score: float
    trust_tier: str
    is_drifting: bool
    evaluations_count: int

class SystemAccuracyValidationData(BaseModel):
    id: str
    engine: str
    prediction: str
    outcome: str
    accuracy_score: float
    confidence_score: float
    timestamp: str | None

class FounderVsJayLogData(BaseModel):
    id: str
    scenario: str
    jay_recommendation: str
    founder_decision: str
    outcome: str
    who_was_right: str
    timestamp: str | None

class FounderVsJayData(BaseModel):
    jay_wins: int
    founder_wins: int
    ties: int
    jay_win_rate: float
    log: list[FounderVsJayLogData]

class SystemAccuracyData(BaseModel):
    aggregate_accuracy: list[SystemAccuracyAggregateData]
    recent_validations: list[SystemAccuracyValidationData]
    founder_vs_jay: FounderVsJayData

class DeviceContextData(BaseModel):
    device_name: str
    active_app: str | None = None
    context_payload: dict | None = None
    location: str | None = None

class AutonomyGovernanceData(BaseModel):
    id: str
    domain: str
    autonomy_level: int
    trust_score: float
    success_rate: float
    failure_rate: float
    requires_approval: bool

class RealityProofData(BaseModel):
    id: str
    agent_role: str
    action_taken: str
    proof_url: str
    proof_hash: str | None = None
    verified: bool

class CommandCenterResponse(BaseModel):
    reality_proofs: list[RealityProofData] = []
    autonomy_governance: list[AutonomyGovernanceData] = []
    device_context: DeviceContextData | None = None
    agent_workforce: list[AgentWorkforceData] = []
    mission_autonomy: list[MissionAutonomyData] = []
    epistemology_audits: list[EpistemologyData] = []
    simulation_timelines: list[SimulationTimelineData] = []
    executive_council: list[ExecutiveDebateData] = []
    strategic_simulations: list[StrategicSimulationData] = []
    board_advice: list[BoardAdvisoryData] = []
    digital_twin: DigitalTwinData | None = None
    digital_twin_predictions: list[DigitalTwinPredictionData] = []
    system_accuracy: SystemAccuracyData | None = None
    research_queue: list[ResearchData] = []
    constraint_intelligence: ConstraintData | None = None
    opportunity_intelligence: OpportunityData | None = None
    business_intelligence: BusinessIntelligenceData | None = None
    relationship_intelligence: RelationshipIntelligenceData | None = None
    highest_leverage_action: HighestLeverageAction | None = None
    founder_intelligence: FounderIntelligence | None = None
    top_priorities: list[TopPriority] = []
    critical_risks: list[CriticalRisk] = []
    open_commitments: list[OpenCommitment] = []
    relationship_alerts: list[RelationshipAlert] = []
    decision_reviews: list[DecisionReview] = []
    mission_graph: list[MissionNode] = []
    strategic_bottlenecks: list[BottleneckNode] = []
    alignment_score: float = 0.0
    leverage_score: float = 0.0
