from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from jay.db import get_session
from jay.founder.models import BehaviorLedger, FounderProfile, PreferenceEdge
from jay.founder.schemas import (
    BehaviorCreate,
    BehaviorResponse,
    FounderProfileResponse,
    FounderProfileUpdate,
    PreferenceEdgeResponse,
)
from jay.founder.service import FounderService
from jay.founder.engines.preference import PreferenceEngine
from jay.founder.engines.decision_style import DecisionStyleEngine
from jay.founder.engines.prioritization import PrioritizationEngine
from jay.founder.engines.consistency import ConsistencyEngine
from jay.intent.models import IntentNode

router = APIRouter(prefix="/founder", tags=["Founder Model"])


@router.get("/profile", response_model=FounderProfileResponse)
def get_profile(session: Session = Depends(get_session)):
    profile = (
        session.query(FounderProfile).filter(FounderProfile.id == "default").first()
    )
    if not profile:
        profile = FounderProfile(id="default")
        session.add(profile)
        session.commit()

    intent_nodes = session.query(IntentNode).filter(IntentNode.status == "active").all()

    response_dict = {
        "id": profile.id,
        "risk_tolerance": profile.risk_tolerance,
        "time_horizon": profile.time_horizon,
        "decision_style": profile.decision_style,
        "communication_style": profile.communication_style,
        "leadership_style": profile.leadership_style,
        "learning_style": profile.learning_style,
        "mission": [
            {"id": n.id, "title": n.title}
            for n in intent_nodes
            if n.node_type == "mission"
        ],
        "values": [
            {"id": n.id, "title": n.title}
            for n in intent_nodes
            if n.node_type == "value"
        ],
        "goals": [
            {"id": n.id, "title": n.title}
            for n in intent_nodes
            if n.node_type == "goal"
        ],
        "non_negotiables": [
            {"id": n.id, "title": n.title}
            for n in intent_nodes
            if n.node_type == "non_negotiable"
        ],
    }
    return response_dict


@router.patch("/profile", response_model=FounderProfileResponse)
def update_profile(
    update: FounderProfileUpdate, session: Session = Depends(get_session)
):
    service = FounderService(session)
    service.update_profile(update, actor_id="system")
    return get_profile(session)


@router.post("/behavior", response_model=BehaviorResponse)
def record_behavior(behavior: BehaviorCreate, session: Session = Depends(get_session)):
    service = FounderService(session)
    resp = service.record_behavior(behavior, actor_id="system")
    # Dynamically update preference graph
    PreferenceEngine(session).generate_graph()
    return resp


@router.get("/behavior", response_model=list[BehaviorResponse])
def list_behavior(session: Session = Depends(get_session)):
    return (
        session.query(BehaviorLedger).order_by(BehaviorLedger.occurred_at.desc()).all()
    )


@router.get("/preferences", response_model=list[PreferenceEdgeResponse])
def get_preferences(session: Session = Depends(get_session)):
    return session.query(PreferenceEdge).order_by(PreferenceEdge.weight.desc()).all()


@router.get("/decision-style")
def get_decision_style(session: Session = Depends(get_session)):
    engine = DecisionStyleEngine(session)
    return engine.analyze()


@router.get("/priorities")
def get_priorities(session: Session = Depends(get_session)):
    engine = PrioritizationEngine(session)
    return engine.analyze()


@router.get("/consistency")
def get_consistency(session: Session = Depends(get_session)):
    engine = ConsistencyEngine(session)
    return engine.analyze()
