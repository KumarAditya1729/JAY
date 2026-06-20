from jay.db import SessionLocal
from jay.engines.models import (
    ConstraintLedger,
    OpportunityLedger,
    TaskLedger,
    OutcomeLedger,
    CommitmentLedger
)
from jay.engines.business.intelligence import BusinessIntelligenceEngine

class ConstraintIntelligenceEngine:
    @staticmethod
    def detect_global_constraint() -> dict | None:
        """
        Determines the current system constraint using Theory of Constraints heuristics.
        Returns the top active constraint or None.
        """
        with SessionLocal() as db:
            constraints_found = []

            # 1. CASH CONSTRAINT
            biz_data = BusinessIntelligenceEngine.analyze_business_reality()
            if biz_data["runway_months"] < 6.0:
                constraints_found.append({
                    "constraint_type": "CASH",
                    "severity": "CRITICAL",
                    "confidence": 1.0,
                    "evidence": f"Runway is only {biz_data['runway_months']} months.",
                    "recommended_action": "Pause all non-essential dev; transition to 100% fundraising & closing."
                })

            # 2. FOUNDER CONSTRAINT
            pending_tasks = db.query(TaskLedger).filter(TaskLedger.status != "SUCCESS").count()
            overdue_commitments = db.query(CommitmentLedger).filter(CommitmentLedger.status == "PENDING").count() # simplified
            if pending_tasks > 30 or overdue_commitments > 10:
                constraints_found.append({
                    "constraint_type": "FOUNDER",
                    "severity": "CRITICAL" if pending_tasks > 50 else "HIGH",
                    "confidence": 0.9,
                    "evidence": f"{pending_tasks} open tasks, {overdue_commitments} overdue commitments.",
                    "recommended_action": "Stop starting new things. Execute pending backlog or delegate immediately."
                })

            # 3. SALES CONSTRAINT
            opportunities = db.query(OpportunityLedger).filter(OpportunityLedger.status == "DETECTED").count()
            won_outcomes = db.query(OutcomeLedger).filter(OutcomeLedger.domain == "Sales", OutcomeLedger.status == "SUCCESS").count()
            if opportunities > 10 and won_outcomes == 0:
                constraints_found.append({
                    "constraint_type": "SALES",
                    "severity": "CRITICAL",
                    "confidence": 0.85,
                    "evidence": f"{opportunities} leads detected, but 0 conversions.",
                    "recommended_action": "Fix onboarding pitch and actively close deals."
                })

            # Save newly detected constraints to the Ledger
            for c in constraints_found:
                # Check if this exact constraint is already active
                existing = db.query(ConstraintLedger).filter(
                    ConstraintLedger.constraint_type == c["constraint_type"],
                    ConstraintLedger.resolved == False
                ).first()

                if not existing:
                    new_constraint = ConstraintLedger(
                        constraint_type=c["constraint_type"],
                        severity=c["severity"],
                        confidence=c["confidence"],
                        evidence=c["evidence"],
                        recommended_action=c["recommended_action"],
                        resolved=False
                    )
                    db.add(new_constraint)
            
            db.commit()

            # Return the highest severity active constraint
            top_constraint = db.query(ConstraintLedger).filter(
                ConstraintLedger.resolved == False
            ).order_by(
                # Sort by severity (CRITICAL > HIGH > MEDIUM)
                ConstraintLedger.severity.asc() # Alphabetical C < H < M, so CRITICAL is first
            ).first()

            if top_constraint:
                return {
                    "id": str(top_constraint.id),
                    "type": top_constraint.constraint_type,
                    "severity": top_constraint.severity,
                    "evidence": top_constraint.evidence,
                    "recommended_action": top_constraint.recommended_action
                }
            return None
