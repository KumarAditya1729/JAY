from sqlalchemy.orm import Session
from jay.engines.risk import RiskEngine
from jay.engines.attention import AttentionEngine
from jay.leverage.service import LeverageService
from .leverage_ranker import LeverageRanker, CandidateAction
from .schemas import HighestLeverageAction

class RecommendationEngine:
    def __init__(self, session: Session):
        self.session = session
        self.ranker = LeverageRanker()
        self.attention = AttentionEngine(session)
        self.risk = RiskEngine(session)
        
    def generate_highest_leverage_action(self) -> HighestLeverageAction | None:
        candidates = []
        
        priorities = self.attention.analyze()
        for p in priorities:
            candidates.append(CandidateAction(
                statement=f"Address {p.entity_title}",
                reason=p.why_it_matters,
                impact=min(10.0, p.attention_score * 5),
                urgency=8.0,
                intent_alignment=9.0,
                trust=8.5,
                reversibility=7.0
            ))
            
        risks = self.risk.analyze()
        for r in risks:
            if r.score > 0.7:
                candidates.append(CandidateAction(
                    statement=f"Mitigate Risk: {r.entity_title}",
                    reason=r.reason,
                    impact=min(10.0, r.score * 10),
                    urgency=9.0,
                    intent_alignment=8.0,
                    trust=9.0,
                    reversibility=6.0
                ))
                
        # Default fallback
        if not candidates:
            candidates.append(CandidateAction(
                statement="Review JAY Architecture and Goals",
                reason="No critical operational risks detected. Perfect time for strategic planning.",
                impact=7.0,
                urgency=3.0,
                intent_alignment=10.0,
                trust=10.0,
                reversibility=10.0
            ))
            
        ranked = self.ranker.rank(candidates)
        top_action, score = ranked[0]
        
        return HighestLeverageAction(
            statement=top_action.statement,
            reason=top_action.reason,
            impact_score=round(top_action.impact, 1),
            estimated_leverage="+10 hours/week",  # Simplification for now
            confidence_score=round(score, 1)
        )
