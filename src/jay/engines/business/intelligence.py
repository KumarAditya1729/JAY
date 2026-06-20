from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from jay.db import SessionLocal
from jay.engines.models import FinancialLedger, OutcomeLedger

class BusinessIntelligenceEngine:
    FOUNDER_HOURLY_RATE = 500.0 # Standard $500/hr opportunity cost
    
    @staticmethod
    def analyze_business_reality():
        with SessionLocal() as db:
            mrr = BusinessIntelligenceEngine.calculate_mrr(db)
            runway_months, burn_rate = BusinessIntelligenceEngine.calculate_runway(db)
            founder_roi, hours_tracked = BusinessIntelligenceEngine.calculate_founder_roi(db)
            
            return {
                "mrr": mrr,
                "runway_months": runway_months,
                "monthly_burn_rate": burn_rate,
                "founder_roi_score": founder_roi,
                "hours_tracked": hours_tracked
            }
            
    @staticmethod
    def calculate_mrr(db) -> float:
        # Sum all recent active 'MRR' revenue
        # For simplicity, we just sum any Revenue marked as 'MRR' 
        # In a real system this handles churn, upgrades, downgrades.
        mrr_records = db.query(FinancialLedger).filter(
            FinancialLedger.transaction_type == "Revenue",
            FinancialLedger.category == "MRR"
        ).all()
        return sum(r.amount for r in mrr_records)
        
    @staticmethod
    def calculate_runway(db) -> tuple[float, float]:
        """
        Calculates total cash buffer vs 30-day burn rate.
        """
        # Calculate Total Cash (Funding + Revenue - Expenses)
        total_cash = 0.0
        all_tx = db.query(FinancialLedger).all()
        for tx in all_tx:
            if tx.transaction_type in ["Revenue", "Funding"]:
                total_cash += tx.amount
            elif tx.transaction_type == "Expense":
                total_cash -= tx.amount
                
        # Calculate 30-day burn (Expenses only)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_expenses = db.query(FinancialLedger).filter(
            FinancialLedger.transaction_type == "Expense",
            FinancialLedger.date_recorded >= thirty_days_ago
        ).all()
        
        burn_rate = sum(e.amount for e in recent_expenses)
        
        if burn_rate == 0:
            return float('inf'), 0.0
            
        runway_months = total_cash / burn_rate
        return round(runway_months, 1), round(burn_rate, 2)
        
    @staticmethod
    def calculate_founder_roi(db) -> tuple[float, float]:
        """
        Are the founder's hours generating leverage?
        Value = leverage_generated * (assumed value per leverage point)
        Cost = hours_invested * FOUNDER_HOURLY_RATE
        """
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        outcomes = db.query(OutcomeLedger).filter(
            OutcomeLedger.recorded_at >= thirty_days_ago
        ).all()
        
        total_hours = sum(o.hours_invested for o in outcomes)
        if total_hours == 0:
            return 1.0, 0.0 # Neutral ROI if no hours tracked
            
        total_cost = total_hours * BusinessIntelligenceEngine.FOUNDER_HOURLY_RATE
        
        # Assume 1 leverage point = $2500 in enterprise value (arbitrary coefficient for metric)
        total_value_generated = sum(o.leverage_generated for o in outcomes) * 2500.0
        
        roi = total_value_generated / max(total_cost, 1.0)
        return round(roi, 2), round(total_hours, 1)
