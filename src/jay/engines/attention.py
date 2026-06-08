from sqlalchemy.orm import Session

from jay.engines.opportunity import OpportunityEngine
from jay.engines.relationship import RelationshipEngine
from jay.engines.risk import RiskEngine
from jay.engines.schemas import Priority
from jay.leverage.service import LeverageService


class AttentionEngine:
    def __init__(self, session: Session):
        self.session = session
        self.risk_engine = RiskEngine(session)
        self.opportunity_engine = OpportunityEngine(session)
        self.relationship_engine = RelationshipEngine(session)
        self.leverage_service = LeverageService(session)

    def analyze(self) -> list[Priority]:
        priorities = []

        risks = self.risk_engine.analyze()
        opportunities = self.opportunity_engine.analyze()
        relationships = self.relationship_engine.analyze()

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

        # Score relationships
        for rel in relationships:
            if rel.status == "neglected":
                priorities.append(
                    Priority(
                        entity_id=rel.entity_id,
                        entity_title=rel.name,
                        attention_score=round((1.0 - rel.health_score) * 1.4, 2),
                        why_it_matters=f"Relationship is {rel.status}.",
                        evidence=f"Last contacted {rel.last_contacted_days_ago} days ago.",
                        risk_of_delay="Loss of strategic relationship.",
                        expected_leverage_gain="Restoring relationship health.",
                    )
                )

        return sorted(priorities, key=lambda x: x.attention_score, reverse=True)[:3]
