from uuid import uuid4

from sqlalchemy.orm import Session

from jay.decisions.models import DecisionLedger
from jay.decisions.projector import DecisionProjector
from jay.decisions.schemas import DecisionCreate, DecisionOutcome
from jay.events.service import EventService


class DecisionService:
    def __init__(self, session: Session):
        self.session = session
        self.event_service = EventService(session)
        self.projector = DecisionProjector()

    def record_decision(
        self, decision: DecisionCreate, actor_id: str
    ) -> DecisionLedger:
        decision_id = str(uuid4())

        event = self.event_service.record(
            stream_id=f"decision-{decision_id}",
            event_type="decision.recorded",
            actor_id=actor_id,
            entity_type="decision",
            entity_id=decision_id,
            payload=decision.model_dump(),
        )

        # Synchronous projection
        self.projector.handle(event, self.session)
        self.session.commit()

        return (
            self.session.query(DecisionLedger)
            .filter(DecisionLedger.id == decision_id)
            .one()
        )

    def record_outcome(
        self, decision_id: str, outcome: DecisionOutcome, actor_id: str
    ) -> DecisionLedger:
        event = self.event_service.record(
            stream_id=f"decision-{decision_id}",
            event_type="decision.outcome.recorded",
            actor_id=actor_id,
            entity_type="decision",
            entity_id=decision_id,
            payload=outcome.model_dump(),
        )

        self.projector.handle(event, self.session)
        self.session.commit()

        return (
            self.session.query(DecisionLedger)
            .filter(DecisionLedger.id == decision_id)
            .one()
        )
