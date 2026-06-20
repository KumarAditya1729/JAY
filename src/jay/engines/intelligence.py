from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from jay.engines.models import FounderActivityLedger, OutcomeLedger


class IntelligenceEngine:
    def __init__(self, session: Session):
        self.session = session

    def generate_founder_intelligence(self) -> dict:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # 1. Fetch Activity Ledger History
        activity_logs = (
            self.session.query(FounderActivityLedger)
            .order_by(FounderActivityLedger.date_recorded.desc())
            .limit(14)
            .all()
        )

        if not activity_logs:
            # Fallback if no ledger data yet
            return {
                "activity_score": 0.0,
                "progress_score": 0.0,
                "impact_score": 0.0,
                "warnings": [
                    "No Founder Activity Ledger data found. Sync GitHub to begin tracking."
                ],
                "hotspots": [],
            }

        latest = activity_logs[0]

        # 2. Compute Stagnation / Momentum Warnings
        warnings = []
        if latest.velocity_trend == "Slowing":
            warnings.append(
                "Stagnation Warning: Velocity is slowing. You closed fewer items this week than last."
            )

        if (
            latest.commits_count > 20
            and latest.prs_closed == 0
            and latest.issues_closed == 0
        ):
            warnings.append(
                "High Effort, Low Yield: You have a high commit volume but no completed PRs/Issues. Check for busywork."
            )

        if latest.velocity_trend == "Accelerating" and latest.progress_score > 0:
            warnings.append(
                "Momentum Surge: You are shipping significantly faster than your 14-day average."
            )

        # 3. Leverage Hotspots
        outcomes = (
            self.session.query(OutcomeLedger)
            .filter(
                OutcomeLedger.status == "SUCCESS",
                OutcomeLedger.recorded_at >= thirty_days_ago,
            )
            .order_by(OutcomeLedger.leverage_generated.desc())
            .limit(5)
            .all()
        )

        hotspots = []
        for o in outcomes:
            if o.leverage_generated > 2.0:
                hotspots.append(
                    {
                        "recommendation": o.recommendation_text[:100],
                        "leverage": round(o.leverage_generated, 2),
                    }
                )

        if not hotspots and len(outcomes) > 0:
            hotspots.append(
                {
                    "recommendation": "Logging consistent outcomes will reveal leverage hotspots over time.",
                    "leverage": 0.0,
                }
            )

        # 4. Strength Graph (Success Rate by Domain)
        all_outcomes = self.session.query(OutcomeLedger).all()
        domain_stats = {}
        for o in all_outcomes:
            if o.domain not in domain_stats:
                domain_stats[o.domain] = {"total": 0, "success": 0, "leverage": 0.0}
            domain_stats[o.domain]["total"] += 1
            domain_stats[o.domain]["leverage"] += float(o.leverage_generated)
            if o.status == "SUCCESS":
                domain_stats[o.domain]["success"] += 1

        strength_graph = []
        for domain, stats in domain_stats.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            strength_graph.append(
                {"domain": domain, "success_rate": round(success_rate, 1)}
            )
        strength_graph.sort(key=lambda x: x["success_rate"], reverse=True)

        # 5. Failure Graph (Count by Reason)
        failure_stats = {}
        for o in all_outcomes:
            if (
                o.status == "FAILURE"
                and o.failure_reason
                and o.failure_reason != "None"
            ):
                if o.failure_reason not in failure_stats:
                    failure_stats[o.failure_reason] = 0
                failure_stats[o.failure_reason] += 1

        failure_graph = []
        for reason, count in failure_stats.items():
            failure_graph.append({"reason": reason, "count": count})
        failure_graph.sort(key=lambda x: x["count"], reverse=True)

        # 6. Energy Graph (Leverage by Hour)
        hour_stats = {}
        for o in all_outcomes:
            # Safely get hour, fallback to 0 if no timezone
            hour = o.recorded_at.hour if o.recorded_at else 0
            if hour not in hour_stats:
                hour_stats[hour] = {"total": 0, "leverage": 0.0}
            hour_stats[hour]["total"] += 1
            hour_stats[hour]["leverage"] += float(o.leverage_generated)

        energy_graph = []
        for hour, stats in hour_stats.items():
            avg_lev = stats["leverage"] / stats["total"]
            energy_graph.append({"hour": hour, "average_leverage": round(avg_lev, 2)})
        energy_graph.sort(key=lambda x: x["hour"])

        # 7. Leverage DNA Engine
        leverage_dna = []
        if len(all_outcomes) > 3:
            # Find highest leverage domain
            highest_lev_domain = max(
                domain_stats.keys(),
                key=lambda d: (
                    domain_stats[d]["leverage"] / domain_stats[d]["total"]
                    if domain_stats[d]["total"] > 0
                    else 0
                ),
            )
            highest_lev = (
                domain_stats[highest_lev_domain]["leverage"]
                / domain_stats[highest_lev_domain]["total"]
            )
            if highest_lev > 1.0:
                leverage_dna.append(
                    {
                        "directive": f"Do more {highest_lev_domain}",
                        "reason": f"It averages {round(highest_lev, 2)}x leverage.",
                    }
                )

            # Find top failure reason
            if failure_graph:
                top_failure = failure_graph[0]["reason"]
                leverage_dna.append(
                    {
                        "directive": f"Stop {top_failure.lower()}",
                        "reason": f"It has killed {failure_graph[0]['count']} projects/tasks.",
                    }
                )

            # Find lowest success domain
            if strength_graph:
                lowest = strength_graph[-1]
                if lowest["success_rate"] < 50:
                    leverage_dna.append(
                        {
                            "directive": f"Delegate or avoid {lowest['domain']}",
                            "reason": f"Your success rate is only {lowest['success_rate']}%.",
                        }
                    )

        return {
            "activity_score": round(latest.activity_score, 2),
            "progress_score": round(latest.progress_score, 2),
            "impact_score": round(latest.impact_score, 2),
            "strength_graph": strength_graph,
            "failure_graph": failure_graph,
            "energy_graph": energy_graph,
            "leverage_dna": leverage_dna,
            "warnings": warnings,
            "hotspots": hotspots,
        }
