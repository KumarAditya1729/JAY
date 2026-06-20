import logging
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid
import tempfile

from fastapi import UploadFile
from jay.memory.models import EventLog, MemoryItem, ExtractionAudit
from .parsers import FileParser
from .extraction import MemoryExtractor

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, session: Session):
        self.session = session
        self.extractor = MemoryExtractor()

    async def process_upload(self, file: UploadFile) -> dict:
        """Processes an uploaded file, extracts memory, and logs to EventLog."""
        # Save temp file
        ext = Path(file.filename).suffix
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        try:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            temp_file.close()

            # Parse
            text = FileParser.parse_file(temp_file.name)

            # Log File Ingested Event
            ingest_event = EventLog(
                stream_id=f"import-{uuid.uuid4()}",
                event_type="FileIngested",
                actor_id="founder",
                payload={
                    "filename": file.filename,
                    "size": len(content),
                    "text_length": len(text),
                },
            )
            self.session.add(ingest_event)

            # Extract
            extracted_items = await self.extractor.extract_memories(
                text, source=file.filename
            )

            created_count = 0
            review_count = 0

            for item in extracted_items:
                event_type = "MemoryExtracted"
                mem_id = str(uuid.uuid4())
                status = "APPROVED"

                if item["confidence"] < 0.7:
                    event_type = "MemoryExtractionReviewRequired"
                    status = "PENDING"
                    review_count += 1
                else:
                    created_count += 1
                    # Also project directly to MemoryItem for high confidence
                    mem = MemoryItem(
                        id=mem_id,
                        kind=item["kind"],
                        title=item["title"],
                        body=item["body"],
                        source=item["source"],
                        importance=item["importance"],
                        confidence=item["confidence"],
                        tags=item["tags"],
                        occurred_at=datetime.now(timezone.utc),
                    )
                    self.session.add(mem)

                item["memory_id"] = mem_id  # Store the intended memory ID in payload

                memory_event = EventLog(
                    stream_id=ingest_event.stream_id,
                    event_type=event_type,
                    actor_id="jay-import-engine",
                    payload=item,
                )
                self.session.add(memory_event)

                # Create Audit Record
                audit = ExtractionAudit(
                    memory_id=mem_id,
                    source_file=item.get("source", "unknown"),
                    model_used="llama3",  # TODO: Get from extractor dynamically
                    prompt_version="v1.0",
                    confidence=item["confidence"],
                    status=status,
                )
                self.session.add(audit)

            self.session.commit()

            return {
                "status": "success",
                "filename": file.filename,
                "extracted_count": len(extracted_items),
                "high_confidence_created": created_count,
                "pending_reviews": review_count,
            }

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to process upload {file.filename}: {e}")
            raise
        finally:
            Path(temp_file.name).unlink(missing_ok=True)
