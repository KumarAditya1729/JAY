from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from jay.engines.schemas import Opportunity
from jay.memory.models import MemoryItem


class OpportunityEngine:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> list[Opportunity]:
        opportunities = []
        now = datetime.now(timezone.utc)
        fourteen_days_ago = now - timedelta(days=14)

        # 1. Dormant Ideas / Projects
        dormant_items = (
            self.session.query(MemoryItem)
            .filter(
                MemoryItem.kind.in_(["idea", "project"]),
                MemoryItem.importance >= 4,
                MemoryItem.updated_at < fourteen_days_ago,
            )
            .all()
        )
        for item in dormant_items:
            updated = (
                item.updated_at.replace(tzinfo=timezone.utc)
                if item.updated_at.tzinfo is None
                else item.updated_at
            )
            if "completed" not in [t.lower() for t in item.tags] and "archived" not in [
                t.lower() for t in item.tags
            ]:
                opportunities.append(
                    Opportunity(
                        opportunity_type=f"Dormant {item.kind.capitalize()}",
                        entity_id=item.id,
                        entity_title=item.title,
                        impact_score=item.importance * 0.2,
                        confidence_score=float(item.confidence),
                        evidence=f"High importance ({item.importance}) but no updates since {updated.date()}.",
                        recommended_action="Review and decide whether to revive or officially archive.",
                    )
                )

        # 2. Unfinished Decisions
        decisions = (
            self.session.query(MemoryItem)
            .filter(MemoryItem.kind == "decision", MemoryItem.confidence < 0.6)
            .all()
        )
        for d in decisions:
            if "completed" not in [t.lower() for t in d.tags]:
                opportunities.append(
                    Opportunity(
                        opportunity_type="Unfinished Decision",
                        entity_id=d.id,
                        entity_title=d.title,
                        impact_score=0.8,
                        confidence_score=1.0 - float(d.confidence),
                        evidence=f"Decision confidence is very low ({d.confidence}).",
                        recommended_action="Gather missing evidence and finalize decision.",
                    )
                )

        return sorted(
            opportunities,
            key=lambda x: (x.impact_score * x.confidence_score),
            reverse=True,
        )
