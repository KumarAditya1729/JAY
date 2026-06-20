import json
import asyncio
from datetime import datetime, timezone, timedelta
from jay.db import SessionLocal
from jay.engines.models import ExecutiveDebateLedger
from jay.engines.constraints.intelligence import ConstraintIntelligenceEngine
from jay.engines.business.intelligence import BusinessIntelligenceEngine
from jay.engines.llm import generate_chat

class ExecutiveCouncilEngine:
    @staticmethod
    async def get_active_debates() -> list[dict]:
        """
        Retrieves active strategic debates from the Executive Council.
        Uses intelligent caching: generates a new debate if none exists in the last 24 hours.
        """
        with SessionLocal() as db:
            one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            debates = db.query(ExecutiveDebateLedger).filter(
                ExecutiveDebateLedger.created_at >= one_day_ago
            ).order_by(ExecutiveDebateLedger.created_at.desc()).all()
            
            if not debates:
                # Need to generate a new live debate
                debate_data = await ExecutiveCouncilEngine._generate_live_debate()
                
                # Save to db
                new_debate = ExecutiveDebateLedger(
                    topic=debate_data.get("topic", "Unknown Issue"),
                    status="DEBATING",
                    arguments=debate_data.get("arguments", []),
                    founder_decision=None
                )
                db.add(new_debate)
                db.commit()
                db.refresh(new_debate)
                debates = [new_debate]

            return [
                {
                    "id": str(d.id),
                    "topic": d.topic,
                    "status": d.status,
                    "arguments": d.arguments,
                    "founder_decision": d.founder_decision
                } for d in debates
            ]

    @staticmethod
    async def _generate_live_debate() -> dict:
        constraint = ConstraintIntelligenceEngine.detect_global_constraint()
        biz_data = BusinessIntelligenceEngine.analyze_business_reality()
        
        context = f"""
        CURRENT SYSTEM REALITY:
        MRR: ${biz_data.get('mrr', 0)}
        Runway: {biz_data.get('runway_months', 0)} months
        Top Constraint: {constraint['type'] if constraint else 'None detected'}
        Constraint Evidence: {constraint['evidence'] if constraint else 'N/A'}
        """

        system_prompt = f"""
        You are the Executive Council of JAY (CTO, CRO, COO). 
        Based on the current business reality, identify the most pressing strategic issue and debate it.
        
        {context}
        
        Output MUST be strict JSON in the following format:
        {{
            "topic": "Brief 3-6 word description of the issue",
            "arguments": [
                {{
                    "executive": "CTO",
                    "stance": "DELAY/ACCELERATE/PIVOT/etc",
                    "argument": "Their perspective based on the reality data"
                }},
                {{
                    "executive": "CRO",
                    "stance": "...",
                    "argument": "..."
                }}
            ]
        }}
        Provide 2 or 3 arguments maximum.
        """
        
        def _run_llm():
            return generate_chat(
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
        try:
            response = await asyncio.to_thread(_run_llm)
            content = response["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            import logging
            logging.error(f"Live Debate generation failed: {e}")
            return {
                "topic": "System Reality Sync Failure",
                "arguments": [{"executive": "SYSTEM", "stance": "ERROR", "argument": "Failed to generate live debate."}]
            }
