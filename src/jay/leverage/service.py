from sqlalchemy import func
from sqlalchemy.orm import Session

from jay.leverage.models import LeverageLedger
from jay.leverage.projector import LeverageProjector
from jay.leverage.schemas import LeverageLedgerCreate, LeverageRatio
from jay.memory.models import EventLog


class LeverageService:
    def __init__(self, session: Session):
        self.session = session

    def record_leverage(self, data: LeverageLedgerCreate) -> LeverageLedger:
        event = EventLog(
            stream_id=f"leverage:{data.entity_type}:{data.entity_id}",
            event_type="leverage.recorded",
            actor_id="system",
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            payload={
                "hours_saved": data.hours_saved,
                "knowledge_preserved_score": data.knowledge_preserved_score,
                "decisions_improved_score": data.decisions_improved_score,
                "risks_avoided_score": data.risks_avoided_score,
                "opportunities_captured_score": data.opportunities_captured_score,
                "notes": data.notes,
            },
        )
        self.session.add(event)
        LeverageProjector().handle(event, self.session)
        self.session.commit()
        return self.session.query(LeverageLedger).order_by(LeverageLedger.created_at.desc()).first()

    def get_ratio(self) -> LeverageRatio:
        stats = self.session.query(
            func.sum(LeverageLedger.hours_saved).label("total_hours"),
            func.avg(LeverageLedger.knowledge_preserved_score).label("avg_knowledge"),
            func.avg(LeverageLedger.decisions_improved_score).label("avg_decision"),
            func.avg(LeverageLedger.risks_avoided_score).label("avg_risk"),
            func.avg(LeverageLedger.opportunities_captured_score).label("avg_opp"),
        ).one_or_none()

        if not stats or stats.total_hours is None:
            return LeverageRatio(
                total_hours_saved=0.0,
                avg_knowledge_preserved=0.0,
                avg_decisions_improved=0.0,
                avg_risks_avoided=0.0,
                avg_opportunities_captured=0.0,
                ratio=0.0,
            )

        total_hours = float(stats.total_hours)
        avg_knowledge = float(stats.avg_knowledge or 0.0)
        avg_decision = float(stats.avg_decision or 0.0)
        avg_risk = float(stats.avg_risk or 0.0)
        avg_opp = float(stats.avg_opp or 0.0)

        # Simple heuristic for leverage ratio calculation
        base_multiplier = (avg_knowledge + avg_decision + avg_risk + avg_opp) / 4.0
        ratio = total_hours * (1.0 + base_multiplier)

        return LeverageRatio(
            total_hours_saved=total_hours,
            avg_knowledge_preserved=avg_knowledge,
            avg_decisions_improved=avg_decision,
            avg_risks_avoided=avg_risk,
            avg_opportunities_captured=avg_opp,
            ratio=round(ratio, 2),
        )
