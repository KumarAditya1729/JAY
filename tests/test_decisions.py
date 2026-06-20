from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import sessionmaker

from jay.db import Base
from jay.decisions.analytics import DecisionAnalytics
from jay.decisions.models import DecisionLedger
from jay.decisions.patterns import DecisionPatternDetector
from jay.decisions.review import DecisionReviewEngine

# Patch JSON for SQLite
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


def test_decision_analytics(session):
    now = datetime.now(timezone.utc)

    # 1 Success, Reversible
    d1 = DecisionLedger(
        statement="Use Postgres",
        decision_type="Architecture",
        maker="System",
        outcome_status="Success",
        reversibility_score=0.8,
        outcome_date=now - timedelta(days=5),
    )

    # 1 Failure, Irreversible
    d2 = DecisionLedger(
        statement="Drop old database",
        decision_type="Migration",
        maker="System",
        outcome_status="Failure",
        reversibility_score=0.1,
        outcome_date=now - timedelta(days=2),
    )

    # 1 Pending
    d3 = DecisionLedger(
        statement="Rewrite in Rust",
        decision_type="Architecture",
        maker="System",
        outcome_status="Pending",
        reversibility_score=0.5,
    )

    session.add_all([d1, d2, d3])
    session.commit()

    analytics = DecisionAnalytics(session)
    metrics = analytics.get_metrics()

    assert metrics["total_decisions"] == 3
    assert metrics["resolved_decisions"] == 2
    assert metrics["successes"] == 1
    assert metrics["failures"] == 1
    assert metrics["success_rate"] == 0.50
    assert metrics["highly_reversible_count"] == 1
    assert metrics["highly_irreversible_count"] == 1


def test_decision_patterns(session):
    now = datetime.now(timezone.utc)

    # Two failures with no evidence -> Repeated Mistake
    f1 = DecisionLedger(
        statement="Buy crypto",
        decision_type="Finance",
        maker="System",
        outcome_status="Failure",
        evidence=[],
    )
    f2 = DecisionLedger(
        statement="Skip testing",
        decision_type="Engineering",
        maker="System",
        outcome_status="Failure",
        evidence=[],
    )

    session.add_all([f1, f2])
    session.commit()

    detector = DecisionPatternDetector(session)
    patterns = detector.detect()

    assert len(patterns) == 2
    types = [p["pattern_type"] for p in patterns]
    assert "Repeated Mistake" in types
    assert "Decision Bias" in types


def test_decision_review(session):
    now = datetime.now(timezone.utc)

    # Old failure (should be excluded from 7 day review)
    d_old = DecisionLedger(
        statement="Old decision",
        decision_type="Test",
        maker="System",
        outcome_status="Failure",
        outcome_date=now - timedelta(days=10),
    )

    # Recent success
    d_recent = DecisionLedger(
        statement="Recent success",
        decision_type="Test",
        maker="System",
        outcome_status="Success",
        lessons_learned="Testing works",
        outcome_date=now - timedelta(days=2),
    )

    session.add_all([d_old, d_recent])
    session.commit()

    engine = DecisionReviewEngine(session)
    review = engine.generate_review(days_back=7)

    assert review["timeframe_days"] == 7
    # Old decision shouldn't be in insights
    assert len(review["insights"]["what_worked"]) == 1
    assert len(review["insights"]["what_failed"]) == 0
    assert "Testing works" in review["insights"]["what_worked"][0]
