import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID

from jay.db import Base


class ExecutionLedger(Base):
    __tablename__ = "execution_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    command = Column(Text, nullable=False)
    status = Column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING, APPROVED, REJECTED, EXECUTED, FAILED
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)

    requested_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    executed_at = Column(DateTime(timezone=True), nullable=True)


class RecommendationLedger(Base):
    __tablename__ = "recommendation_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    statement = Column(Text, nullable=False)
    impact_score = Column(Float, nullable=False)
    urgency_score = Column(Float, nullable=False)
    intent_alignment_score = Column(Float, nullable=False)
    trust_score = Column(Float, nullable=False)
    reversibility_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    llm_explanation = Column(Text, nullable=True)
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class OutcomeLedger(Base):
    __tablename__ = "outcome_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), nullable=False)
    recommendation_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # Foreign Key to RecommendationLedger
    recommendation_text = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILURE, PARTIAL
    outcome = Column(Text, nullable=True) # Success narrative or failure post-mortem
    domain = Column(String(50), nullable=True, default="Execution")
    failure_reason = Column(String(255), nullable=True, default="None")
    impact_score = Column(Float, nullable=True) # 1-10 subjective
    hours_saved = Column(Float, nullable=True) # E.g. automation saved 10 hours
    hours_invested = Column(Float, nullable=True) # How long did it take
    leverage_generated = Column(Float, nullable=True) # Derived formula
    inferred = Column(Boolean, nullable=False, default=False)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OpportunityLedger(Base):
    __tablename__ = "opportunity_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    opportunity_type = Column(String(100), nullable=False) # Customer, Partnership, Funding
    revenue_potential = Column(String(100), nullable=True) # e.g., "₹5L–₹15L annually"
    recommended_action = Column(String(255), nullable=False)
    score = Column(Float, nullable=False, default=0.0) # 0.0 to 1.0
    status = Column(String(50), nullable=False, default="DETECTED") # DETECTED, PURSUING, WON, LOST
    source_ledger = Column(String(100), nullable=True) # CommunicationLedger, ObservationLedger
    source_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

class ConstraintLedger(Base):
    __tablename__ = "constraint_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    constraint_type = Column(String(100), nullable=False) # FOUNDER, SALES, CASH, PRODUCT
    severity = Column(String(50), nullable=False) # CRITICAL, HIGH, MEDIUM
    confidence = Column(Float, nullable=False, default=1.0)
    evidence = Column(Text, nullable=False)
    recommended_action = Column(String(255), nullable=False)
    resolved = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ResearchLedger(Base):
    __tablename__ = "research_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(String(255), nullable=False)
    trigger_source = Column(String(100), nullable=False) # e.g., "CONSTRAINT: SALES"
    status = Column(String(50), nullable=False, default="PENDING") # PENDING, RESEARCHING, COMPLETE, FAILED
    synthesis_report = Column(Text, nullable=True) # The final LLM synthesized report
    sources_cited = Column(JSON, nullable=True) # List of URLs
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DigitalTwinModel(Base):
    __tablename__ = "digital_twin_model"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trait_name = Column(String(100), nullable=False) # e.g., "Speed vs Perfection", "Delegation Preference"
    current_value = Column(Float, nullable=False) # 0.0 to 1.0
    confidence = Column(Float, nullable=False)
    evidence_count = Column(Integer, default=0) # How many decisions inform this trait
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AgentLedger(Base):
    __tablename__ = "agent_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_role = Column(String(100), nullable=False) # e.g., "Engineering", "Sales", "Research"
    status = Column(String(50), nullable=False, default="IDLE") # IDLE, EXECUTING, BLOCKED
    current_task_id = Column(String(100), nullable=True) # ID of the task they are working on
    current_action = Column(String(255), nullable=True) # Human readable action
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DeviceAwarenessLedger(Base):
    __tablename__ = "device_awareness_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_name = Column(String(100), nullable=False) # e.g., "MacBook Pro", "iPhone 15"
    active_app = Column(String(100), nullable=True) # e.g., "VS Code", "Chrome"
    context_payload = Column(JSON, nullable=True) # e.g., {"file": "models.py", "url": "github.com"}
    location = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AutonomyLedger(Base):
    __tablename__ = "autonomy_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String(100), nullable=False, unique=True) # e.g., "GitHub Code Reviews"
    autonomy_level = Column(Integer, nullable=False, default=1) # 0=Observe, 1=Recommend, 2=Execute w/ Approval, 3=Execute Independently, 4=Mission Autonomy
    trust_score = Column(Float, nullable=False, default=0.5)
    success_rate = Column(Float, nullable=False, default=1.0)
    failure_rate = Column(Float, nullable=False, default=0.0)
    requires_approval = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class RealityProofLedger(Base):
    __tablename__ = "reality_proof_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), nullable=False) # Maps to ExecutionLedger (or a mock UUID for now)
    agent_role = Column(String(50), nullable=False)
    action_taken = Column(String(255), nullable=False)
    proof_url = Column(String(500), nullable=False)
    proof_hash = Column(String(255), nullable=True)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE 17: FOUNDER DIGITAL TWIN V2 ---

