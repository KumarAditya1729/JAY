from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from jay.db import get_session
from .service import ChiefOfStaffService
from .schemas import CommandCenterResponse

router = APIRouter(prefix="/chief-of-staff", tags=["Chief of Staff"])


@router.get("/command-center", response_model=CommandCenterResponse)
async def get_command_center(session: Session = Depends(get_session)):
    service = ChiefOfStaffService(session)
    return await service.generate_command_center()


@router.get("/recommendations/{rec_id}/audit")
def get_recommendation_audit(rec_id: str, session: Session = Depends(get_session)):
    from jay.engines.models import RecommendationLedger
    from fastapi import HTTPException
    import uuid

    try:
        uid = uuid.UUID(rec_id)
        rec = (
            session.query(RecommendationLedger)
            .filter(RecommendationLedger.id == uid)
            .first()
        )
        if not rec:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        return {
            "statement": rec.statement,
            "impact_score": rec.impact_score,
            "urgency_score": rec.urgency_score,
            "intent_alignment_score": rec.intent_alignment_score,
            "trust_score": rec.trust_score,
            "reversibility_score": rec.reversibility_score,
            "final_score": rec.final_score,
            "llm_explanation": rec.llm_explanation,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
