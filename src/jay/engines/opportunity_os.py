from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from jay.db import SessionLocal
from jay.engines.models import OpportunityLedger, CommunicationLedger, ObservationLedger
from jay.engines.llm import generate_chat
import json
import re

class OpportunityOSEngine:
    @staticmethod
    def scan_for_opportunities():
        """
        Scans CommunicationLedger and ObservationLedger for unstructured opportunities
        and extracts them into OpportunityLedger using an LLM.
        """
        with SessionLocal() as db:
            # 1. Fetch un-scanned communications from last 7 days
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Simple heuristic: scan everything recent. In production, we'd mark `scanned_for_opportunities = True`
            recent_comms = db.query(CommunicationLedger).filter(
                CommunicationLedger.timestamp >= seven_days_ago
            ).all()
            
            recent_obs = db.query(ObservationLedger).filter(
                ObservationLedger.timestamp >= seven_days_ago
            ).all()
            
            if not recent_comms and not recent_obs:
                return

            # Prepare Context
            context = "RECENT COMMUNICATIONS:\\n"
            for c in recent_comms:
                context += f"ID: {c.id} | From: {c.person_id} | Channel: {c.channel} | Summary: {c.summary}\\n"
                
            context += "\\nRECENT OBSERVATIONS:\\n"
            for o in recent_obs:
                context += f"ID: {o.id} | Source: {o.source} | Payload: {o.payload}\\n"

            system_prompt = \"\"\"
You are JAY's Opportunity OS Engine.
Your job is to scan the Founder's recent communications and observations to detect HIGH-LEVERAGE BUSINESS OPPORTUNITIES.
We are looking for: Customers, Partnerships, Funding, Hiring, Acquisition, or Distribution.

If you find an opportunity, return a JSON array of objects with this exact schema:
[
  {
    "title": "Short title of opportunity",
    "description": "Why this is an opportunity",
    "opportunity_type": "Customer" | "Partnership" | "Funding",
    "revenue_potential": "Estimate e.g., ₹5L–₹15L annually, or 'High', 'Unknown'",
    "recommended_action": "What the founder should do next",
    "score": 0.0 to 1.0 (float, 1.0 is highest leverage),
    "source_id": "UUID from the input context"
  }
]

If NO opportunities are found, return an empty array: []
\"\"\"

            try:
                response = generate_chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context}
                    ],
                    temperature=0.3
                )
                
                content = response["choices"][0]["message"]["content"].strip()
                json_match = re.search(r'\\[.*\\]', content, re.DOTALL)
                
                if json_match:
                    opportunities = json.loads(json_match.group(0))
                    
                    for opp in opportunities:
                        # Check if we already logged this opportunity based on source_id
                        existing = db.query(OpportunityLedger).filter(
                            OpportunityLedger.source_id == opp["source_id"],
                            OpportunityLedger.title == opp["title"]
                        ).first()
                        
                        if not existing:
                            new_opp = OpportunityLedger(
                                title=opp["title"],
                                description=opp["description"],
                                opportunity_type=opp["opportunity_type"],
                                revenue_potential=opp["revenue_potential"],
                                recommended_action=opp["recommended_action"],
                                score=opp["score"],
                                status="DETECTED",
                                source_id=opp["source_id"]
                            )
                            db.add(new_opp)
                    
                    db.commit()
            except Exception as e:
                print(f"Failed to scan opportunities: {e}")


    @staticmethod
    def analyze_opportunities() -> dict | None:
        """
        Deterministically returns the highest ranked ACTIVE opportunity.
        """
        with SessionLocal() as db:
            top_opp = db.query(OpportunityLedger).filter(
                OpportunityLedger.status.in_(["DETECTED", "PURSUING"])
            ).order_by(OpportunityLedger.score.desc()).first()
            
            if top_opp:
                return {
                    "id": str(top_opp.id),
                    "opportunity_score": round(top_opp.score, 2),
                    "title": top_opp.title,
                    "revenue_potential": top_opp.revenue_potential,
                    "recommended_action": top_opp.recommended_action
                }
            return None
