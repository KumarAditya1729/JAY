import logging
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from jay.events.projector import Projector
from jay.founder.models import BehaviorLedger, FounderProfile, PreferenceEdge
from jay.memory.models import EventLog

logger = logging.getLogger(__name__)


class FounderProjector(Projector):
    @property
    def name(self) -> str:
        return "founder"

    def reset(self, session: Session) -> None:
        if session.bind.dialect.name == "postgresql":
            session.execute(text("TRUNCATE TABLE founder_profile, behavior_ledger, preference_edges;"))
        else:
            session.execute(text("DELETE FROM founder_profile;"))
            session.execute(text("DELETE FROM behavior_ledger;"))
            session.execute(text("DELETE FROM preference_edges;"))
        logger.info("Truncated founder tables.")

    def handle(self, event: EventLog, session: Session) -> None:
        if event.event_type == "behavior.recorded":
            self._apply_behavior_recorded(event, session)
        elif event.event_type == "founder.profile.updated":
            self._apply_profile_updated(event, session)
        elif event.event_type == "preference.edge.updated":
            self._apply_preference_updated(event, session)

    def _apply_behavior_recorded(self, event: EventLog, session: Session) -> None:
        payload = event.payload
        behavior = BehaviorLedger(
            id=UUID(event.entity_id),
            action=payload["action"],
            recommendation=payload.get("recommendation"),
            response=payload.get("response"),
            outcome=payload.get("outcome"),
            context=payload.get("context", {}),
            occurred_at=event.occurred_at,
        )
        session.add(behavior)

    def _apply_profile_updated(self, event: EventLog, session: Session) -> None:
        profile = session.query(FounderProfile).filter(FounderProfile.id == "default").first()
        if not profile:
            profile = FounderProfile(id="default")
            session.add(profile)
        
        payload = event.payload
        for k, v in payload.items():
            if hasattr(profile, k) and v is not None:
                setattr(profile, k, v)

    def _apply_preference_updated(self, event: EventLog, session: Session) -> None:
        payload = event.payload
        source = payload["source_id"]
        target = payload["target_id"]
        rel = payload["relationship_type"]
        weight = payload["weight"]

        edge = (
            session.query(PreferenceEdge)
            .filter(
                PreferenceEdge.source_id == source,
                PreferenceEdge.target_id == target,
                PreferenceEdge.relationship_type == rel,
            )
            .first()
        )

        if not edge:
            edge = PreferenceEdge(
                source_id=source, target_id=target, relationship_type=rel, weight=weight
            )
            session.add(edge)
        else:
            edge.weight = weight
