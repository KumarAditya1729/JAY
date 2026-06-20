from jay.db import SessionLocal
from jay.engines.models import FounderPreferenceLedger
import datetime

class DigitalTwinEngine:
    @staticmethod
    def predict_decision(situation: str) -> dict:
        """
        Decision Prediction Engine
        Predicts a likely decision for a given situation based on historical DNA.
        """
        # In a real system, we'd query FounderDecisionLedger and FounderBehaviorLedger via an LLM or ML model.
        # For this prototype, we simulate the output based on the "Fundraising" vs "Product" DNA.
        if "fundraising" in situation.lower():
            return {
                "situation": situation,
                "prediction": "Reject and focus on Product Velocity.",
                "confidence": 0.89,
                "reason": "Previous 17 similar decisions favored product velocity over fundraising."
            }
        
        return {
            "situation": situation,
            "prediction": "Delegate to Engineering Agent.",
            "confidence": 0.72,
            "reason": "Matches typical execution style for non-critical path tasks."
        }

    @staticmethod
    def get_preferences() -> list[dict]:
        """
        Preference Graph
        """
        with SessionLocal() as db:
            prefs = db.query(FounderPreferenceLedger).order_by(FounderPreferenceLedger.weight.desc()).all()
            return [
                {
                    "preference_key": p.preference_key,
                    "preferred": p.preferred_value,
                    "rejected": p.rejected_value,
                    "weight": p.weight
                } for p in prefs
            ]

    @staticmethod
    def get_energy_state() -> dict:
        """
        Energy Model
        Analyzes the current time and predicts cognitive state.
        """
        now = datetime.datetime.now()
        hour = now.hour
        
        state = "Recovery"
        task = "Rest"
        
        if 7 <= hour < 12:
            state = "Peak"
            task = "Morning Deep Work & High Creativity"
        elif 12 <= hour < 17:
            state = "Active"
            task = "Execution & Meetings"
        elif 17 <= hour < 22:
            state = "Trough"
            task = "Low-Energy Admin / Strategy Review"
            
        return {
            "current_time": now.strftime("%H:%M"),
            "energy_level": state,
            "optimal_task": task
        }