class FounderDecisionLedger(Base):
    __tablename__ = "founder_decision_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    situation = Column(String(255), nullable=False)
    options = Column(JSON, nullable=False)
    choice = Column(String(255), nullable=False)
    outcome = Column(String(255), nullable=True)
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class FounderPreferenceLedger(Base):
    __tablename__ = "founder_preference_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    preference_key = Column(String(100), nullable=False, unique=True) # e.g., "build_vs_meetings"
    preferred_value = Column(String(100), nullable=False) # e.g., "Build"
    rejected_value = Column(String(100), nullable=False) # e.g., "Meetings"
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class FounderBehaviorLedger(Base):
    __tablename__ = "founder_behavior_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trait = Column(String(100), nullable=False, unique=True) # e.g., "Risk Tolerance", "Speed Preference"
    score = Column(Float, nullable=False) # 0.0 to 1.0
    evidence = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class FounderEnergyLedger(Base):
    __tablename__ = "founder_energy_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time_window = Column(String(50), nullable=False) # e.g., "07:00-11:00"
    energy_level = Column(String(50), nullable=False) # e.g., "Peak", "Trough", "Recovery"
    optimal_task_type = Column(String(100), nullable=False) # e.g., "Deep Work", "Meetings", "Rest"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE 18: MISSION AUTONOMY ---

