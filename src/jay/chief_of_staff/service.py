from sqlalchemy.orm import Session
from datetime import datetime, timezone

from jay.engines.risk import RiskEngine
from jay.decisions.models import DecisionLedger

from .schemas import CommandCenterResponse, CriticalRisk, DecisionReview, FounderIntelligence
from .commitment_monitor import CommitmentMonitor
from .relationship_monitor import RelationshipMonitor
from .prioritizer import Prioritizer
from jay.engines.founder_mri import FounderMRIEngine
from .recommendation_engine import RecommendationEngine
from jay.engines.communication.intelligence import RelationshipIntelligenceEngine
from jay.engines.communication.followup import FollowUpEngine
from jay.engines.mission.intelligence import MissionIntelligenceEngine
from jay.engines.business.intelligence import BusinessIntelligenceEngine
from jay.engines.opportunity_os import OpportunityOSEngine
from jay.engines.constraints.intelligence import ConstraintIntelligenceEngine
from jay.engines.research_os import ResearchOSEngine
from jay.engines.digital_twin import DigitalTwinEngine
from jay.engines.agent_workforce import AgentWorkforceEngine
from jay.engines.device_awareness import DeviceAwarenessEngine
from jay.engines.autonomy_governance import AutonomyGovernanceEngine
from jay.engines.mission_orchestrator import MissionOrchestratorEngine
from jay.engines.executive_council import ExecutiveCouncilEngine
from jay.engines.omega import OmegaEngine
from jay.engines.truth import TruthEngine
from jay.engines.simulation import SimulationSandboxEngine
from jay.engines.digital_twin_os import DigitalTwinOSEngine
from jay.engines.accuracy import SystemAccuracyEngine
from jay.engines.models import RealityProofLedger
from jay.db import SessionLocal
from .schemas import RelationshipIntelligenceData, ProjectNode, MissionNode, BottleneckNode, BusinessIntelligenceData, OpportunityData, ConstraintData, ResearchData, DigitalTwinData, AgentWorkforceData, DeviceContextData, AutonomyGovernanceData, RealityProofData, MissionAutonomyData, ExecutiveDebateData, StrategicSimulationData, BoardAdvisoryData, EpistemologyData, SimulationTimelineData, DigitalTwinPredictionData, SystemAccuracyData


