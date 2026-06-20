from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from jay.db import get_session
from jay.engines.attention import AttentionEngine
from jay.engines.opportunity import OpportunityEngine
from jay.engines.relationship import RelationshipEngine
from jay.engines.risk import RiskEngine
from jay.engines.schemas import Opportunity, Priority, Relationship, Risk
from jay.leverage.schemas import LeverageRatio
from jay.leverage.service import LeverageService
from jay.memory.models import MemoryItem

router = APIRouter(prefix="/briefing", tags=["Briefing"])


class BriefingResponse(BaseModel):
    top_priorities: list[Priority]
    critical_risks: list[Risk]
    opportunity_queue: list[Opportunity]
    important_relationships: list[Relationship]
    leverage_summary: LeverageRatio
    open_commitments: list[dict]


@router.get("/morning", response_model=BriefingResponse)
@router.get("/evening", response_model=BriefingResponse)
@router.get("/weekly", response_model=BriefingResponse)
@router.get("/monthly", response_model=BriefingResponse)
def get_briefing(session: Session = Depends(get_session)):
    attention_engine = AttentionEngine(session)
    risk_engine = RiskEngine(session)
    opp_engine = OpportunityEngine(session)
    rel_engine = RelationshipEngine(session)
    leverage_service = LeverageService(session)

    # Calculate top priorities
    top_priorities = attention_engine.analyze()

    # Calculate critical risks (score > 0.6)
    all_risks = risk_engine.analyze()
    critical_risks = [r for r in all_risks if r.score > 0.6]

    # Opportunity queue
    all_opps = opp_engine.analyze()
    opp_queue = [o for o in all_opps if (o.impact_score * o.confidence_score) > 0.5]

    # Relationships (neglected or fading)
    all_rels = rel_engine.analyze()
    important_rels = [r for r in all_rels if r.status in ("neglected", "fading")]

    # Leverage
    leverage_summary = leverage_service.get_ratio()

    # Open commitments
    commitments = (
        session.query(MemoryItem).filter(MemoryItem.kind == "commitment").all()
    )
    open_commitments = [
        {"id": str(c.id), "title": c.title, "due": c.occurred_at}
        for c in commitments
        if "completed" not in [t.lower() for t in c.tags]
    ]

    return BriefingResponse(
        top_priorities=top_priorities,
        critical_risks=critical_risks,
        opportunity_queue=opp_queue,
        important_relationships=important_rels,
        leverage_summary=leverage_summary,
        open_commitments=open_commitments,
    )
