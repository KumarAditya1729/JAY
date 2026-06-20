from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
import json
from jay.engines.observation_router import ObservationRouter

router = APIRouter(prefix="/reality", tags=["Reality Engine"])

class WebhookPayload(BaseModel):
    source: str
    event_type: str
    data: dict

@router.post("/webhook")
async def reality_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Ingests external events directly into JAY's Hybrid Memory OS.
    Examples: Stripe Payments, GitHub Commits, Vercel Deployments.
    """
    raw_text = f"Event: {payload.event_type} | Data: {json.dumps(payload.data)}"
    
    # Process asynchronously so we don't block the external webhook sender
    background_tasks.add_task(
        ObservationRouter.route_observation,
        source=payload.source,
        raw_text=raw_text
    )
    
    return {"status": "received", "reality_sync": "queued"}
