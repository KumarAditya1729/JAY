from sqlalchemy.orm import Session

from jay.intent.models import IntentNode
from jay.founder.models import BehaviorLedger
from jay.decisions.models import DecisionLedger


class ConsistencyEngine:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> dict:
        intent_nodes = (
            self.session.query(IntentNode).filter(IntentNode.status == "active").all()
        )
        behaviors = self.session.query(BehaviorLedger).all()
        decisions = self.session.query(DecisionLedger).all()

        gaps = []
        alignment_score = 100

        # 1. Action vs Intent gap
        if intent_nodes and not behaviors and not decisions:
            gaps.append(
                "Founder has stated goals/intents, but no actions or decisions have been recorded."
            )
            alignment_score -= 20

        # 2. Decision alignment check
        unaligned_decisions = [d for d in decisions if d.intent_alignment_score < 0.5]
        if unaligned_decisions:
            ratio = len(unaligned_decisions) / len(decisions)
            if ratio > 0.3:
                gaps.append(
                    f"{ratio*100:.0f}% of recent decisions are not aligned with Founder Intent."
                )
                alignment_score -= int(ratio * 30)

        # 3. Recommendations ignoring
        ignored = [b for b in behaviors if b.recommendation and b.response == "Ignored"]
        if ignored and len(behaviors) > 0:
            ratio = len(ignored) / len([b for b in behaviors if b.recommendation])
            if ratio > 0.5:
                gaps.append(
                    f"Founder is ignoring {ratio*100:.0f}% of system recommendations."
                )
                alignment_score -= int(ratio * 20)

        return {
            "consistency_score": max(0, alignment_score),
            "identified_gaps": (
                gaps
                if gaps
                else ["Founder is acting consistently with stated intent and goals."]
            ),
        }
