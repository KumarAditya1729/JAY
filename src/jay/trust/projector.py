import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from jay.events.projector import Projector
from jay.memory.models import EventLog
from jay.trust.models import TrustLedger

logger = logging.getLogger(__name__)


class TrustProjector(Projector):
    @property
    def name(self) -> str:
        return "trust"

    def handle(self, event: EventLog, session: Session) -> None:
        if not event.trust:
            return

        trust_data = event.trust

        ledger_entry = TrustLedger(
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            confidence_score=trust_data.get("confidence_score", 0.7),
            risk_score=trust_data.get("risk_score", 0.0),
            impact_score=trust_data.get("impact_score", 0.5),
            reversibility_score=trust_data.get("reversibility_score", 0.8),
            evidence_score=trust_data.get("evidence_score", 0.5),
            assumptions=trust_data.get("assumptions", []),
            evidence=trust_data.get("evidence", []),
            created_at=event.occurred_at,
        )

        session.add(ledger_entry)

    def reset(self, session: Session) -> None:
        if session.bind.dialect.name == "postgresql":
            session.execute(text("TRUNCATE TABLE trust_ledger;"))
        else:
            session.execute(text("DELETE FROM trust_ledger;"))
        logger.info("Truncated trust_ledger table.")