class ChiefOfStaffService:
    def __init__(self, session: Session):
        self.session = session
        self.commitments = CommitmentMonitor(session)
        self.relationships = RelationshipMonitor(session)
        self.prioritizer = Prioritizer(session)
        self.recommendations = RecommendationEngine(session)
        self.risks = RiskEngine(session)

    async def generate_command_center(self) -> CommandCenterResponse:
        # Phase 11.2: Constraint OS
        constraint_data_raw = ConstraintIntelligenceEngine.detect_global_constraint()
        constraint_intel = None
        if constraint_data_raw:
            constraint_intel = ConstraintData(**constraint_data_raw)

        # Phase 10.2: Mission Health & Project Graph
        mission_intel = MissionIntelligenceEngine.analyze_missions()
        mission_graph = []
        all_bottlenecks = []
        
        for md in mission_intel:
            projects_data = []
            for pd in md["projects"]:
                projects_data.append(ProjectNode(
                    id=str(pd["project"].id),
                    title=pd["project"].title,
                    momentum_score=pd["project"].momentum_score,
                    open_tasks_count=0, # Simplified for now
                    forecast=pd["forecast"],
                    velocity=pd["velocity"]
                ))
            
            mission_constraint = None
            if len(md["bottlenecks"]) > 0:
                mission_constraint = "Task Dependency Block"

            mission_graph.append(MissionNode(
                id=str(md["mission"].id),
                title=md["mission"].title,
                status=md["mission"].status,
                progress_percentage=0.0,
                health_score=md["mission"].health_score,
                active_projects=len(md["projects"]),
                momentum_forecast="Stable" if len(md["projects"]) == 0 else md["projects"][0]["forecast"],
                constraint=mission_constraint,
                projects=projects_data
            ))
            
            for b in md["bottlenecks"]:
                all_bottlenecks.append(BottleneckNode(
                    task_id=str(b["task"].id),
                    statement=b["task"].statement,
                    blocks_count=b["blocks_count"],
                    blast_radius_impact=b["blast_radius_impact"]
                ))
                
        # Sort bottlenecks by impact
        all_bottlenecks.sort(key=lambda x: x.blast_radius_impact, reverse=True)

        # Synthesize Highest Leverage Action (HLA)
        if constraint_intel:
            hla = HighestLeverageAction(
                statement=constraint_intel.recommended_action,
                reason=f"Current system constraint is {constraint_intel.type.capitalize()}.",
                impact_score=10.0,
                estimated_leverage="100x",
                confidence_score=0.95,
                constraint_reason=f"Removing this bottleneck increases projected mission velocity significantly."
            )
        else:
            hla = await self.recommendations.generate_highest_leverage_action()

        # Priorities
        top_priorities = self.prioritizer.analyze()

        # Risks
        critical_risks = []
        for r in self.risks.analyze():
            critical_risks.append(
                CriticalRisk(
                    risk_type=r.risk_type,
                    entity_title=r.entity_title,
                    score=round(r.score, 2),
                    reason=r.reason,
                    recommended_action=r.recommended_action,
                )
            )

        # Commitments
        open_commitments = self.commitments.analyze()

        # Relationships
        relationship_alerts = self.relationships.analyze()

        # Decisions to Review
        decision_reviews = []
        now = datetime.now(timezone.utc)
        decisions = (
            self.session.query(DecisionLedger)
            .filter(DecisionLedger.outcome_status == "Pending")
            .all()
        )
        for d in decisions:
            age = 0
            if d.decision_date:
                dd = (
                    d.decision_date.replace(tzinfo=timezone.utc)
                    if d.decision_date.tzinfo is None
                    else d.decision_date
                )
                age = (now - dd).days

            if age > 7 or float(d.reversibility_score) < 0.3:
                decision_reviews.append(
                    DecisionReview(
                        decision=d.statement,
                        age_days=age,
                        risk="High" if float(d.reversibility_score) < 0.3 else "Medium",
                        recommended_review_date="Today" if age > 14 else "This Week",
                    )
                )

        all_bottlenecks.sort(key=lambda x: x.blast_radius_impact, reverse=True)

        # Phase 10.3: Business Intelligence
        biz_data = BusinessIntelligenceEngine.analyze_business_reality()
        business_intel = BusinessIntelligenceData(
            mrr=biz_data["mrr"],
            runway_months=biz_data["runway_months"],
            monthly_burn_rate=biz_data["monthly_burn_rate"],
            founder_roi_score=biz_data["founder_roi_score"],
            hours_tracked=biz_data["hours_tracked"]
        )

        # Phase 11.1: Opportunity OS
        opp_data_raw = OpportunityOSEngine.analyze_opportunities()
        opportunity_intel = None
        if opp_data_raw:
            opportunity_intel = OpportunityData(**opp_data_raw)

        # Phase 11.2: Constraint OS
        constraint_data_raw = ConstraintIntelligenceEngine.detect_global_constraint()
        constraint_intel = None
        if constraint_data_raw:
            constraint_intel = ConstraintData(**constraint_data_raw)

        # Phase 12.0: Research OS
        research_raw = ResearchOSEngine.get_research_queue()
        research_queue = [ResearchData(**r) for r in research_raw]

        # Phase 17: Founder Digital Twin V2
        prediction = DigitalTwinEngine.predict_decision("Incoming email: Series A term sheet from Sequoia for $10M at $50M val.")
        preferences = DigitalTwinEngine.get_preferences()
        energy = DigitalTwinEngine.get_energy_state()
        
        digital_twin = DigitalTwinData(
            active_prediction=prediction,
            preferences=preferences,
            energy_state=energy
        )

        # Phase 14: Agent Workforce
        workforce_raw = AgentWorkforceEngine.get_active_agents()
        agent_workforce = [AgentWorkforceData(**a) for a in workforce_raw]

        # Phase 15: Device Awareness
        device_raw = DeviceAwarenessEngine.get_current_context()
        device_context = None
        if device_raw:
            device_context = DeviceContextData(**device_raw)

        # Phase 23: Truth OS
        truth_raw = TruthEngine.get_active_audits()
        epistemology_audits = [EpistemologyData(**t) for t in truth_raw]
        
        # Phase 24: Simulation OS
        simulation_raw = SimulationSandboxEngine.get_active_timelines()
        simulation_timelines = [SimulationTimelineData(**s) for s in simulation_raw]

        # JAY OMEGA (Phases 21 & 22)
        simulations_raw = await OmegaEngine.get_strategic_simulations()
        strategic_simulations = [StrategicSimulationData(**s) for s in simulations_raw]
        board_raw = await OmegaEngine.get_board_advice()
        board_advice = [BoardAdvisoryData(**b) for b in board_raw]

        # Phase 25: Digital Twin OS
        twin_raw = DigitalTwinOSEngine.get_active_predictions()
        digital_twin_predictions = [DigitalTwinPredictionData(**t) for t in twin_raw]
        
        # Phase X: Empirical Validation Program
        accuracy_raw = SystemAccuracyEngine.get_system_accuracy()
        system_accuracy = SystemAccuracyData(**accuracy_raw)

        # Phase 19: Digital Executive Team
        executive_debates_raw = await ExecutiveCouncilEngine.get_active_debates()
        executive_council = [ExecutiveDebateData(**d) for d in executive_debates_raw]

        # Phase 18: Mission Autonomy
        mission_autonomy_raw = MissionOrchestratorEngine.get_active_missions()
        mission_autonomy = [MissionAutonomyData(**m) for m in mission_autonomy_raw]

        # Phase 15.5: Autonomy Governance
        governance_raw = AutonomyGovernanceEngine.get_governance_state()
        autonomy_governance = [AutonomyGovernanceData(**g) for g in governance_raw]

        # Phase 16: Reality Proofs
        reality_proofs = []
        with SessionLocal() as db:
            proofs_raw = db.query(RealityProofLedger).order_by(RealityProofLedger.created_at.desc()).limit(10).all()
            for p in proofs_raw:
                reality_proofs.append(RealityProofData(
                    id=str(p.id),
                    agent_role=p.agent_role,
                    action_taken=p.action_taken,
                    proof_url=p.proof_url,
                    proof_hash=p.proof_hash,
                    verified=p.verified
                ))

        # Global Scores
        alignment_score = 98.5
        leverage_score = 0.0
        if mission_graph:
            leverage_score = sum(
                [m.get("health_score", 0) for m in mission_graph]
            ) / len(mission_graph)

        # Phase 11.0: Founder MRI
        mri_data = FounderMRIEngine.analyze_founder()
        founder_intelligence = FounderIntelligence(
            peak_performance_window=mri_data["peak_performance_window"],
            primary_failure_cause=mri_data["primary_failure_cause"],
            energy_vampires=mri_data["energy_vampires"],
            stop_doing_list=mri_data["stop_doing_list"]
        )

        # Phase 10.1: Relationship Intelligence
        relationship_intel = RelationshipIntelligenceData()
        all_rels = RelationshipIntelligenceEngine.analyze_all()
        
        # Populate strategic contacts
        relationship_intel.top_strategic_contacts = [
            {"name": r["relationship"].name, "role": r["relationship"].role, "leverage": r["leverage_score"]}
            for r in all_rels[:5]
        ]
        
        # Populate at risk
        relationship_intel.relationships_at_risk = [
            {"name": r["relationship"].name, "reason": "No recent contact", "strategic_value": r["relationship"].strategic_value}
            for r in all_rels if r["is_neglected"]
        ]
        
        # Populate pending commitments via FollowUpEngine insights
        relationship_intel.pending_commitments = [{"insight": i} for i in FollowUpEngine.analyze()]

        return CommandCenterResponse(
            reality_proofs=reality_proofs,
            autonomy_governance=autonomy_governance,
            device_context=device_context,
            agent_workforce=agent_workforce,
            mission_autonomy=mission_autonomy,
            epistemology_audits=epistemology_audits,
            simulation_timelines=simulation_timelines,
            executive_council=executive_council,
            strategic_simulations=strategic_simulations,
            board_advice=board_advice,
            digital_twin=digital_twin,
            digital_twin_predictions=digital_twin_predictions,
            system_accuracy=system_accuracy,
            research_queue=research_queue,
            constraint_intelligence=constraint_intel,
            opportunity_intelligence=opportunity_intel,
            business_intelligence=business_intel,
            relationship_intelligence=relationship_intel,
            highest_leverage_action=hla,
            founder_intelligence=founder_intelligence,
            top_priorities=top_priorities,
            critical_risks=critical_risks,
            open_commitments=open_commitments,
            relationship_alerts=relationship_alerts,
            decision_reviews=decision_reviews,
            mission_graph=mission_graph,
            strategic_bottlenecks=all_bottlenecks,
            alignment_score=round(alignment_score, 1),
            leverage_score=round(leverage_score, 1),
        )
