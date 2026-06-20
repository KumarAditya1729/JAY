import uuid
import json
import asyncio
from datetime import datetime, timezone, timedelta
from jay.db import SessionLocal
from jay.engines.models import StrategicSimulationLedger, BoardAdvisoryLedger
from jay.engines.constraints.intelligence import ConstraintIntelligenceEngine
from jay.engines.business.intelligence import BusinessIntelligenceEngine
from jay.engines.llm import generate_chat

class OmegaEngine:
    @staticmethod
    async def get_strategic_simulations() -> list[dict]:
        with SessionLocal() as db:
            one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            sims = db.query(StrategicSimulationLedger).filter(
                StrategicSimulationLedger.created_at >= one_day_ago
            ).order_by(StrategicSimulationLedger.created_at.desc()).all()
            
            if not sims:
                sim_data = await OmegaEngine._generate_strategic_simulation()
                new_sim = StrategicSimulationLedger(
                    scenario=sim_data.get("scenario", "Unknown Scenario"),
                    best_case=sim_data.get("best_case", []),
                    expected_case=sim_data.get("expected_case", []),
                    worst_case=sim_data.get("worst_case", [])
                )
                db.add(new_sim)
                db.commit()
                db.refresh(new_sim)
                sims = [new_sim]

            return [
                {
                    "id": str(s.id),
                    "scenario": s.scenario,
                    "best_case": s.best_case,
                    "expected_case": s.expected_case,
                    "worst_case": s.worst_case
                } for s in sims
            ]

    @staticmethod
    async def get_board_advice() -> list[dict]:
        with SessionLocal() as db:
            one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            boards = db.query(BoardAdvisoryLedger).filter(
                BoardAdvisoryLedger.created_at >= one_day_ago
            ).order_by(BoardAdvisoryLedger.created_at.desc()).all()
            
            if not boards:
                board_data = await OmegaEngine._generate_board_advice()
                new_board = BoardAdvisoryLedger(
                    topic=board_data.get("topic", "General Assessment"),
                    advice=board_data.get("advice", [])
                )
                db.add(new_board)
                db.commit()
                db.refresh(new_board)
                boards = [new_board]

            return [
                {
                    "id": str(b.id),
                    "topic": b.topic,
                    "advice": b.advice
                } for b in boards
            ]

    @staticmethod
    async def _generate_strategic_simulation() -> dict:
        constraint = ConstraintIntelligenceEngine.detect_global_constraint()
        biz_data = BusinessIntelligenceEngine.analyze_business_reality()
        
        context = f"""
        MRR: ${biz_data.get('mrr', 0)}
        Runway: {biz_data.get('runway_months', 0)} months
        Top Constraint: {constraint['type'] if constraint else 'None detected'}
        """

        system_prompt = f"""
        You are JAY OMEGA, a Strategic Simulation Engine.
        Based on the current business reality, identify the biggest looming risk or strategic crossroads, and simulate outcomes.
        
        {context}
        
        Output MUST be strict JSON in the following format:
        {{
            "scenario": "Brief description of the risk or strategic choice",
            "best_case": ["Outcome 1", "Outcome 2"],
            "expected_case": ["Outcome 1", "Outcome 2"],
            "worst_case": ["Outcome 1", "Outcome 2"]
        }}
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
            logging.error(f"Strategic Simulation generation failed: {e}")
            return {
                "scenario": "Simulation Engine Failure",
                "best_case": ["System restored."],
                "expected_case": ["Data sync error."],
                "worst_case": [f"Fatal failure: {e}"]
            }

    @staticmethod
    async def _generate_board_advice() -> dict:
        constraint = ConstraintIntelligenceEngine.detect_global_constraint()
        biz_data = BusinessIntelligenceEngine.analyze_business_reality()
        
        context = f"""
        MRR: ${biz_data.get('mrr', 0)}
        Runway: {biz_data.get('runway_months', 0)} months
        Top Constraint: {constraint['type'] if constraint else 'None detected'}
        Constraint Evidence: {constraint['evidence'] if constraint else 'N/A'}
        """

        system_prompt = f"""
        You are JAY's Digital Board of Directors (e.g., Steve Jobs, Peter Thiel, Naval Ravikant).
        Based on the current business metrics, give critical advice.
        
        {context}
        
        Output MUST be strict JSON in the following format:
        {{
            "topic": "Overall strategic assessment",
            "advice": [
                {{
                    "advisor": "Steve Jobs",
                    "critique": "Their critical perspective based on reality data"
                }},
                {{
                    "advisor": "Naval Ravikant",
                    "critique": "..."
                }}
            ]
        }}
        Provide exactly 2 or 3 pieces of advice.
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
            logging.error(f"Board Advice generation failed: {e}")
            return {
                "topic": "System Error",
                "advice": [{"advisor": "SYSTEM", "critique": f"Failed to generate advice: {e}"}]
            }
