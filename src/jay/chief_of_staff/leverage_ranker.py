from dataclasses import dataclass

@dataclass
class CandidateAction:
    statement: str
    reason: str
    impact: float
    urgency: float
    intent_alignment: float
    trust: float
    reversibility: float

class LeverageRanker:
    """
    Leverage Priority Score =
    (Impact × 0.35)
    + (Urgency × 0.25)
    + (Intent Alignment × 0.20)
    + (Trust × 0.10)
    + (Reversibility × 0.10)
    """
    
    def score(self, action: CandidateAction) -> float:
        return (
            (action.impact * 0.35) +
            (action.urgency * 0.25) +
            (action.intent_alignment * 0.20) +
            (action.trust * 0.10) +
            (action.reversibility * 0.10)
        )
        
    def rank(self, actions: list[CandidateAction]) -> list[tuple[CandidateAction, float]]:
        scored = [(a, self.score(a)) for a in actions]
        return sorted(scored, key=lambda x: x[1], reverse=True)