class MissionAutonomyLedger(Base):
    __tablename__ = "mission_autonomy_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_name = Column(String(255), nullable=False) # e.g., "Acquire 10 CA Firms"
    status = Column(String(50), nullable=False, default="IN_PROGRESS") # PLANNING, IN_PROGRESS, COMPLETED, BLOCKED
    current_stage = Column(Integer, nullable=False, default=1)
    
    # Workflow Pipeline: List of dicts representing the steps and the assigned agents
    # e.g., [{"stage": 1, "agent": "Research Agent", "status": "COMPLETED"}, {"stage": 2, "agent": "Growth Agent", "status": "IN_PROGRESS"}]
    workflow_pipeline = Column(JSON, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE 19: DIGITAL EXECUTIVE TEAM ---

class ExecutiveDebateLedger(Base):
    __tablename__ = "executive_debate_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(255), nullable=False) # e.g., "Launch Arkashri"
    status = Column(String(50), nullable=False, default="DEBATING") # DEBATING, RESOLVED
    
    # JSON array of arguments: 
    # [{"executive": "CTO", "stance": "DELAY", "argument": "Need 3 more weeks. Architecture unstable."}, ...]
    arguments = Column(JSON, nullable=False) 
    
    founder_decision = Column(String(255), nullable=True) # Final resolution
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- JAY OMEGA (PHASES 21 & 22) ---

class StrategicSimulationLedger(Base):
    __tablename__ = "strategic_simulation_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario = Column(String(255), nullable=False) # e.g., "Pivot to Enterprise B2B"
    # JSON arrays containing predictions for Best, Expected, Worst cases
    best_case = Column(JSON, nullable=False) 
    expected_case = Column(JSON, nullable=False)
    worst_case = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class BoardAdvisoryLedger(Base):
    __tablename__ = "board_advisory_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(255), nullable=False)
    # JSON array: [{"advisor": "Steve Jobs", "critique": "The product lacks focus..."}, ...]
    advice = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE 23: TRUTH OS ---

class EpistemologyLedger(Base):
    __tablename__ = "epistemology_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim = Column(String(500), nullable=False) # e.g., "Competitor launched audit AI"
    source = Column(String(255), nullable=False) # e.g., "Website / PR Newswire"
    
    # JSON array: ["URL", "Screenshot hash"]
    evidence = Column(JSON, nullable=False) 
    
    confidence_score = Column(Float, nullable=False, default=0.0) # 0.0 to 1.0
    verification_status = Column(String(50), nullable=False, default="UNVERIFIED") # UNVERIFIED, VERIFIED, DEBUNKED
    
    # The Chief Auditor's reasoning for the verdict
    auditor_notes = Column(Text, nullable=True) 
    
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE 24: SIMULATION OS ---

class SimulationTimelineLedger(Base):
    __tablename__ = "simulation_timeline_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timeline_name = Column(String(255), nullable=False) # e.g., "Timeline Alpha: Apple Launch"
    injected_event = Column(String(500), nullable=False) # The hypothetical crisis/event
    
    # JSON array mapping the cascading effects over time
    # [{"month": 1, "financial_impact": "-15% MRR", "operational_impact": "Support overwhelmed"}, ...]
    cascading_effects = Column(JSON, nullable=False) 
    
    # The final outcome of this timeline
    terminal_state = Column(String(50), nullable=False) # SURVIVED, BANKRUPT, ACQUIRED
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE 25: DIGITAL TWIN OS ---

class DigitalTwinDecisionLedger(Base):
    __tablename__ = "digital_twin_decision_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario = Column(String(500), nullable=False) # e.g., "Pivot to Enterprise B2B"
    
    predicted_decision = Column(String(50), nullable=False) # e.g., "APPROVE", "REJECT", "DEFER"
    reasoning = Column(Text, nullable=False)
    
    # 0.0 to 1.0 - how confident the twin is based on past data
    alignment_confidence = Column(Float, nullable=False) 
    
    # JSON array mapping founder biases that the twin is flagging
    # e.g. ["Optimism bias on engineering delivery times", "Ignores churn when ARR is up"]
    cognitive_blind_spots = Column(JSON, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE X: EMPIRICAL VALIDATION PROGRAM ---

class SystemAccuracyLedger(Base):
    __tablename__ = "system_accuracy_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engine = Column(String(100), nullable=False) # e.g., "Digital Twin", "Opportunity OS", "Research OS"
    prediction = Column(String(500), nullable=False) # e.g., "Founder will reject enterprise pivot"
    outcome = Column(String(500), nullable=False) # e.g., "Founder accepted"
    accuracy_score = Column(Float, nullable=False) # 0.0 to 1.0 (e.g. 0.0 = completely wrong, 1.0 = perfect)
    confidence_score = Column(Float, nullable=False, default=1.0) # E.g. JAY was 90% confident (0.9)
    
    # Optional foreign key linking back to the specific Ledger ID
    source_ledger_id = Column(String(100), nullable=True) 
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# --- PHASE Y: TRUST MARKETS & THE ULTIMATE METRIC ---

class FounderVersusJAYLedger(Base):
    __tablename__ = "founder_versus_jay_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario = Column(String(500), nullable=False)
    jay_recommendation = Column(String(500), nullable=False)
    founder_decision = Column(String(500), nullable=False)
    outcome = Column(String(500), nullable=False)
    
    # "JAY", "FOUNDER", "TIE", or "PENDING"
    who_was_right = Column(String(50), nullable=False, default="PENDING") 
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FounderActivityLedger(Base):
    __tablename__ = "founder_activity_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_recorded = Column(DateTime(timezone=True), nullable=False)
    commits_count = Column(Integer, nullable=False, default=0)
    issues_closed = Column(Integer, nullable=False, default=0)
    prs_closed = Column(Integer, nullable=False, default=0)
    repositories_active = Column(Integer, nullable=False, default=0)
    activity_score = Column(Float, nullable=False, default=0.0)
    progress_score = Column(Float, nullable=False, default=0.0)
    impact_score = Column(Float, nullable=False, default=0.0)
    velocity_trend = Column(String(50), nullable=False)  # Accelerating, Stable, Slowing
    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ExpertFrameworkLedger(Base):
    __tablename__ = "expert_framework_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expert_name = Column(String(100), nullable=False)
    framework_name = Column(String(200), nullable=False)
    core_principle = Column(Text, nullable=False)
    application_criteria = Column(Text, nullable=False)
    added_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class MissionLedger(Base):
    __tablename__ = "mission_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    health_score = Column(Float, nullable=False, default=100.0)
    status = Column(String(50), nullable=False, default="Active")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ProjectLedger(Base):
    __tablename__ = "project_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(200), nullable=False)
    momentum_score = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="Active")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TaskLedger(Base):
    __tablename__ = "task_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    statement = Column(Text, nullable=False)
    urgency = Column(Float, nullable=False, default=5.0)
    impact = Column(Float, nullable=False, default=5.0)
    status = Column(String(50), nullable=False, default="Pending")
    assigned_to = Column(String(100), nullable=False, default="Founder")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class MilestoneLedger(Base):
    __tablename__ = "milestone_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(200), nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="Pending")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class DependencyLedger(Base):
    __tablename__ = "dependency_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), nullable=False)
    blocked_by_task_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class WorkSessionLedger(Base):
    __tablename__ = "work_session_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String(50), nullable=False, default="Active")  # Active, Completed
    start_time = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    end_time = Column(DateTime(timezone=True), nullable=True)
    primary_project_id = Column(UUID(as_uuid=True), nullable=True)
    session_summary = Column(Text, nullable=True)
    
    # Phase 11.0: Founder MRI
    energy_drain = Column(Float, nullable=False, default=0.0) # Scale 0.0 to 10.0 (10 = exhausted)
    focus_score = Column(Float, nullable=False, default=5.0) # Scale 0.0 to 10.0 (10 = deep flow state)
    session_type = Column(String(50), nullable=False, default="Execution") # Coding, Meetings, Writing, Planning, Debugging


class ObservationLedger(Base):
    __tablename__ = "observation_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    source = Column(String(50), nullable=False)  # Terminal, GitHub, Voice
    observation_type = Column(String(50), nullable=False, default="SYSTEM_EVENT")
    payload = Column(JSON, nullable=False)
    
    # Phase 9.5 Quality Scores
    importance_score = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=0.0)
    source_reliability = Column(Float, nullable=False, default=0.0)
    business_relevance = Column(Float, nullable=False, default=0.0)
    
    status = Column(
        String(50), nullable=False, default="Unprocessed"
    )  # Unprocessed, Inferred, Ignored
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

