from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import sessionmaker

from jay.db import Base
from jay.engines.attention import AttentionEngine
from jay.engines.opportunity import OpportunityEngine
from jay.engines.relationship import RelationshipEngine
from jay.engines.risk import RiskEngine
from jay.leverage.models import LeverageLedger
from jay.memory.models import MemoryItem
from jay.trust.models import TrustLedger
import jay.memory.models as models
import jay.trust.models as trust_models

models.MemoryItem.__table__.c.tags.type = JSON()
models.MemoryItem.__table__.c.linked_entity_ids.type = JSON()
models.EventLog.__table__.c.payload.type = JSON()
models.EventLog.__table__.c.trust.type = JSON()
models.EventLog.__table__.c.metadata.type = JSON()
trust_models.TrustLedger.__table__.c.assumptions.type = JSON()
trust_models.TrustLedger.__table__.c.evidence.type = JSON()

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_risk_engine(session):
    now = datetime.now(timezone.utc)
    
    c = MemoryItem(
        id="c1",
        kind="commitment",
        title="Overdue task",
        body="test",
        source="system",
        importance=5,
        confidence=1.0,
        tags=[],
        occurred_at=now - timedelta(days=2),
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2)
    )
    p = MemoryItem(
        id="p1",
        kind="project",
        title="Failing Project",
        body="test",
        source="system",
        importance=4,
        confidence=0.9,
        tags=[],
        created_at=now,
        updated_at=now
    )
    t = TrustLedger(
        entity_type="project",
        entity_id="p1",
        confidence_score=0.4,
        risk_score=0.5,
        impact_score=0.5,
        reversibility_score=0.5,
        evidence_score=0.5,
        assumptions=[],
        evidence=[]
    )
    session.add_all([c, p, t])
    session.commit()

    engine = RiskEngine(session)
    risks = engine.analyze()
    
    assert len(risks) == 3 
    types = [r.risk_type for r in risks]
    assert "Commitment Risk" in types
    assert "Project Risk" in types
    assert "Intent Misalignment Risk" in types

def test_opportunity_engine(session):
    now = datetime.now(timezone.utc)
    
    p = MemoryItem(
        id="p2",
        kind="project",
        title="Dormant Project",
        body="test",
        source="system",
        importance=5,
        confidence=1.0,
        tags=[],
        created_at=now - timedelta(days=20),
        updated_at=now - timedelta(days=20)
    )
    d = MemoryItem(
        id="d1",
        kind="decision",
        title="Unfinished Decision",
        body="test",
        source="system",
        importance=3,
        confidence=0.3, 
        tags=[],
        created_at=now,
        updated_at=now
    )
    session.add_all([p, d])
    session.commit()
    
    engine = OpportunityEngine(session)
    opps = engine.analyze()
    
    assert len(opps) == 2
    types = [o.opportunity_type for o in opps]
    assert "Dormant Project" in types
    assert "Unfinished Decision" in types

def test_relationship_engine(session):
    now = datetime.now(timezone.utc)
    person = MemoryItem(
        id="person1",
        kind="person",
        title="Important Contact",
        body="test",
        source="system",
        importance=5,
        confidence=1.0,
        tags=[],
        created_at=now - timedelta(days=100),
        updated_at=now - timedelta(days=100)
    )
    session.add(person)
    session.commit()
    
    engine = RelationshipEngine(session)
    rels = engine.analyze()
    assert len(rels) == 1
    assert rels[0].status == "neglected"

def test_attention_engine(session):
    now = datetime.now(timezone.utc)
    
    # 1 critical risk (overdue commitment)
    c = MemoryItem(
        id="c1",
        kind="commitment",
        title="Overdue task",
        body="test",
        source="system",
        importance=5,
        confidence=1.0,
        tags=[],
        occurred_at=now - timedelta(days=2),
        created_at=now,
        updated_at=now
    )
    
    # 1 high impact opportunity (unfinished decision)
    d = MemoryItem(
        id="d1",
        kind="decision",
        title="Unfinished Decision",
        body="test",
        source="system",
        importance=5,
        confidence=0.1, 
        tags=[],
        created_at=now,
        updated_at=now,
        linked_entity_ids=["some_intent"]
    )
    
    # 1 neglected relationship
    p = MemoryItem(
        id="person1",
        kind="person",
        title="Important Contact",
        body="test",
        source="system",
        importance=5,
        confidence=1.0,
        tags=[],
        created_at=now - timedelta(days=100),
        updated_at=now - timedelta(days=100)
    )
    
    session.add_all([c, d, p])
    session.commit()
    
    engine = AttentionEngine(session)
    priorities = engine.analyze()
    
    assert len(priorities) == 3
