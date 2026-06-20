import uuid
from sqlalchemy.orm import Session
from jay.memory.models import EventLog
from jay.intent.models import IntentNode, IntentEdge
from jay.intent.projector import IntentProjector
from jay.intent.schemas import IntentNodeCreate, IntentEdgeCreate


class IntentService:
    def __init__(self, session: Session):
        self.session = session

    def create_node(self, node: IntentNodeCreate) -> IntentNode:
        node_id = str(uuid.uuid4())
        event = EventLog(
            stream_id=f"intent:{node_id}",
            event_type="intent.node_created",
            actor_id="system",
            entity_type="intent_node",
            entity_id=node_id,
            payload={
                "node_type": node.node_type.value,
                "title": node.title,
                "description": node.description,
                "status": node.status,
            },
        )
        self.session.add(event)
        IntentProjector().handle(event, self.session)
        self.session.commit()
        return self.session.query(IntentNode).filter_by(id=node_id).one()

    def create_edge(self, edge: IntentEdgeCreate) -> IntentEdge:
        event = EventLog(
            stream_id=f"intent:{edge.source_id}",
            event_type="intent.edge_created",
            actor_id="system",
            entity_type="intent_edge",
            entity_id=f"{edge.source_id}-{edge.target_id}",
            payload={
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "relationship_type": edge.relationship_type,
            },
        )
        self.session.add(event)
        IntentProjector().handle(event, self.session)
        self.session.commit()
        return (
            self.session.query(IntentEdge)
            .filter_by(
                source_id=edge.source_id,
                target_id=edge.target_id,
                relationship_type=edge.relationship_type,
            )
            .one()
        )

    def list_nodes(self) -> list[IntentNode]:
        return self.session.query(IntentNode).all()

    def list_edges(self) -> list[IntentEdge]:
        return self.session.query(IntentEdge).all()
