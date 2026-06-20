from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from jay.db import get_session
from jay.engines.models import ObservationLedger
from jay.engines.inference import ContextCorrelator
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/observation", tags=["Observation"])


class ObservationPayload(BaseModel):
    source: str
    payload: Dict[str, Any]


from jay.db import SessionLocal
from datetime import datetime, timezone, timedelta
from jay.engines.models import WorkSessionLedger


def get_or_create_active_session(session: Session) -> WorkSessionLedger:
    active_session = (
        session.query(WorkSessionLedger)
        .filter(WorkSessionLedger.status == "Active")
        .first()
    )
    now = datetime.now(timezone.utc)

    if active_session:
        last_obs = (
            session.query(ObservationLedger)
            .filter(ObservationLedger.session_id == active_session.id)
            .order_by(ObservationLedger.created_at.desc())
            .first()
        )

        if last_obs:
            # Need to ensure both are offset-aware or naive before comparing.
            # Assuming created_at is timezone-aware from UTC.
            last_created = last_obs.created_at
            if last_created.tzinfo is None:
                last_created = last_created.replace(tzinfo=timezone.utc)

            time_since_last = now - last_created
            if time_since_last > timedelta(minutes=30):
                active_session.status = "Completed"
                active_session.end_time = last_created

                new_session = WorkSessionLedger(start_time=now)
                session.add(new_session)
                session.flush()
                return new_session
        return active_session

    new_session = WorkSessionLedger(start_time=now)
    session.add(new_session)
    session.flush()
    return new_session


async def trigger_inference():
    with SessionLocal() as session:
        engine = ContextCorrelator(session)
        await engine.infer_outcomes()


def sanitize_payload(payload: dict) -> dict:
    import json
    import re
    payload_str = json.dumps(payload)
    payload_str = re.sub(r'(system:|user:|<\|.*?\|>|```)', '', payload_str, flags=re.IGNORECASE)
    try:
        return json.loads(payload_str)
    except Exception:
        return payload

@router.post("")
async def log_observation(
    data: ObservationPayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    active_sess = get_or_create_active_session(session)
    safe_payload = sanitize_payload(data.payload)
    obs = ObservationLedger(
        session_id=active_sess.id, source=data.source, payload=safe_payload
    )
    session.add(obs)
    session.commit()

    # Trigger background inference
    background_tasks.add_task(trigger_inference)
    return {"status": "received"}

@router.delete("/prune")
async def prune_observations(session: Session = Depends(get_session)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    result = session.query(ObservationLedger).filter(ObservationLedger.created_at < cutoff).delete()
    session.commit()
    return {"status": "success", "deleted_rows": result}


@router.get("/session")
async def get_active_session(session: Session = Depends(get_session)):
    active_sess = (
        session.query(WorkSessionLedger)
        .filter(WorkSessionLedger.status == "Active")
        .first()
    )
    if not active_sess:
        return {"session": None, "observations": []}

    obs = (
        session.query(ObservationLedger)
        .filter(ObservationLedger.session_id == active_sess.id)
        .order_by(ObservationLedger.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "session": {
            "id": str(active_sess.id),
            "start_time": active_sess.start_time.isoformat(),
            "status": active_sess.status,
            "session_summary": active_sess.session_summary,
        },
        "observations": [
            {
                "id": str(o.id),
                "source": o.source,
                "payload": o.payload,
                "created_at": o.created_at.isoformat(),
                "status": o.status,
            }
            for o in obs
        ],
    }
