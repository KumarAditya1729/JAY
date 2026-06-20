from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from jay.decisions.analytics import DecisionAnalytics
from jay.decisions.models import DecisionLedger
from jay.decisions.patterns import DecisionPatternDetector


class DecisionReviewEngine:
    def __init__(self, session: Session):
        self.session = session
        self.analytics = DecisionAnalytics(session)
        self.patterns = DecisionPatternDetector(session)

    def generate_review(self, days_back: int) -> dict:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days_back)

        recent_decisions = (
            self.session.query(DecisionLedger)
            .filter(DecisionLedger.outcome_date != None)
            .filter(DecisionLedger.outcome_date >= cutoff)
            .all()
        )

        worked = [d for d in recent_decisions if d.outcome_status == "Success"]
        failed = [d for d in recent_decisions if d.outcome_status == "Failure"]

        metrics = self.analytics.get_metrics()
        detected_patterns = self.patterns.detect()

        what_worked = [
            f"Decision '{d.statement}' succeeded. Lesson: {d.lessons_learned or 'None'}"
            for d in worked
        ]
        what_failed = [
            f"Decision '{d.statement}' failed. Lesson: {d.lessons_learned or 'None'}"
            for d in failed
        ]
        what_should_change = [
            p["description"]
            for p in detected_patterns
            if p["severity"] in ("Medium", "High")
        ]

        if not what_should_change:
            what_should_change.append("No critical pattern changes detected.")

        return {
            "timeframe_days": days_back,
            "metrics": metrics,
            "insights": {
                "what_worked": what_worked,
                "what_failed": what_failed,
                "what_should_change": what_should_change,
            },
        }
