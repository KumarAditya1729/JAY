from sqlalchemy.orm import Session
from datetime import datetime, timezone

from jay.engines.risk import RiskEngine
from jay.decisions.models import DecisionLedger

from .schemas import CommandCenterResponse, CriticalRisk, DecisionReview
from .commitment_monitor import CommitmentMonitor
from .relationship_monitor import RelationshipMonitor
from .project_monitor import ProjectMonitor
from .prioritizer import Prioritizer
from .recommendation_engine import RecommendationEngine

class ChiefOfStaffService:
    def __init__(self, session: Session):
        self.session = session
        self.commitments = CommitmentMonitor(session)
        self.relationships = RelationshipMonitor(session)
        self.projects = ProjectMonitor(session)
        self.prioritizer = Prioritizer(session)
        self.recommendations = RecommendationEngine(session)
        self.risks = RiskEngine(session)

    def generate_command_center(self) -> CommandCenterResponse:
        # Highest Leverage Action
        hla = self.recommendations.generate_highest_leverage_action()
        
        # Priorities
        top_priorities = self.prioritizer.analyze()
        
        # Risks
        critical_risks = []
        for r in self.risks.analyze():
            critical_risks.append(CriticalRisk(
                risk_type=r.risk_type,
                entity_title=r.entity_title,
                score=round(r.score, 2),
                reason=r.reason,
                recommended_action=r.recommended_action
            ))
            
        # Commitments
        open_commitments = self.commitments.analyze()
        
        # Relationships
        relationship_alerts = self.relationships.analyze()
        
        # Decisions to Review
        decision_reviews = []
        now = datetime.now(timezone.utc)
        decisions = self.session.query(DecisionLedger).filter(DecisionLedger.outcome_status == "Pending").all()
        for d in decisions:
            age = 0
            if d.decision_date:
                dd = d.decision_date.replace(tzinfo=timezone.utc) if d.decision_date.tzinfo is None else d.decision_date
                age = (now - dd).days
                
            if age > 7 or float(d.reversibility_score) < 0.3:
                decision_reviews.append(DecisionReview(
                    decision=d.statement,
                    age_days=age,
                    risk="High" if float(d.reversibility_score) < 0.3 else "Medium",
                    recommended_review_date="Today" if age > 14 else "This Week"
                ))
        
        # Project Health
        project_health = self.projects.analyze()
        
        # Global Scores (Mock aggregations for Phase 5.0)
        alignment_score = 98.5
        leverage_score = sum([p.momentum_score for p in project_health]) / max(len(project_health), 1) * 100

        return CommandCenterResponse(
            highest_leverage_action=hla,
            top_priorities=top_priorities,
            critical_risks=critical_risks,
            open_commitments=open_commitments,
            relationship_alerts=relationship_alerts,
            decision_reviews=decision_reviews,
            project_health=project_health,
            alignment_score=round(alignment_score, 1),
            leverage_score=round(leverage_score, 1)
        )
