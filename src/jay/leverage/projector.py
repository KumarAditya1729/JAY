import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from jay.events.projector import Projector
from jay.leverage.models import LeverageLedger
from jay.memory.models import EventLog

logger = logging.getLogger(__name__)


class LeverageProjector(Projector):
    @property
    def name(self) -> str:
        return "leverage"

    def handle(self, event: EventLog, session: Session) -> None:
        if event.event_type != "leverage.recorded":
            return

        payload = event.payload

        ledger_entry = LeverageLedger(
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            hours_saved=payload.get("hours_saved", 0.0),
            knowledge_preserved_score=payload.get("knowledge_preserved_score", 0.0),
            decisions_improved_score=payload.get("decisions_improved_score", 0.0),
            risks_avoided_score=payload.get("risks_avoided_score", 0.0),
            opportunities_captured_score=payload.get(
                "opportunities_captured_score", 0.0
            ),
            notes=payload.get("notes"),
            created_at=event.occurred_at,
        )

        session.add(ledger_entry)

    def reset(self, session: Session) -> None:
        if session.bind.dialect.name == "postgresql":
            session.execute(text("TRUNCATE TABLE leverage_ledger;"))
        else:
            session.execute(text("DELETE FROM leverage_ledger;"))
        logger.info("Truncated leverage_ledger table.")