class ExecutionWorkflowLedger(Base):
    __tablename__ = "execution_workflows"

    id = Column(String, primary_key=True, index=True) # UUID string
    agent_id = Column(String, index=True)
    state = Column(String, default="CREATED") # PLANNING, EXECUTING, WAITING_APPROVAL, COMPLETED, FAILED
    context = Column(String)
    last_result = Column(String)
    tool_calls = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class RelationshipLedger(Base):
    __tablename__ = "relationship_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    role = Column(String(100), nullable=False) # Customer, Investor, Partner, Employee
    trust_level = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0
    revenue_generated = Column(Float, nullable=False, default=0.0)
    strategic_value = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0
    health_score = Column(Float, nullable=False, default=1.0) # 0.0 to 1.0
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class CommunicationLedger(Base):
    __tablename__ = "communication_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    relationship_id = Column(UUID(as_uuid=True), nullable=False) # Foreign Key to RelationshipLedger
    channel = Column(String(100), nullable=False) # Slack, WhatsApp, Email, Meeting
    summary = Column(Text, nullable=False)
    sentiment = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0
    importance = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0
    mission_relevance = Column(Float, nullable=False, default=0.5) # 0.0 to 1.0
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class CommitmentLedger(Base):
    __tablename__ = "commitment_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    communication_id = Column(UUID(as_uuid=True), nullable=False) # Foreign Key to CommunicationLedger
    relationship_id = Column(UUID(as_uuid=True), nullable=False) # Foreign Key to RelationshipLedger
    promise_text = Column(Text, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="Pending") # Pending, Completed, Overdue, Cancelled
    owner = Column(String(100), nullable=False, default="Founder") # Who owes the commitment? Founder or Contact
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class FinancialLedger(Base):
    __tablename__ = "financial_ledger"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(String(50), nullable=False) # Revenue, Expense, Funding
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False) # MRR, One-Time, Server Costs, Salaries, etc.
    description = Column(Text, nullable=True)
    date_recorded = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

