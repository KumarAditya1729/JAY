from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from jay.engines.schemas import Relationship
from jay.memory.models import MemoryItem

class RelationshipEngine:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> list[Relationship]:
        relationships = []
        now = datetime.now(timezone.utc)

        people = self.session.query(MemoryItem).filter(MemoryItem.kind == "person").all()

        # Optimize by loading all meetings once
        meetings = self.session.query(MemoryItem).filter(MemoryItem.kind == "meeting").all()

        for person in people:
            person_meetings = [m for m in meetings if person.id in m.linked_entity_ids]
            
            last_contact = max([m.occurred_at or m.created_at for m in person_meetings], default=None)
            
            if last_contact:
                last_contact = last_contact.replace(tzinfo=timezone.utc) if last_contact.tzinfo is None else last_contact
                days_since = (now - last_contact).days
            else:
                created_at = person.created_at.replace(tzinfo=timezone.utc) if person.created_at.tzinfo is None else person.created_at
                days_since = (now - created_at).days
                
            # Health score heuristic
            health_score = 1.0
            if days_since > 30:
                health_score = max(0.0, 1.0 - ((days_since - 30) * 0.02))
                
            status = "healthy"
            if health_score < 0.4 and person.importance >= 4:
                status = "neglected"
            elif health_score < 0.7:
                status = "fading"

            relationships.append(Relationship(
                entity_id=person.id,
                name=person.title,
                health_score=round(health_score, 2),
                last_contacted_days_ago=days_since,
                status=status
            ))
            
        return sorted(relationships, key=lambda x: x.health_score)
