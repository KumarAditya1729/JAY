from sqlalchemy.orm import Session
from jay.engines.relationship import RelationshipEngine
from .schemas import RelationshipAlert

class RelationshipMonitor:
    def __init__(self, session: Session):
        self.session = session
        self.engine = RelationshipEngine(session)

    def analyze(self) -> list[RelationshipAlert]:
        alerts = []
        relationships = self.engine.analyze()
        
        for rel in relationships:
            if rel.status == "neglected" or rel.last_contacted_days_ago > 30:
                score = round(rel.health_score * 100, 1)
                
                recommendation = "Send a short check-in message."
                if rel.leverage_potential > 0.7:
                    recommendation = "High leverage. Schedule a catch-up call."
                    
                alerts.append(RelationshipAlert(
                    person=rel.name,
                    score=score,
                    last_contact_days_ago=rel.last_contacted_days_ago,
                    recommendation=recommendation
                ))
                
        return sorted(alerts, key=lambda x: x.score)
