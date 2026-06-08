from uuid import uuid4

from sqlalchemy.orm import Session

from jay.events.service import EventService
from jay.founder.models import BehaviorLedger, FounderProfile
from jay.founder.projector import FounderProjector
from jay.founder.schemas import BehaviorCreate, FounderProfileUpdate


class FounderService:
    def __init__(self, session: Session):
        self.session = session
        self.event_service = EventService(session)
        self.projector = FounderProjector()

    def update_profile(self, update: FounderProfileUpdate, actor_id: str) -> FounderProfile:
        event = self.event_service.record(
            stream_id="founder:profile",
            event_type="founder.profile.updated",
            actor_id=actor_id,
            entity_type="founder_profile",
            entity_id="default",
            payload=update.model_dump(exclude_unset=True),
        )

        self.projector.handle(event, self.session)
        self.session.commit()

        return self.session.query(FounderProfile).filter(FounderProfile.id == "default").one()

    def record_behavior(self, behavior: BehaviorCreate, actor_id: str) -> BehaviorLedger:
        behavior_id = str(uuid4())

        event = self.event_service.record(
            stream_id=f"behavior:{behavior_id}",
            event_type="behavior.recorded",
            actor_id=actor_id,
            entity_type="behavior",
            entity_id=behavior_id,
            payload=behavior.model_dump(),
        )

        self.projector.handle(event, self.session)
        self.session.commit()

        return self.session.query(BehaviorLedger).filter(BehaviorLedger.id == behavior_id).one()

    def update_preference_edge(self, source: str, target: str, rel: str, weight: float, actor_id: str) -> None:
        event = self.event_service.record(
            stream_id=f"preference:{source}:{target}",
            event_type="preference.edge.updated",
            actor_id=actor_id,
            entity_type="preference_edge",
            entity_id=f"{source}:{target}",
            payload={
                "source_id": source,
                "target_id": target,
                "relationship_type": rel,
                "weight": weight
            },
        )

        self.projector.handle(event, self.session)
        self.session.commit()
