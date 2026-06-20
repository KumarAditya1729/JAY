from jay.db import SessionLocal
from jay.engines.models import SystemAccuracyLedger, FounderVersusJAYLedger
from collections import defaultdict

class SystemAccuracyEngine:
    @staticmethod
    def get_system_accuracy() -> dict:
        """
        Retrieves the empirical accuracy, calibration, and trust scores of each engine,
        plus the ultimate Founder vs JAY win rate.
        """
        with SessionLocal() as db:
            records = db.query(SystemAccuracyLedger).order_by(SystemAccuracyLedger.created_at.desc()).all()
            
            # Group by engine to calculate trust metrics
            engine_stats = defaultdict(list)
            recent_validations = []
            
            for idx, r in enumerate(records):
                engine_stats[r.engine].append({
                    'accuracy': r.accuracy_score,
                    'confidence': r.confidence_score,
                    'timestamp': r.created_at
                })
                # Keep top 10 recent validations
                if idx < 10:
                    recent_validations.append({
                        "id": str(r.id),
                        "engine": r.engine,
                        "prediction": r.prediction,
                        "outcome": r.outcome,
                        "accuracy_score": r.accuracy_score,
                        "confidence_score": r.confidence_score,
                        "timestamp": r.created_at.isoformat() if r.created_at else None
                    })
            
            aggregated = []
            for engine, evals in engine_stats.items():
                if not evals:
                    continue
                    
                # Accuracy
                acc_scores = [e['accuracy'] for e in evals]
                avg_acc = sum(acc_scores) / len(acc_scores)
                
                # Calibration = 1.0 - absolute difference between confidence and accuracy
                # E.g. If confidence is 0.9 and accuracy is 0.2, calibration error is 0.7. Calibration is 0.3.
                calibrations = []
                for e in evals:
                    err = abs(e['confidence'] - e['accuracy'])
                    calibrations.append(1.0 - err)
                
                avg_calib = sum(calibrations) / len(calibrations)
                
                # Trust Score: weighted average of Accuracy, Calibration, and a sample size modifier
                # E.g. 60% Accuracy, 30% Calibration, 10% Recency/Samples
                sample_bonus = min(1.0, len(evals) / 10.0) # Caps out at 10 samples
                trust_score = (avg_acc * 0.6) + (avg_calib * 0.3) + (sample_bonus * 0.1)
                
                # Drift Detection (last 3 vs historical)
                is_drifting = False
                if len(acc_scores) > 5:
                    recent_acc = sum(acc_scores[:3]) / 3.0
                    historical_acc = sum(acc_scores[3:]) / len(acc_scores[3:])
                    if historical_acc - recent_acc > 0.2: # 20% drop
                        is_drifting = True
                
                # Assign trust tier
                trust_tier = "LOW"
                if trust_score > 0.8:
                    trust_tier = "HIGH"
                elif trust_score > 0.5:
                    trust_tier = "MEDIUM"

                aggregated.append({
                    "engine": engine,
                    "accuracy": avg_acc,
                    "calibration": avg_calib,
                    "trust_score": trust_score,
                    "trust_tier": trust_tier,
                    "is_drifting": is_drifting,
                    "evaluations_count": len(evals)
                })

            # Fetch JAY vs Founder Leaderboard
            versus_records = db.query(FounderVersusJAYLedger).order_by(FounderVersusJAYLedger.created_at.desc()).all()
            jay_wins = 0
            founder_wins = 0
            ties = 0
            leaderboard_log = []
            
            for v in versus_records:
                if v.who_was_right == "JAY":
                    jay_wins += 1
                elif v.who_was_right == "FOUNDER":
                    founder_wins += 1
                elif v.who_was_right == "TIE":
                    ties += 1
                    
                leaderboard_log.append({
                    "id": str(v.id),
                    "scenario": v.scenario,
                    "jay_recommendation": v.jay_recommendation,
                    "founder_decision": v.founder_decision,
                    "outcome": v.outcome,
                    "who_was_right": v.who_was_right,
                    "timestamp": v.created_at.isoformat() if v.created_at else None
                })
                
            total_resolved = jay_wins + founder_wins + ties
            jay_win_rate = (jay_wins / total_resolved) if total_resolved > 0 else 0.0
            
            return {
                "aggregate_accuracy": aggregated,
                "recent_validations": recent_validations,
                "founder_vs_jay": {
                    "jay_wins": jay_wins,
                    "founder_wins": founder_wins,
                    "ties": ties,
                    "jay_win_rate": jay_win_rate,
                    "log": leaderboard_log
                }
            }
