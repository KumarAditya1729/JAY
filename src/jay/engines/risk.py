from datetime import datetime, timezone
from sqlalchemy.orm import Session

from jay.engines.schemas import Risk
from jay.memory.models import MemoryItem
from jay.trust.models import TrustLedger

class RiskEngine:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> list[Risk]:
        risks = []
        now = datetime.now(timezone.utc)

        # 1. Commitment Risk
        commitments = self.session.query(MemoryItem).filter(MemoryItem.kind == "commitment").all()
        for c in commitments:
            if c.occurred_at:
                occurred = c.occurred_at.replace(tzinfo=timezone.utc) if c.occurred_at.tzinfo is None else c.occurred_at
                if occurred < now:
                    if "completed" not in [t.lower() for t in c.tags]:
                        risks.append(Risk(
                            risk_type="Commitment Risk",
                            entity_id=c.id,
                            entity_title=c.title,
                            score=0.8 + (c.importance * 0.04), 
                            reason="Deadline has passed but commitment is not marked complete.",
                            evidence=f"Due {c.occurred_at.isoformat()}, importance {c.importance}.",
                            recommended_action="Follow up or renegotiate deadline immediately."
                        ))

        # 2. Project Risk
        projects = self.session.query(MemoryItem).filter(MemoryItem.kind == "project").all()
        for p in projects:
            latest_trust = self.session.query(TrustLedger).filter(
                TrustLedger.entity_id == p.id
            ).order_by(TrustLedger.created_at.desc()).first()
            if latest_trust and latest_trust.confidence_score < 0.5:
                risks.append(Risk(
                    risk_type="Project Risk",
                    entity_id=p.id,
                    entity_title=p.title,
                    score=1.0 - float(latest_trust.confidence_score),
                    reason="Project trust/confidence has dropped below acceptable levels.",
                    evidence=f"Confidence is {latest_trust.confidence_score}.",
                    recommended_action="Review project blockers and re-align expectations."
                ))

        # 3. Intent Misalignment
        decisions = self.session.query(MemoryItem).filter(MemoryItem.kind.in_(["decision", "project"])).all()
        for d in decisions:
            if not d.linked_entity_ids:
                risks.append(Risk(
                    risk_type="Intent Misalignment Risk",
                    entity_id=d.id,
                    entity_title=d.title,
                    score=0.75,
                    reason="Critical decision or project is not linked to any goals or mission.",
                    evidence="Empty linked entities array.",
                    recommended_action="Explicitly link this to a Founder Intent node."
                ))

        return sorted(risks, key=lambda x: x.score, reverse=True)
