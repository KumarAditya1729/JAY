import logging
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from jay.memory.models import EventLog

logger = logging.getLogger(__name__)


class Projector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the projector"""
        pass

    @abstractmethod
    def handle(self, event: EventLog, session: Session) -> None:
        """Handle a single event and update the projection."""
        pass

    @abstractmethod
    def reset(self, session: Session) -> None:
        """Reset the projection to an empty state."""
        pass


class GraphProjector(Projector):
    @property
    def name(self) -> str:
        return "graph"

    def handle(self, event: EventLog, session: Session) -> None:
        logger.debug(f"GraphProjector ignored event {event.id}")

    def reset(self, session: Session) -> None:
        logger.debug("GraphProjector reset called")


class VectorProjector(Projector):
    @property
    def name(self) -> str:
        return "vector"

    def handle(self, event: EventLog, session: Session) -> None:
        logger.debug(f"VectorProjector ignored event {event.id}")

    def reset(self, session: Session) -> None:
        logger.debug("VectorProjector reset called")


class DashboardProjector(Projector):
    @property
    def name(self) -> str:
        return "dashboard"

    def handle(self, event: EventLog, session: Session) -> None:
        logger.debug(f"DashboardProjector ignored event {event.id}")

    def reset(self, session: Session) -> None:
        logger.debug("DashboardProjector reset called")
