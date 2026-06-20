from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from jay.db import get_session
from jay.decisions.models import DecisionLedger
from jay.decisions.schemas import DecisionCreate, DecisionOutcome, DecisionResponse
from jay.decisions.service import DecisionService
from jay.decisions.review import DecisionReviewEngine

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post("", response_model=DecisionResponse)
def record_decision(decision: DecisionCreate, session: Session = Depends(get_session)):
    service = DecisionService(session)
    return service.record_decision(decision, actor_id="system")


@router.get("", response_model=list[DecisionResponse])
def list_decisions(session: Session = Depends(get_session)):
    return (
        session.query(DecisionLedger)
        .order_by(DecisionLedger.decision_date.desc())
        .all()
    )


@router.get("/timeline", response_model=list[DecisionResponse])
def decision_timeline(session: Session = Depends(get_session)):
    return (
        session.query(DecisionLedger).order_by(DecisionLedger.decision_date.asc()).all()
    )


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(decision_id: str, session: Session = Depends(get_session)):
    decision = (
        session.query(DecisionLedger).filter(DecisionLedger.id == decision_id).first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.patch("/{decision_id}/outcome", response_model=DecisionResponse)
def record_outcome(
    decision_id: str, outcome: DecisionOutcome, session: Session = Depends(get_session)
):
    service = DecisionService(session)
    decision = (
        session.query(DecisionLedger).filter(DecisionLedger.id == decision_id).first()
    )
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return service.record_outcome(decision_id, outcome, actor_id="system")


@router.get("/review/weekly")
def review_weekly(session: Session = Depends(get_session)):
    engine = DecisionReviewEngine(session)
    return engine.generate_review(days_back=7)


@router.get("/review/monthly")
def review_monthly(session: Session = Depends(get_session)):
    engine = DecisionReviewEngine(session)
    return engine.generate_review(days_back=30)


@router.get("/review/quarterly")
def review_quarterly(session: Session = Depends(get_session)):
    engine = DecisionReviewEngine(session)
    return engine.generate_review(days_back=90)
