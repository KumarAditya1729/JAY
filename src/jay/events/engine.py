import logging

from sqlalchemy.orm import Session

from jay.events.projector import Projector
from jay.memory.models import EventLog

logger = logging.getLogger(__name__)


class ReplayEngine:
    def __init__(self, session: Session, projectors: list[Projector]):
        self.session = session
        self.projectors = projectors

    def rebuild(self) -> None:
        logger.info(f"Starting replay engine with {len(self.projectors)} projectors.")

        # 1. Reset all projectors
        for projector in self.projectors:
            logger.info(f"Resetting projector: {projector.name}")
            projector.reset(self.session)

        # Commit resets
        self.session.commit()

        # 2. Stream all events
        events = self.session.query(EventLog).order_by(EventLog.occurred_at.asc()).all()

        logger.info(f"Found {len(events)} events to replay.")

        # 3. Apply events to projectors
        for count, event in enumerate(events, 1):
            for projector in self.projectors:
                try:
                    projector.handle(event, self.session)
                except Exception as e:
                    logger.error(
                        f"Projector {projector.name} failed on event {event.id}: {e}"
                    )
                    self.session.rollback()
                    raise

            # Commit in batches or at the end. For now, every 100 events or at the end.
            if count % 100 == 0:
                self.session.commit()
                logger.info(f"Replayed {count} events...")

        # Final commit
        self.session.commit()
        logger.info("Replay complete.")
