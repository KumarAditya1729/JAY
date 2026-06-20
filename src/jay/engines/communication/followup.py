from datetime import datetime, timezone
from jay.db import SessionLocal
from jay.engines.models import CommitmentLedger, RelationshipLedger

class FollowUpEngine:
    @staticmethod
    def analyze():
        """
        Scans JAY's Communication OS for:
        1. Pending or overdue commitments.
        2. High-value neglected relationships.
        Returns a list of actionable insights for the Founder.
        """
        insights = []
        now = datetime.now(timezone.utc)
        
        with SessionLocal() as db:
            # 1. Analyze Commitments
            pending_commitments = db.query(CommitmentLedger).filter(
                CommitmentLedger.status == "Pending"
            ).all()
            
            for commitment in pending_commitments:
                rel = db.query(RelationshipLedger).filter_by(id=commitment.relationship_id).first()
                if not rel:
                    continue
                
                days_old = (now - commitment.created_at.replace(tzinfo=timezone.utc)).days
                
                # Check due date
                if commitment.due_date and commitment.due_date.replace(tzinfo=timezone.utc) < now:
                    insights.append(
                        f"OVERDUE: {commitment.owner} owes '{commitment.promise_text}' to {rel.name}. It was due on {commitment.due_date.date()}."
                    )
                elif days_old > 3:
                    insights.append(
                        f"PENDING: {commitment.owner} promised '{commitment.promise_text}' to {rel.name} {days_old} days ago."
                    )
                    
            # 2. Analyze Neglected Relationships
            relationships = db.query(RelationshipLedger).all()
            for rel in relationships:
                if not rel.last_contact_date:
                    continue
                
                days_since_contact = (now - rel.last_contact_date.replace(tzinfo=timezone.utc)).days
                
                # High strategic value or high revenue generated should be contacted frequently
                if rel.strategic_value >= 0.8 and days_since_contact > 14:
                    insights.append(
                        f"NEGLECTED: {rel.name} ({rel.role}) has extremely high strategic value ({rel.strategic_value}), but hasn't been contacted in {days_since_contact} days."
                    )
                elif rel.trust_level < 0.4 and days_since_contact > 30:
                    insights.append(
                        f"DETERIORATING: Relationship with {rel.name} is fading (Trust: {rel.trust_level}). No contact in {days_since_contact} days."
                    )
                    
        return insights
