from sqlalchemy.orm import Session

from jay.engines.opportunity import OpportunityEngine
from jay.engines.communication.intelligence import RelationshipIntelligenceEngine
from jay.engines.mission.intelligence import MissionIntelligenceEngine
from jay.engines.business.intelligence import BusinessIntelligenceEngine
from jay.engines.risk import RiskEngine
from jay.engines.schemas import Priority
from jay.leverage.service import LeverageService


class AttentionEngine:
    def __init__(self, session: Session):
        self.session = session
        self.risk_engine = RiskEngine(session)
        self.opportunity_engine = OpportunityEngine(session)
        # RelationshipIntelligenceEngine is now stateless and queries DB directly
        self.leverage_service = LeverageService(session)

    def analyze(self) -> list[Priority]:
        priorities = []

        risks = self.risk_engine.analyze()
        opportunities = self.opportunity_engine.analyze()
        
        # Phase 10.1: Relationship Intelligence
        relationship_data = RelationshipIntelligenceEngine.analyze_all()
        
        # Phase 10.2: Mission Intelligence
        mission_data = MissionIntelligenceEngine.analyze_missions()
        
        # Phase 10.3: Business Intelligence
        business_data = BusinessIntelligenceEngine.analyze_business_reality()

        # Score risks (high score is bad, so it gets high attention)
        for risk in risks:
            if risk.score > 0.6:
                priorities.append(
                    Priority(
                        entity_id=risk.entity_id,
                        entity_title=risk.entity_title,
                        attention_score=round(risk.score * 1.5, 2),
                        why_it_matters=risk.reason,
                        evidence=risk.evidence,
                        risk_of_delay=f"Critical {risk.risk_type} will worsen.",
                        expected_leverage_gain="Preventing trust/leverage loss.",
                    )
                )

        # Score opportunities
        for opp in opportunities:
            opp_score = opp.impact_score * opp.confidence_score
            if opp_score > 0.5:
                priorities.append(
                    Priority(
                        entity_id=opp.entity_id,
                        entity_title=opp.entity_title,
                        attention_score=round(opp_score * 1.2, 2),
                        why_it_matters=opp.opportunity_type,
                        evidence=opp.evidence,
                        risk_of_delay="Missed leverage potential.",
                        expected_leverage_gain="High impact opportunity.",
                    )
                )

        # Phase 10.1: Score Relationships natively using Intelligence Engine
        for data in relationship_data:
            rel = data["relationship"]
            if data["is_neglected"]:
                priorities.append(
                    Priority(
                        entity_id=str(rel.id),
                        entity_title=f"Contact {rel.role}: {rel.name}",
                        attention_score=round(data["leverage_score"] * 1.5, 2), # Multiplied heavily
                        why_it_matters=f"High-Value Relationship at Risk.",
                        evidence=f"Strategic Value {rel.strategic_value}. Health dropped to {round(data['health_score'], 2)}. No recent contact.",
                        risk_of_delay="Loss of strategic leverage and revenue.",
                        expected_leverage_gain="Restoring relationship health.",
                    )
                )
            elif data["pending_commitments"] > 0:
                priorities.append(
                    Priority(
                        entity_id=str(rel.id),
                        entity_title=f"Pending Commitments for {rel.name}",
                        attention_score=round(data["leverage_score"] * 1.2, 2),
                        why_it_matters=f"You owe {data['pending_commitments']} deliverables.",
                        evidence=f"Unmet commitments destroy Trust. Current Trust Level: {rel.trust_level}",
                        risk_of_delay="Loss of Trust.",
                        expected_leverage_gain="Delivering on promises.",
                    )
                )

        # Phase 10.2: Score Missions and Bottlenecks
        for md in mission_data:
            # Score stalled projects
            for p_data in md["projects"]:
                if p_data["forecast"] == "Stall":
                    priorities.append(
                        Priority(
                            entity_id=str(p_data["project"].id),
                            entity_title=f"Project Stalled: {p_data['project'].title}",
                            attention_score=0.95, # Very high attention
                            why_it_matters=f"Forecast indicates momentum is dead (Velocity: {p_data['velocity']} tasks/day).",
                            evidence=f"Pending tasks accumulating without progress.",
                            risk_of_delay="Mission failure.",
                            expected_leverage_gain="Unblocking critical path.",
                        )
                    )
            # Score severe bottlenecks
            for b_data in md["bottlenecks"]:
                if b_data["blast_radius_impact"] > 20: # Arbitrary high threshold
                    task = b_data["task"]
                    priorities.append(
                        Priority(
                            entity_id=str(task.id),
                            entity_title=f"Critical Bottleneck: {task.statement}",
                            attention_score=0.90,
                            why_it_matters=f"Blocking {b_data['blocks_count']} tasks with massive impact.",
                            evidence=f"Blast Radius Impact Score: {b_data['blast_radius_impact']}",
                            risk_of_delay="Cascading project delays.",
                            expected_leverage_gain="Resolving multi-task dependency.",
                        )
                    )

        # Phase 10.3: Score Business Existential Risks
        runway = business_data["runway_months"]
        if runway < 6.0:
            priorities.append(
                Priority(
                    entity_id="finance_runway",
                    entity_title="EXISTENTIAL: Low Runway",
                    attention_score=1.0, # Highest possible priority
                    why_it_matters=f"Only {runway} months of cash remaining at current burn rate.",
                    evidence=f"Monthly Burn Rate: ${business_data['monthly_burn_rate']}.",
                    risk_of_delay="Company death.",
                    expected_leverage_gain="Survival.",
                )
            )
            
        founder_roi = business_data["founder_roi_score"]
        if founder_roi < 1.0 and business_data["hours_tracked"] > 10.0:
            priorities.append(
                Priority(
                    entity_id="founder_roi",
                    entity_title="Warning: Negative Founder ROI",
                    attention_score=0.85,
                    why_it_matters=f"Your time is destroying enterprise value. ROI Score: {founder_roi}x.",
                    evidence=f"You invested {business_data['hours_tracked']} hours recently with inadequate leverage returns.",
                    risk_of_delay="Opportunity cost of working on the wrong things.",
                    expected_leverage_gain="Realigning focus to high-leverage tasks.",
                )
            )

        return sorted(priorities, key=lambda x: x.attention_score, reverse=True)[:3]
