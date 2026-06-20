from fastapi import Depends, FastAPI, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from jay.db import Base, engine, get_session
from jay.memory.models import EventLog, MemoryItem
from jay.memory.schemas import MemoryCreate, MemoryRead, SearchResult
from jay.memory.service import MemoryService

from jay.api.trust import router as trust_router
from jay.api.intent import router as intent_router
from jay.api.leverage import router as leverage_router
from jay.api.briefing import router as briefing_router
from jay.decisions.api import router as decisions_router
from jay.founder.api import router as founder_router
from jay.chief_of_staff.router import router as chief_of_staff_router
from jay.api.voice import router as voice_router
from jay.api.auth import verify_api_key
from jay.api.execution import router as execution_router
from jay.api.ingestion import router as ingestion_router
from jay.api.outcomes import router as outcomes_router
from jay.api.observation import router as observation_router
from jay.api.attention import router as attention_router
from jay.engines.reality.ingestion import router as reality_router

# Import models to ensure they are registered with Base metadata

app = FastAPI(
    title="JAY Memory Core",
    description="Local-first memory foundation for Joint Artificial You.",
    version="0.1.0",
    dependencies=[Depends(verify_api_key)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trust_router)
app.include_router(intent_router)
app.include_router(leverage_router)
app.include_router(briefing_router)
app.include_router(decisions_router)
app.include_router(founder_router)
app.include_router(chief_of_staff_router)
app.include_router(voice_router)
app.include_router(execution_router)
app.include_router(ingestion_router)
app.include_router(outcomes_router)
app.include_router(observation_router)
app.include_router(attention_router)
app.include_router(reality_router)


@app.on_event("startup")
def ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "system": "jay-memory-core"}


@app.post("/memory", response_model=MemoryRead)
def record_memory(
    memory: MemoryCreate, session: Session = Depends(get_session)
) -> MemoryItem:
    return MemoryService(session).record(memory)


@app.get("/memory/timeline", response_model=list[MemoryRead])
def memory_timeline(
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[MemoryItem]:
    return MemoryService(session).list_timeline(limit=limit)


@app.get("/memory/search", response_model=list[SearchResult])
def search_memory(
    q: str = Query(default=""),
    limit: int = Query(default=10, ge=1, le=50),
    session: Session = Depends(get_session),
) -> list[SearchResult]:
    items = MemoryService(session).search(q, limit=limit)
    reason = "timeline fallback" if not q.strip() else "title/body lexical match"
    return [{"item": item, "reason": reason} for item in items]


@app.get("/audit/events")
def audit_events(
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[dict]:
    rows = (
        session.query(EventLog).order_by(EventLog.occurred_at.desc()).limit(limit).all()
    )
    return [
        {
            "id": str(row.id),
            "stream_id": row.stream_id,
            "event_type": row.event_type,
            "actor_id": row.actor_id,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "occurred_at": row.occurred_at.isoformat(),
            "payload": row.payload,
            "trust": row.trust,
            "metadata": row.event_metadata,
        }
        for row in rows
    ]

from pydantic import BaseModel
class MissionPayload(BaseModel):
    task_description: str

@app.post("/missions/deploy")
async def deploy_mission(payload: MissionPayload):
    from jay.engines.execution import ExecutionEngine
    engine = ExecutionEngine()
    result = await engine.delegate_task(payload.task_description)
    return {"status": "deployed", "result": result}
