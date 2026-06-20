from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import subprocess
from datetime import datetime, timezone

from jay.db import get_session
from jay.engines.models import ExecutionLedger

router = APIRouter(prefix="/execution", tags=["Execution Ledger"])


@router.get("/pending")
def list_pending(session: Session = Depends(get_session)):
    return (
        session.query(ExecutionLedger).filter(ExecutionLedger.status == "PENDING").all()
    )


@router.post("/{execution_id}/approve")
def approve_execution(execution_id: str, session: Session = Depends(get_session)):
    ledger = (
        session.query(ExecutionLedger)
        .filter(ExecutionLedger.id == execution_id)
        .first()
    )
    if not ledger:
        raise HTTPException(status_code=404, detail="Execution not found")

    if ledger.status != "PENDING":
        raise HTTPException(status_code=400, detail="Execution is not pending")

    try:
        result = subprocess.run(
            ledger.command, shell=True, text=True, capture_output=True, timeout=30
        )
        ledger.stdout = result.stdout
        ledger.stderr = result.stderr
        ledger.status = "EXECUTED" if result.returncode == 0 else "FAILED"
    except Exception as e:
        ledger.stderr = str(e)
        ledger.status = "FAILED"

    ledger.executed_at = datetime.now(timezone.utc)
    session.commit()
    return ledger


@router.post("/{execution_id}/reject")
def reject_execution(execution_id: str, session: Session = Depends(get_session)):
    ledger = (
        session.query(ExecutionLedger)
        .filter(ExecutionLedger.id == execution_id)
        .first()
    )
    if not ledger:
        raise HTTPException(status_code=404, detail="Execution not found")

    if ledger.status != "PENDING":
        raise HTTPException(status_code=400, detail="Execution is not pending")

    ledger.status = "REJECTED"
    session.commit()
    return ledger
