import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from jay.events.projector import Projector
from jay.intent.models import IntentEdge, IntentNode
from jay.memory.models import EventLog

logger = logging.getLogger(__name__)


class IntentProjector(Projector):
    @property
    def name(self) -> str:
        return "intent"

    def handle(self, event: EventLog, session: Session) -> None:
        if event.event_type in ("intent.node_created", "intent.node_updated"):
            payload = event.payload
            node = session.query(IntentNode).filter_by(id=event.entity_id).first()
            if not node:
                node = IntentNode(
                    id=event.entity_id,
                    node_type=payload["node_type"],
                    title=payload["title"],
                    description=payload.get("description"),
                    status=payload.get("status", "active"),
                    created_at=event.occurred_at,
                    updated_at=event.occurred_at,
                )
                session.add(node)
            else:
                if "title" in payload:
                    node.title = payload["title"]
                if "description" in payload:
                    node.description = payload["description"]
                if "status" in payload:
                    node.status = payload["status"]
                node.updated_at = event.occurred_at

        elif event.event_type == "intent.edge_created":
            payload = event.payload
            edge = (
                session.query(IntentEdge)
                .filter_by(
                    source_id=payload["source_id"],
                    target_id=payload["target_id"],
                    relationship_type=payload["relationship_type"],
                )
                .first()
            )
            if not edge:
                edge = IntentEdge(
                    source_id=payload["source_id"],
                    target_id=payload["target_id"],
                    relationship_type=payload["relationship_type"],
                    created_at=event.occurred_at,
                )
                session.add(edge)

        elif event.event_type == "intent.edge_deleted":
            payload = event.payload
            session.query(IntentEdge).filter_by(
                source_id=payload["source_id"],
                target_id=payload["target_id"],
                relationship_type=payload["relationship_type"],
            ).delete()

    def reset(self, session: Session) -> None:
        if session.bind.dialect.name == "postgresql":
            session.execute(text("TRUNCATE TABLE intent_edges CASCADE;"))
            session.execute(text("TRUNCATE TABLE intent_nodes CASCADE;"))
        else:
            session.execute(text("DELETE FROM intent_edges;"))
            session.execute(text("DELETE FROM intent_nodes;"))
        logger.info("Truncated intent tables.")
