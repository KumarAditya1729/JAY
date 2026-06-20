import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from jay.db import get_session
from jay.memory.models import EventLog, MemoryItem, ExtractionAudit
from jay.import_engine.service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), session: Session = Depends(get_session)
):
    service = IngestionService(session)
    result = await service.process_upload(file)
    return result


class GithubSyncPayload(BaseModel):
    repo_name: str


@router.post("/github/sync")
async def sync_github(data: GithubSyncPayload, session: Session = Depends(get_session)):
    try:
        from jay.import_engine.github import GithubIngestor

        ingestor = GithubIngestor(session)
        result = await ingestor.sync_repository(data.repo_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during sync")


@router.get("/status")
def get_status(session: Session = Depends(get_session)):
    files = (
        session.query(EventLog).filter(EventLog.event_type == "FileIngested").count()
    )
    memories = (
        session.query(EventLog).filter(EventLog.event_type == "MemoryExtracted").count()
    )
    reviews = (
        session.query(EventLog)
        .filter(EventLog.event_type == "MemoryExtractionReviewRequired")
        .count()
    )

    return {
        "files_ingested": files,
        "memories_created": memories,
        "pending_reviews": reviews,
    }


@router.get("/pending-reviews")
def get_pending_reviews(session: Session = Depends(get_session)):
    events = (
        session.query(EventLog)
        .filter(EventLog.event_type == "MemoryExtractionReviewRequired")
        .order_by(EventLog.occurred_at.desc())
        .all()
    )

    return [
        {"id": str(e.id), "payload": e.payload, "occurred_at": e.occurred_at}
        for e in events
    ]


@router.post("/reviews/{event_id}/approve")
def approve_review(event_id: str, session: Session = Depends(get_session)):
    event = session.query(EventLog).filter(EventLog.id == event_id).first()
    if not event or event.event_type != "MemoryExtractionReviewRequired":
        raise HTTPException(
            status_code=404, detail="Review event not found or not pending."
        )

    payload = event.payload
    mem_id = payload.get("memory_id", str(uuid.uuid4()))

    # Project to MemoryItem
    mem = MemoryItem(
        id=mem_id,
        kind=payload.get("kind", "idea"),
        title=payload.get("title", "Approved Item"),
        body=payload.get("body", ""),
        source=payload.get("source", "manual-approval"),
        importance=payload.get("importance", 3),
        confidence=payload.get("confidence", 1.0),  # Human approved, so 1.0
        tags=payload.get("tags", []),
        occurred_at=datetime.now(timezone.utc),
    )
    session.add(mem)

    # Update event
    event.event_type = "MemoryExtracted"
    event.payload["approved_by"] = "founder"

    # Update audit
    audit = (
        session.query(ExtractionAudit)
        .filter(ExtractionAudit.memory_id == mem_id)
        .first()
    )
    if audit:
        audit.status = "APPROVED"

    session.commit()
    return {"status": "approved", "memory_id": mem.id}


@router.post("/reviews/{event_id}/reject")
def reject_review(event_id: str, session: Session = Depends(get_session)):
    event = session.query(EventLog).filter(EventLog.id == event_id).first()
    if not event or event.event_type != "MemoryExtractionReviewRequired":
        raise HTTPException(status_code=404, detail="Review event not found.")

    payload = event.payload
    mem_id = payload.get("memory_id", "")

    # We do not create a MemoryItem. We update the event to indicate rejection.
    event.event_type = "MemoryExtractionRejected"

    audit = (
        session.query(ExtractionAudit)
        .filter(ExtractionAudit.memory_id == mem_id)
        .first()
    )
    if audit:
        audit.status = "REJECTED"

    session.commit()
    return {"status": "rejected"}


class EditReviewPayload(BaseModel):
    title: str
    body: str
    kind: str
    importance: int


@router.put("/reviews/{event_id}/edit")
def edit_review(
    event_id: str, data: EditReviewPayload, session: Session = Depends(get_session)
):
    event = session.query(EventLog).filter(EventLog.id == event_id).first()
    if not event or event.event_type != "MemoryExtractionReviewRequired":
        raise HTTPException(status_code=404, detail="Review event not found.")

    # Update event payload inline
    payload = event.payload
    payload["title"] = data.title
    payload["body"] = data.body
    payload["kind"] = data.kind
    payload["importance"] = data.importance

    mem_id = payload.get("memory_id", str(uuid.uuid4()))
    payload["memory_id"] = mem_id

    # Project to MemoryItem immediately since it's edited (and essentially approved)
    mem = MemoryItem(
        id=mem_id,
        kind=data.kind,
        title=data.title,
        body=data.body,
        source=payload.get("source", "manual-edit"),
        importance=data.importance,
        confidence=1.0,
        tags=payload.get("tags", []),
        occurred_at=datetime.now(timezone.utc),
    )
    session.add(mem)

    event.event_type = "MemoryExtracted"

    audit = (
        session.query(ExtractionAudit)
        .filter(ExtractionAudit.memory_id == mem_id)
        .first()
    )
    if audit:
        audit.status = "EDITED"

    session.commit()
    return {"status": "edited", "memory_id": mem.id}


@router.get("/accuracy")
def get_accuracy(session: Session = Depends(get_session)):
    total = session.query(ExtractionAudit).count()
    if total == 0:
        return {
            "total": 0,
            "approved_pct": 0,
            "rejected_pct": 0,
            "edited_pct": 0,
            "avg_confidence": 0,
        }

    approved = (
        session.query(ExtractionAudit)
        .filter(ExtractionAudit.status == "APPROVED")
        .count()
    )
    rejected = (
        session.query(ExtractionAudit)
        .filter(ExtractionAudit.status == "REJECTED")
        .count()
    )
    edited = (
        session.query(ExtractionAudit)
        .filter(ExtractionAudit.status == "EDITED")
        .count()
    )

    avg_conf = session.query(func.avg(ExtractionAudit.confidence)).scalar() or 0.0

    return {
        "total": total,
        "approved_pct": round((approved / total) * 100, 1),
        "rejected_pct": round((rejected / total) * 100, 1),
        "edited_pct": round((edited / total) * 100, 1),
        "avg_confidence": round(float(avg_conf), 2),
    }


@router.get("/connectors/audit")
def get_connector_audits(session: Session = Depends(get_session)):
    from jay.memory.models import ConnectorAuditLedger

    audits = (
        session.query(ConnectorAuditLedger)
        .order_by(ConnectorAuditLedger.imported_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": str(a.id),
            "source": a.source,
            "imported_at": a.imported_at,
            "items_imported": a.items_imported,
            "items_rejected": a.items_rejected,
            "average_confidence": round(float(a.average_confidence), 2),
            "manual_review_rate": round(float(a.manual_review_rate), 2),
            "false_positive_rate": round(float(a.false_positive_rate), 2),
            "correction_rate": round(float(a.correction_rate), 2),
            "processing_version": a.processing_version,
            "status": a.status,
            "error_log": a.error_log,
        }
        for a in audits
    ]
