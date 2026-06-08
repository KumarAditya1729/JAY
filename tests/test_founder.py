import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker

from jay.db import Base
from jay.founder.models import BehaviorLedger, PreferenceEdge, FounderProfile
from jay.founder.engines.preference import PreferenceEngine
from jay.founder.engines.decision_style import DecisionStyleEngine
from jay.founder.engines.consistency import ConsistencyEngine
from jay.decisions.models import DecisionLedger
from jay.intent.models import IntentNode

# Patch for SQLite
BehaviorLedger.__table__.c.context.type = JSON()
DecisionLedger.__table__.c.options_considered.type = JSON()
DecisionLedger.__table__.c.evidence.type = JSON()
DecisionLedger.__table__.c.assumptions.type = JSON()
DecisionLedger.__table__.c.risks.type = JSON()
DecisionLedger.__table__.c.linked_entity_ids.type = JSON()

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_preference_engine(session):
    # Setup some behavior
    b1 = BehaviorLedger(action="Schedule Meeting", recommendation="Meet with CTO", response="Accepted")
    b2 = BehaviorLedger(action="Review Code", recommendation="Meet with CTO", response="Accepted")
    b3 = BehaviorLedger(action="Ignore Alert", recommendation="Update system", response="Rejected")
    
    session.add_all([b1, b2, b3])
    session.commit()
    
    engine = PreferenceEngine(session)
    engine.generate_graph()
    
    edges = session.query(PreferenceEdge).all()
    # We should have prefers_action edges for the actions, and accepts/rejects for recommendations
    assert len(edges) > 0
    
    accept_edge = session.query(PreferenceEdge).filter(PreferenceEdge.target_id == "Meet with CTO").first()
    assert float(accept_edge.weight) == 1.4 # 1.0 + (2 * 0.2)
    
    reject_edge = session.query(PreferenceEdge).filter(PreferenceEdge.target_id == "Update system").first()
    assert float(reject_edge.weight) == 0.8 # 1.0 - (1 * 0.2)


def test_consistency_engine(session):
    # Intent exists, but no behaviors or decisions
    n = IntentNode(id="n1", node_type="mission", title="Build fast", status="active")
    session.add(n)
    session.commit()
    
    engine = ConsistencyEngine(session)
    result = engine.analyze()
    
    assert result["consistency_score"] == 80 # Lost 20 due to no actions/decisions
    assert "no actions" in result["identified_gaps"][0].lower()
