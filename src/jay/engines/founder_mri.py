from datetime import datetime, timezone, timedelta
from jay.db import SessionLocal
from jay.engines.models import WorkSessionLedger, OutcomeLedger, ProjectLedger

class FounderMRIEngine:
    @staticmethod
    def analyze_founder() -> dict:
        """
        Conducts a deep MRI of the Founder's execution patterns.
        """
        with SessionLocal() as db:
            peak_window = FounderMRIEngine.analyze_peak_window(db)
            energy_vampires = FounderMRIEngine.analyze_energy_vampires(db)
            stop_doing_list = FounderMRIEngine.generate_stop_doing_list(db)
            primary_failure = FounderMRIEngine.analyze_failure_patterns(db)
            
            return {
                "peak_performance_window": peak_window,
                "energy_vampires": energy_vampires,
                "stop_doing_list": stop_doing_list,
                "primary_failure_cause": primary_failure
            }

    @staticmethod
    def analyze_peak_window(db) -> str:
        """
        Identifies the time of day with the highest focus_score and lowest energy_drain.
        """
        sessions = db.query(WorkSessionLedger).all()
        if not sessions:
            return "Insufficient data to determine peak window."
            
        hour_scores = {}
        for s in sessions:
            if not s.start_time: continue
            hour = s.start_time.hour
            if hour not in hour_scores:
                hour_scores[hour] = {"focus": 0.0, "drain": 0.0, "count": 0}
            
            hour_scores[hour]["focus"] += s.focus_score
            hour_scores[hour]["drain"] += s.energy_drain
            hour_scores[hour]["count"] += 1
            
        best_hour = None
        best_score = -999.0
        
        for hour, stats in hour_scores.items():
            avg_focus = stats["focus"] / stats["count"]
            avg_drain = stats["drain"] / stats["count"]
            # Score = Focus - (Drain * 0.5)
            score = avg_focus - (avg_drain * 0.5)
            if score > best_score:
                best_score = score
                best_hour = hour
                
        if best_hour is not None:
            time_str = f"{best_hour % 12 or 12} {'AM' if best_hour < 12 else 'PM'}"
            return f"Between {time_str} and {(best_hour+2) % 12 or 12} {'AM' if (best_hour+2)%24 < 12 else 'PM'}"
            
        return "Unknown"

    @staticmethod
    def analyze_energy_vampires(db) -> list:
        """
        Finds projects or session types that cause massive energy drain with low focus.
        """
        sessions = db.query(WorkSessionLedger).filter(WorkSessionLedger.energy_drain > 7.0).all()
        
        vampires = {}
        for s in sessions:
            key = s.session_type
            if s.primary_project_id:
                p = db.query(ProjectLedger).filter(ProjectLedger.id == s.primary_project_id).first()
                if p:
                    key = p.title
            
            if key not in vampires:
                vampires[key] = {"drain": 0.0, "count": 0}
            vampires[key]["drain"] += s.energy_drain
            vampires[key]["count"] += 1
            
        results = []
        for name, stats in vampires.items():
            avg_drain = stats["drain"] / stats["count"]
            results.append({"name": name, "avg_drain": round(avg_drain, 1)})
            
        results.sort(key=lambda x: x["avg_drain"], reverse=True)
        return results[:3]

    @staticmethod
    def generate_stop_doing_list(db) -> list:
        """
        Finds outcomes with High Hours Invested + Low Leverage Generated, OR sessions with terrible ROI.
        """
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        outcomes = db.query(OutcomeLedger).filter(
            OutcomeLedger.recorded_at >= thirty_days_ago,
            OutcomeLedger.hours_invested > 2.0,
            OutcomeLedger.leverage_generated < 0.5
        ).all()
        
        stop_doing = {}
        for o in outcomes:
            if o.domain not in stop_doing:
                stop_doing[o.domain] = {"hours": 0.0, "count": 0}
            stop_doing[o.domain]["hours"] += o.hours_invested
            stop_doing[o.domain]["count"] += 1
            
        results = []
        for domain, stats in stop_doing.items():
            results.append({
                "activity": domain,
                "reason": f"Wasted {round(stats['hours'], 1)} hours for near-zero leverage."
            })
            
        # Add high drain session types
        sessions = db.query(WorkSessionLedger).filter(WorkSessionLedger.session_type != "Execution").all()
        type_stats = {}
        for s in sessions:
            if s.session_type not in type_stats:
                type_stats[s.session_type] = {"drain": 0.0, "count": 0}
            type_stats[s.session_type]["drain"] += s.energy_drain
            type_stats[s.session_type]["count"] += 1
            
        for stype, stats in type_stats.items():
            if stats["count"] > 2 and (stats["drain"] / stats["count"]) > 8.0:
                results.append({
                    "activity": stype,
                    "reason": f"Averages a massive {round(stats['drain']/stats['count'], 1)}/10 energy drain. Delegate this."
                })
                
        return results

    @staticmethod
    def analyze_failure_patterns(db) -> str:
        """
        Finds the most common reason for FAILURE status in OutcomeLedger.
        """
        failures = db.query(OutcomeLedger).filter(
            OutcomeLedger.status == "FAILURE",
            OutcomeLedger.failure_reason.isnot(None)
        ).all()
        
        if not failures:
            return "No systemic failure patterns detected."
            
        reasons = {}
        for f in failures:
            r = f.failure_reason
            reasons[r] = reasons.get(r, 0) + 1
            
        top_reason = max(reasons, key=reasons.get)
        count = reasons[top_reason]
        
        return f"{top_reason} (Caused {count} failed outcomes)"
