from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from jay.db import get_session
from .service import ChiefOfStaffService
from .schemas import CommandCenterResponse

router = APIRouter(prefix="/chief-of-staff", tags=["Chief of Staff"])

@router.get("/command-center", response_model=CommandCenterResponse)
def get_command_center(db: Session = Depends(get_session)):
    service = ChiefOfStaffService(db)
    return service.generate_command_center()
