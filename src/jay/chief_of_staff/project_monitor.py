from sqlalchemy.orm import Session
from jay.memory.models import MemoryItem
from jay.trust.models import TrustLedger
from .schemas import ProjectHealth

class ProjectMonitor:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> list[ProjectHealth]:
        healths = []
        projects = self.session.query(MemoryItem).filter(MemoryItem.kind == "project").all()
        
        for p in projects:
            latest_trust = self.session.query(TrustLedger).filter(
                TrustLedger.entity_id == p.id
            ).order_by(TrustLedger.created_at.desc()).first()
            
            trust_score = float(latest_trust.confidence_score) if latest_trust else 0.5
            alignment_score = float(latest_trust.risk_score) if latest_trust else 0.5  # inverse or mock for now
            
            # Simple momentum heuristic
            momentum = 0.8 if trust_score > 0.7 else 0.4
            activity = 0.5
            
            status = "Healthy"
            if momentum < 0.5:
                status = "Slowing"
            if trust_score < 0.4:
                status = "Critical"
                
            healths.append(ProjectHealth(
                project_id=p.title,
                momentum_score=momentum,
                trust_score=trust_score,
                intent_alignment_score=alignment_score,
                activity_score=activity,
                status=status
            ))
            
        return healths
