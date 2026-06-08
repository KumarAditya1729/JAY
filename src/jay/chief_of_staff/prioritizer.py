from sqlalchemy.orm import Session
from jay.engines.attention import AttentionEngine
from .schemas import TopPriority

class Prioritizer:
    def __init__(self, session: Session):
        self.session = session
        self.engine = AttentionEngine(session)

    def analyze(self) -> list[TopPriority]:
        priorities = self.engine.analyze()
        return [
            TopPriority(
                entity_id=p.entity_id,
                entity_title=p.entity_title,
                attention_score=p.attention_score,
                why_it_matters=p.why_it_matters
            )
            for p in priorities
        ]
