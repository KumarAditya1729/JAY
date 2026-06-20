from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from jay.db import get_session
from jay.trust.models import TrustLedger
from jay.trust.schemas import TrustDashboardStats, TrustLedgerRead

router = APIRouter(prefix="/trust", tags=["Trust"])


@router.get("/ledger/{entity_type}/{entity_id}", response_model=list[TrustLedgerRead])
def get_trust_ledger(
    entity_type: str,
    entity_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[TrustLedger]:
    return (
        session.query(TrustLedger)
        .filter(
            TrustLedger.entity_type == entity_type, TrustLedger.entity_id == entity_id
        )
        .order_by(TrustLedger.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/dashboard", response_model=TrustDashboardStats)
def get_trust_dashboard(session: Session = Depends(get_session)) -> TrustDashboardStats:
    stats = session.query(
        func.count(TrustLedger.id).label("total_entries"),
        func.avg(TrustLedger.confidence_score).label("avg_confidence"),
        func.avg(TrustLedger.risk_score).label("avg_risk"),
        func.avg(TrustLedger.impact_score).label("avg_impact"),
        func.avg(TrustLedger.reversibility_score).label("avg_reversibility"),
        func.avg(TrustLedger.evidence_score).label("avg_evidence"),
    ).one_or_none()

    if not stats or stats.total_entries == 0:
        return TrustDashboardStats(
            total_entries=0,
            average_confidence=0.0,
            average_risk=0.0,
            average_impact=0.0,
            average_reversibility=0.0,
            average_evidence=0.0,
        )

    return TrustDashboardStats(
        total_entries=stats.total_entries,
        average_confidence=float(stats.avg_confidence),
        average_risk=float(stats.avg_risk),
        average_impact=float(stats.avg_impact),
        average_reversibility=float(stats.avg_reversibility),
        average_evidence=float(stats.avg_evidence),
    )
