from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import uuid

from jay.db import get_session
from jay.engines.models import ExecutionLedger, OutcomeLedger

router = APIRouter(prefix="/outcomes", tags=["Outcomes"])


class OutcomePayload(BaseModel):
    execution_id: str
    recommendation_id: str = None
    recommendation_text: str = ""
    status: str
    outcome: str
    domain: str
    failure_reason: str = None
    impact_score: float
    hours_saved: float
    hours_invested: float


@router.post("/log")
def log_outcome(data: OutcomePayload, session: Session = Depends(get_session)):
    # Calculate leverage
    leverage = 0.0
    if data.hours_invested > 0:
        leverage = (data.impact_score * data.hours_saved) / data.hours_invested
    else:
        leverage = data.impact_score * data.hours_saved

    outcome_record = OutcomeLedger(
        execution_id=uuid.UUID(data.execution_id),
        recommendation_id=(
            uuid.UUID(data.recommendation_id) if data.recommendation_id else None
        ),
        recommendation_text=data.recommendation_text,
        status=data.status,
        outcome=data.outcome,
        domain=data.domain,
        failure_reason=data.failure_reason,
        impact_score=data.impact_score,
        hours_saved=data.hours_saved,
        hours_invested=data.hours_invested,
        leverage_generated=leverage,
    )
    session.add(outcome_record)
    session.commit()

    return {"status": "logged", "leverage_generated": leverage}


@router.get("/metrics")
def get_metrics(session: Session = Depends(get_session)):
    count = session.query(OutcomeLedger).count()
    if count == 0:
        return {
            "total_outcomes": 0,
            "founder_leverage_ratio": 0.0,
            "total_hours_saved": 0.0,
            "avg_impact": 0.0,
        }

    avg_leverage = (
        session.query(func.avg(OutcomeLedger.leverage_generated)).scalar() or 0.0
    )
    total_saved = session.query(func.sum(OutcomeLedger.hours_saved)).scalar() or 0.0
    avg_impact = session.query(func.avg(OutcomeLedger.impact_score)).scalar() or 0.0

    return {
        "total_outcomes": count,
        "founder_leverage_ratio": round(float(avg_leverage), 2),
        "total_hours_saved": round(float(total_saved), 2),
        "avg_impact": round(float(avg_impact), 2),
    }


@router.get("/pending")
def get_pending_outcomes(session: Session = Depends(get_session)):
    """Returns executions that have finished but have no outcome logged."""
    # Find executions that are EXECUTED or FAILED
    executions = (
        session.query(ExecutionLedger)
        .filter(ExecutionLedger.status.in_(["EXECUTED", "FAILED"]))
        .all()
    )

    # Filter out ones that already have an outcome
    # In a real app, use a left join or NOT EXISTS query for efficiency
    outcomes = session.query(OutcomeLedger.execution_id).all()
    outcome_exec_ids = {str(o[0]) for o in outcomes}

    pending = []
    for ex in executions:
        if str(ex.id) not in outcome_exec_ids:
            pending.append(
                {
                    "id": str(ex.id),
                    "command": ex.command,
                    "status": ex.status,
                    "executed_at": ex.executed_at,
                    "stdout": ex.stdout,
                    "stderr": ex.stderr,
                }
            )

    return pending


@router.get("/inferred")
def get_inferred_outcomes(session: Session = Depends(get_session)):
    outcomes = (
        session.query(OutcomeLedger).filter(OutcomeLedger.status == "INFERRED").all()
    )
    return [
        {
            "id": str(o.id),
            "recommendation_text": o.recommendation_text,
            "outcome": o.outcome,
            "impact_score": o.impact_score,
        }
        for o in outcomes
    ]


class ConfirmPayload(BaseModel):
    outcome_id: str
    status: str


@router.post("/confirm")
def confirm_outcome(data: ConfirmPayload, session: Session = Depends(get_session)):
    outcome = (
        session.query(OutcomeLedger).filter(OutcomeLedger.id == data.outcome_id).first()
    )
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    if data.status == "REJECTED":
        # If rejected, we can delete the inferred outcome so the task returns to pending
        session.delete(outcome)
    else:
        outcome.status = data.status
    session.commit()
    return {"status": "processed"}
