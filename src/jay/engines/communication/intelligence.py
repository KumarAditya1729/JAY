from datetime import datetime, timezone
from jay.engines.models import RelationshipLedger, CommitmentLedger, CommunicationLedger
from jay.db import SessionLocal

class RelationshipIntelligenceEngine:
    ROLE_MULTIPLIERS = {
        "Investor": 0.9,
        "Customer": 0.8,
        "Partner": 0.7,
        "Mentor": 0.8,
        "Employee": 0.6,
        "Contact": 0.3
    }

    @staticmethod
    def analyze_all():
        with SessionLocal() as db:
            relationships = db.query(RelationshipLedger).all()
            results = []
            
            for rel in relationships:
                health = RelationshipIntelligenceEngine.calculate_health(db, rel)
                leverage = RelationshipIntelligenceEngine.calculate_leverage(rel)
                is_neglected = RelationshipIntelligenceEngine.detect_neglect(rel)
                
                # Fetch pending commitments for this relationship
                commitments = db.query(CommitmentLedger).filter(
                    CommitmentLedger.relationship_id == rel.id,
                    CommitmentLedger.status == "Pending"
                ).all()
                
                results.append({
                    "relationship": rel,
                    "health_score": health,
                    "leverage_score": leverage,
                    "is_neglected": is_neglected,
                    "pending_commitments": len(commitments)
                })
            
            # Sort by leverage descending, so we prioritize the most important relationships
            results.sort(key=lambda x: x["leverage_score"], reverse=True)
            return results

    @staticmethod
    def calculate_health(db, rel: RelationshipLedger) -> float:
        """
        Formula: Frequency + Responsiveness + Commitments Kept + Strategic Value
        """
        # Baseline from DB
        health = 0.5
        
        # 1. Frequency (Days since last contact)
        if rel.last_contact_date:
            days_since = (datetime.now(timezone.utc) - rel.last_contact_date.replace(tzinfo=timezone.utc)).days
            if days_since < 7:
                health += 0.2
            elif days_since > 30:
                health -= 0.3
        else:
            health -= 0.2
            
        # 2. Responsiveness/Sentiment
        comms = db.query(CommunicationLedger).filter_by(relationship_id=rel.id).order_by(CommunicationLedger.occurred_at.desc()).limit(5).all()
        if comms:
            avg_sentiment = sum(c.sentiment for c in comms) / len(comms)
            if avg_sentiment > 0.7:
                health += 0.1
            elif avg_sentiment < 0.4:
                health -= 0.1
                
        # 3. Commitments Kept
        total_commitments = db.query(CommitmentLedger).filter_by(relationship_id=rel.id).count()
        if total_commitments > 0:
            overdue = db.query(CommitmentLedger).filter(
                CommitmentLedger.relationship_id == rel.id,
                CommitmentLedger.status == "Pending",
                CommitmentLedger.due_date < datetime.now(timezone.utc)
            ).count()
            if overdue > 0:
                health -= 0.2
                
        # Bound between 0.0 and 1.0
        return max(0.0, min(1.0, health))

    @staticmethod
    def calculate_leverage(rel: RelationshipLedger) -> float:
        """
        Base Role Multiplier * (Revenue + Strategic Value)
        """
        base_multiplier = RelationshipIntelligenceEngine.ROLE_MULTIPLIERS.get(rel.role, 0.2)
        # Normalize revenue arbitrarily for score (e.g. 1.0 per 10k)
        revenue_score = min(rel.revenue_generated / 10000.0, 1.0)
        
        leverage = base_multiplier * (revenue_score + rel.strategic_value + rel.trust_level)
        return round(leverage, 2)

    @staticmethod
    def detect_neglect(rel: RelationshipLedger) -> bool:
        """
        High Value Contact + No interaction > 30 days = Relationship Risk
        """
        if rel.strategic_value < 0.6:
            return False
            
        if not rel.last_contact_date:
            return True
            
        days_since = (datetime.now(timezone.utc) - rel.last_contact_date.replace(tzinfo=timezone.utc)).days
        if days_since > 30:
            return True
            
        return False
