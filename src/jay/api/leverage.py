from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from jay.db import get_session
from jay.leverage.schemas import LeverageLedgerCreate, LeverageLedgerRead, LeverageRatio
from jay.leverage.service import LeverageService

router = APIRouter(prefix="/leverage", tags=["Leverage"])


@router.post("/record", response_model=LeverageLedgerRead)
def record_leverage(
    data: LeverageLedgerCreate, session: Session = Depends(get_session)
):
    return LeverageService(session).record_leverage(data)


@router.get("/ratio", response_model=LeverageRatio)
def get_leverage_ratio(session: Session = Depends(get_session)):
    return LeverageService(session).get_ratio()
