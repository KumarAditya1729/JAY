from collections import defaultdict
from sqlalchemy.orm import Session

from jay.founder.models import BehaviorLedger
from jay.founder.service import FounderService


class PreferenceEngine:
    def __init__(self, session: Session):
        self.session = session
        self.service = FounderService(session)

    def generate_graph(self) -> None:
        behaviors = self.session.query(BehaviorLedger).all()
        
        action_counts = defaultdict(int)
        recommendation_accepted = defaultdict(int)
        recommendation_rejected = defaultdict(int)

        for b in behaviors:
            action_counts[b.action] += 1
            if b.recommendation:
                if b.response == "Accepted":
                    recommendation_accepted[b.recommendation] += 1
                elif b.response == "Rejected":
                    recommendation_rejected[b.recommendation] += 1

        for action, count in action_counts.items():
            self.service.update_preference_edge(
                source="founder",
                target=action,
                rel="prefers_action",
                weight=1.0 + (count * 0.1),
                actor_id="system"
            )

        for rec, count in recommendation_accepted.items():
            self.service.update_preference_edge(
                source="founder",
                target=rec,
                rel="accepts_recommendation",
                weight=1.0 + (count * 0.2),
                actor_id="system"
            )
            
        for rec, count in recommendation_rejected.items():
            self.service.update_preference_edge(
                source="founder",
                target=rec,
                rel="rejects_recommendation",
                weight=max(0.1, 1.0 - (count * 0.2)),
                actor_id="system"
            )
