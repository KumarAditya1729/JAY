import logging
from github import Github
from github.GithubException import GithubException

from jay.config import get_settings
from .extraction import MemoryExtractor
from jay.memory.models import (
    EventLog,
    MemoryItem,
    ExtractionAudit,
    ConnectorAuditLedger,
)
from jay.engines.models import FounderActivityLedger
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class GithubIngestor:
    def __init__(self, session: Session):
        self.settings = get_settings()
        self.session = session
        self.extractor = MemoryExtractor()

        if not self.settings.github_token:
            raise ValueError("GITHUB_TOKEN is not configured.")

        self.gh = Github(self.settings.github_token)

    async def sync_repository(self, repo_name: str) -> dict:
        try:
            repo = self.gh.get_repo(repo_name)
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)
            seven_days_ago = now - timedelta(days=7)
            fourteen_days_ago = now - timedelta(days=14)

            # 1. Fetch Data
            commits = list(repo.get_commits(since=thirty_days_ago))
            issues_and_prs = list(repo.get_issues(state="all", since=thirty_days_ago))
            milestones = list(repo.get_milestones(state="all"))

            # Separate issues and PRs (GitHub API returns PRs as issues)
            issues = [i for i in issues_and_prs if not i.pull_request]
            prs = [i for i in issues_and_prs if i.pull_request]

            # 2. Calculate Velocity
            closed_last_7 = 0
            closed_prev_7 = 0

            for item in issues_and_prs:
                if item.state == "closed" and item.closed_at:
                    closed_at = item.closed_at.replace(tzinfo=timezone.utc)
                    if closed_at >= seven_days_ago:
                        closed_last_7 += 1
                    elif closed_at >= fourteen_days_ago:
                        closed_prev_7 += 1

            velocity_score = 1.0
            if closed_prev_7 > 0:
                velocity_score = closed_last_7 / closed_prev_7
            elif closed_last_7 > 0:
                velocity_score = 2.0  # Significant increase from 0

            momentum = (
                "Accelerating"
                if velocity_score > 1.2
                else "Slowing" if velocity_score < 0.8 else "Stable"
            )

            # 3. Format Payload
            text_payload = f"FOUNDER ACTIVITY GRAPH - REPOSITORY: {repo_name}\n"
            text_payload += (
                f"VELOCITY SCORE: {velocity_score:.2f} (7-day trend: {momentum})\n"
            )
            text_payload += f"Closed in last 7 days: {closed_last_7} | Previous 7 days: {closed_prev_7}\n\n"

            text_payload += "PROJECT PROGRESS (Milestones):\n"
            for m in milestones:
                text_payload += f"- [{m.state.upper()}] {m.title} - {m.closed_issues}/{m.open_issues + m.closed_issues} issues\n"

            text_payload += "\nDECISION SIGNALS (Recent PRs & Issues):\n"
            for item in issues_and_prs[:20]:  # Top 20 for context limit
                type_str = "PR" if item.pull_request else "ISSUE"
                text_payload += f"- [{type_str} #{item.number}] {item.title} (State: {item.state})\n"
                if item.body:
                    body_preview = item.body[:150].replace("\n", " ") + "..."
                    text_payload += f"  Context: {body_preview}\n"

            text_payload += "\nEXECUTION EVENTS (Recent Commits):\n"
            for commit in commits[:30]:  # Top 30
                text_payload += f"- [{commit.sha[:7]}] {commit.commit.message}\n"

            # Log ingest event
            ingest_event = EventLog(
                stream_id=f"import-github-{uuid.uuid4()}",
                event_type="GithubSyncCompleted",
                actor_id="founder",
                payload={
                    "repo_name": repo_name,
                    "commits_fetched": len(commits),
                    "prs_fetched": len(prs),
                    "issues_fetched": len(issues),
                    "velocity": velocity_score,
                },
            )
            self.session.add(ingest_event)

            # Extract memories
            source = f"github:{repo_name}"
            extracted_items = await self.extractor.extract_memories(
                text_payload, source=source
            )

            created_count = 0
            review_count = 0
            total_confidence = 0.0

            for item in extracted_items:
                event_type = "MemoryExtracted"
                mem_id = str(uuid.uuid4())
                status = "APPROVED"
                total_confidence += item["confidence"]

                if item["confidence"] < 0.7:
                    event_type = "MemoryExtractionReviewRequired"
                    status = "PENDING"
                    review_count += 1
                else:
                    created_count += 1
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

                item["memory_id"] = mem_id

                memory_event = EventLog(
                    stream_id=ingest_event.stream_id,
                    event_type=event_type,
                    actor_id="jay-import-engine",
                    payload=item,
                )
                self.session.add(memory_event)

                audit = ExtractionAudit(
                    memory_id=mem_id,
                    source_file=source,
                    model_used="llama3",
                    prompt_version="v1.1-github",
                    confidence=item["confidence"],
                    status=status,
                )
                self.session.add(audit)

            # 4. Create Connector Audit Ledger Record
            total_items = created_count + review_count
            avg_conf = (
                total_confidence / len(extracted_items) if extracted_items else 0.0
            )
            manual_review_rate = (
                (review_count / total_items) if total_items > 0 else 0.0
            )

            connector_audit = ConnectorAuditLedger(
                source="github",
                items_imported=created_count,
                items_rejected=review_count,
                average_confidence=avg_conf,
                processing_version="v1.1-github",
                status="SUCCESS" if len(extracted_items) > 0 else "PARTIAL",
                error_log=None,
                manual_review_rate=manual_review_rate,
                false_positive_rate=0.0,
                correction_rate=0.0,
            )
            self.session.add(connector_audit)

            # 5. Create Founder Activity Ledger Record
            activity_record = FounderActivityLedger(
                date_recorded=now,
                commits_count=len(commits),
                issues_closed=closed_last_7,  # Simplified approximation for MVP
                prs_closed=len([p for p in prs if p.state == "closed"]),
                repositories_active=1,
                activity_score=float(len(commits) * 0.5 + len(issues_and_prs) * 1.0),
                progress_score=float(closed_last_7 * 2.0),
                impact_score=0.0,  # Will be filled by intelligence engine correlations later
                velocity_trend=momentum,
            )
            self.session.add(activity_record)

            self.session.commit()

            return {
                "status": "success",
                "repo": repo_name,
                "velocity_score": round(velocity_score, 2),
                "momentum": momentum,
                "extracted_count": len(extracted_items),
                "high_confidence_created": created_count,
                "pending_reviews": review_count,
            }

        except GithubException as e:
            self.session.rollback()
            logger.error(f"GitHub API Error: {e}")
            # Log failure to Connector Audit
            connector_audit = ConnectorAuditLedger(
                source="github",
                items_imported=0,
                items_rejected=0,
                average_confidence=0.0,
                processing_version="v1.1-github",
                status="FAILED",
                error_log=f"GitHub API Error: {e.data.get('message', str(e))}",
            )
            self.session.add(connector_audit)
            self.session.commit()
            raise ValueError(f"GitHub API Error: {e.data.get('message', str(e))}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to sync github repo {repo_name}: {e}")
            connector_audit = ConnectorAuditLedger(
                source="github",
                items_imported=0,
                items_rejected=0,
                average_confidence=0.0,
                processing_version="v1.1-github",
                status="FAILED",
                error_log=str(e),
            )
            self.session.add(connector_audit)
            self.session.commit()
            raise
