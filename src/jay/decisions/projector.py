import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text

from jay.decisions.models import DecisionLedger
from jay.memory.models import EventLog
from jay.events.projector import Projector

logger = logging.getLogger(__name__)


class DecisionProjector(Projector):
    @property
    def name(self) -> str:
        return "decisions"

    def reset(self, session: Session) -> None:
        if session.bind.dialect.name == "postgresql":
            session.execute(text("TRUNCATE TABLE decision_ledger;"))
        else:
            session.execute(text("DELETE FROM decision_ledger;"))
        logger.info("Truncated decision_ledger table.")

    def handle(self, event: EventLog, session: Session) -> None:
        if event.event_type == "decision.recorded":
            self._apply_decision_recorded(event, session)
        elif event.event_type == "decision.outcome.recorded":
            self._apply_decision_outcome_recorded(event, session)

    def _apply_decision_recorded(self, event: EventLog, session: Session) -> None:
        payload = event.payload
        decision = DecisionLedger(
            id=UUID(event.entity_id),
            statement=payload["statement"],
            decision_type=payload["decision_type"],
            maker=payload["maker"],
            options_considered=payload.get("options_considered", []),
            evidence=payload.get("evidence", []),
            assumptions=payload.get("assumptions", []),
            risks=payload.get("risks", []),
            expected_outcome=payload.get("expected_outcome"),
            success_criteria=payload.get("success_criteria"),
            reversibility_score=payload.get("reversibility_score", 0.5),
            intent_alignment_score=payload.get("intent_alignment_score", 0.5),
            trust_envelope=payload.get("trust_envelope"),
            linked_entity_ids=payload.get("linked_entity_ids", []),
            decision_date=event.occurred_at,
        )
        session.add(decision)

    def _apply_decision_outcome_recorded(
        self, event: EventLog, session: Session
    ) -> None:
        decision = (
            session.query(DecisionLedger)
            .filter(DecisionLedger.id == event.entity_id)
            .first()
        )
        if decision:
            payload = event.payload
            decision.outcome_status = payload["outcome_status"]
            decision.actual_outcome = payload.get("actual_outcome")
            decision.lessons_learned = payload.get("lessons_learned")
            decision.outcome_date = event.occurred_at
            session.add(decision)
