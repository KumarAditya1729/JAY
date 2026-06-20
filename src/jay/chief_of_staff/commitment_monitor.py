from datetime import datetime, timezone
from sqlalchemy.orm import Session
from jay.memory.models import MemoryItem
from .schemas import OpenCommitment


class CommitmentMonitor:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> list[OpenCommitment]:
        commitments = []
        now = datetime.now(timezone.utc)

        items = (
            self.session.query(MemoryItem).filter(MemoryItem.kind == "commitment").all()
        )
        for item in items:
            if "completed" in [t.lower() for t in item.tags]:
                continue

            days_overdue = 0
            suggested_action = "Schedule time to complete."

            if item.occurred_at:
                occurred = (
                    item.occurred_at.replace(tzinfo=timezone.utc)
                    if item.occurred_at.tzinfo is None
                    else item.occurred_at
                )
                if occurred < now:
                    days_overdue = (now - occurred).days
                    suggested_action = "Follow up or renegotiate deadline."

            # Simple heuristic for missing dates
            if days_overdue == 0 and item.importance > 3:
                suggested_action = "High importance. Needs deadline."

            commitments.append(
                OpenCommitment(
                    commitment=item.title,
                    owner="Founder",
                    days_overdue=days_overdue,
                    suggested_action=suggested_action,
                )
            )

        return sorted(commitments, key=lambda x: x.days_overdue, reverse=True)
