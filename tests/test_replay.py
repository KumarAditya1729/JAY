import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jay.db import Base
from jay.events.engine import ReplayEngine
from jay.intent.models import IntentNode
from jay.intent.projector import IntentProjector
from jay.leverage.models import LeverageLedger
from jay.leverage.projector import LeverageProjector
from jay.decisions.projector import DecisionProjector
from jay.memory.models import EventLog, MemoryItem
from jay.memory.projector import MemoryProjector
from jay.trust.models import TrustLedger
from jay.trust.projector import TrustProjector
import jay.memory.models as models
import jay.trust.models as trust_models
import jay.decisions.models as decision_models
import jay.founder.models as founder_models
from jay.founder.projector import FounderProjector
from sqlalchemy import JSON

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

models.MemoryItem.__table__.c.tags.type = JSON()
models.MemoryItem.__table__.c.linked_entity_ids.type = JSON()
models.EventLog.__table__.c.payload.type = JSON()
models.EventLog.__table__.c.trust.type = JSON()
models.EventLog.__table__.c.metadata.type = JSON()
trust_models.TrustLedger.__table__.c.assumptions.type = JSON()
trust_models.TrustLedger.__table__.c.evidence.type = JSON()
decision_models.DecisionLedger.__table__.c.options_considered.type = JSON()
decision_models.DecisionLedger.__table__.c.evidence.type = JSON()
decision_models.DecisionLedger.__table__.c.assumptions.type = JSON()
decision_models.DecisionLedger.__table__.c.risks.type = JSON()
decision_models.DecisionLedger.__table__.c.linked_entity_ids.type = JSON()
founder_models.BehaviorLedger.__table__.c.context.type = JSON()


@pytest.fixture(scope="function")
def session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()


def test_replay_idempotency_and_integrity(session):
    # 1. Create mock events in the database directly
    events = [
        EventLog(
            stream_id="memory:1",
            event_type="memory.item_recorded",
            actor_id="tester",
            entity_type="memory_item",
            entity_id="1",
            payload={
                "kind": "project",
                "title": "Test Project",
                "body": "Body of test",
                "source": "manual",
                "importance": 5,
                "confidence": 0.9,
            },
            trust={
                "confidence_score": 0.9,
                "risk_score": 0.1,
                "impact_score": 0.8,
                "reversibility_score": 0.2,
                "evidence_score": 0.7,
                "assumptions": ["test"],
                "evidence": ["test_evidence"],
                "aligned_intent_ids": ["mission_1"]
            }
        ),
        EventLog(
            stream_id="memory:2",
            event_type="memory.item_recorded",
            actor_id="tester",
            entity_type="memory_item",
            entity_id="2",
            payload={
                "kind": "idea",
                "title": "Test Idea",
                "body": "Another body",
                "source": "manual",
                "importance": 3,
                "confidence": 0.5,
            },
            trust={
                "confidence_score": 0.5,
                "risk_score": 0.4,
                "impact_score": 0.3,
                "reversibility_score": 0.9,
                "evidence_score": 0.2,
                "assumptions": [],
                "evidence": [],
                "aligned_intent_ids": ["mission_1"]
            }
        ),
        EventLog(
            stream_id="intent:mission_1",
            event_type="intent.node_created",
            actor_id="system",
            entity_type="intent_node",
            entity_id="mission_1",
            payload={
                "node_type": "mission",
                "title": "Test Mission",
                "description": "Test Mission Description",
                "status": "active"
            }
        ),
        EventLog(
            stream_id="leverage:project:1",
            event_type="leverage.recorded",
            actor_id="system",
            entity_type="project",
            entity_id="1",
            payload={
                "hours_saved": 5.0,
                "knowledge_preserved_score": 0.8,
                "decisions_improved_score": 0.5,
                "risks_avoided_score": 0.4,
                "opportunities_captured_score": 0.2,
                "notes": "Automated email parsing"
            }
        ),
        EventLog(
            stream_id="decision:11111111-1111-1111-1111-111111111111",
            event_type="decision.recorded",
            actor_id="system",
            entity_type="decision",
            entity_id="11111111-1111-1111-1111-111111111111",
            payload={
                "statement": "Use Postgres",
                "decision_type": "Architecture",
                "maker": "CTO",
            }
        ),
        EventLog(
            stream_id="founder:profile",
            event_type="founder.profile.updated",
            actor_id="system",
            entity_type="founder_profile",
            entity_id="default",
            payload={
                "risk_tolerance": "High"
            }
        )
    ]
    session.add_all(events)
    session.commit()

    # Verify no memory items exist initially
    assert session.query(MemoryItem).count() == 0

    # 2. Run Replay Engine
    engine = ReplayEngine(session, [
        MemoryProjector(), 
        TrustProjector(), 
        IntentProjector(), 
        LeverageProjector(),
        DecisionProjector(),
        FounderProjector()
    ])
    engine.rebuild()

    # Verify memory items were created
    items = session.query(MemoryItem).all()
    assert len(items) == 2
    assert {i.id for i in items} == {"1", "2"}
    
    # Verify trust ledger entries were created
    trust_entries = session.query(TrustLedger).all()
    assert len(trust_entries) == 2
    assert {str(t.entity_id) for t in trust_entries} == {"1", "2"}
    
    # Verify intent nodes were created
    intent_nodes = session.query(IntentNode).all()
    assert len(intent_nodes) == 1
    assert intent_nodes[0].id == "mission_1"

    # Verify leverage ledger entries were created
    leverage_entries = session.query(LeverageLedger).all()
    assert len(leverage_entries) == 1

    # Verify decision ledger entries were created
    decision_entries = session.query(decision_models.DecisionLedger).all()
    assert len(decision_entries) == 1
    assert str(decision_entries[0].id) == "11111111-1111-1111-1111-111111111111"

    # Verify founder profile was created
    profile = session.query(founder_models.FounderProfile).filter(founder_models.FounderProfile.id == "default").first()
    assert profile is not None
    assert profile.risk_tolerance == "High"

    # 3. Test Idempotency (run again)
    engine.rebuild()
    
    # Still only 2 items and 2 trust entries
    trust_entries = session.query(TrustLedger).all()
    assert len(trust_entries) == 2
    
    intent_nodes = session.query(IntentNode).all()
    assert len(intent_nodes) == 1
    
    leverage_entries = session.query(LeverageLedger).all()
    assert len(leverage_entries) == 1
