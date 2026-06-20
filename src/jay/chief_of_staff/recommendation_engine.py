from sqlalchemy.orm import Session
from jay.engines.risk import RiskEngine
from jay.engines.attention import AttentionEngine
from jay.engines.models import OutcomeLedger, RecommendationLedger
from .leverage_ranker import LeverageRanker, CandidateAction
from .schemas import HighestLeverageAction
from jay.config import get_settings
from jay.engines.polymath import PolymathEngine
from jay.engines.mission.intelligence import MissionIntelligenceEngine
from jay.engines.models import TaskLedger
import uuid


class RecommendationEngine:
    def __init__(self, session: Session):
        self.session = session
        self.ranker = LeverageRanker()
        self.attention = AttentionEngine(session)
        self.risk = RiskEngine(session)
        self.polymath = PolymathEngine(session)

    async def generate_highest_leverage_action(self) -> HighestLeverageAction | None:
        candidates = []

        # 1. Pull Tasks from TaskLedger
        tasks = (
            self.session.query(TaskLedger).filter(TaskLedger.status == "Pending").all()
        )
        # Gather bottlenecks from MissionIntelligenceEngine
        mission_intel = MissionIntelligenceEngine.analyze_missions()
        bottleneck_map = {}
        for md in mission_intel:
            for b in md["bottlenecks"]:
                bottleneck_map[str(b["task"].id)] = b["blocks_count"]

        settings = get_settings()
        for t in tasks:
            multiplier = 1.0 + (bottleneck_map.get(str(t.id), 0) * settings.bottleneck_multiplier)
            candidates.append(
                CandidateAction(
                    statement=f"Execute Task: {t.statement}",
                    reason="Direct project task.",
                    impact=min(10.0, t.impact * multiplier),
                    urgency=min(10.0, t.urgency * multiplier),
                    intent_alignment=9.0,
                    trust=9.5,
                    reversibility=7.0,
                )
            )

        priorities = self.attention.analyze()
        for p in priorities:
            candidates.append(
                CandidateAction(
                    statement=f"Address {p.entity_title}",
                    reason=p.why_it_matters,
                    impact=min(10.0, p.attention_score * 5),
                    urgency=8.0,
                    intent_alignment=9.0,
                    trust=8.5,
                    reversibility=7.0,
                )
            )

        risks = self.risk.analyze()
        for r in risks:
            if r.score > 0.7:
                candidates.append(
                    CandidateAction(
                        statement=f"Mitigate Risk: {r.entity_title}",
                        reason=r.reason,
                        impact=min(10.0, r.score * 10),
                        urgency=9.0,
                        intent_alignment=8.0,
                        trust=9.0,
                        reversibility=6.0,
                    )
                )

        # Default fallback
        if not candidates:
            candidates.append(
                CandidateAction(
                    statement="Review JAY Architecture and Goals",
                    reason="No critical operational risks detected. Perfect time for strategic planning.",
                    impact=7.0,
                    urgency=3.0,
                    intent_alignment=10.0,
                    trust=10.0,
                    reversibility=10.0,
                )
            )

        # DETERMINISTIC RANKING (The Source of Truth)
        ranked = self.ranker.rank(candidates)
        top_action, final_score = ranked[0]

        # Explain the decision using LLM and OutcomeLedger
        top_outcomes = (
            self.session.query(OutcomeLedger)
            .order_by(OutcomeLedger.leverage_generated.desc())
            .limit(3)
            .all()
        )
        learning_context = ""
        if top_outcomes:
            learning_context = (
                "PREVIOUS HIGH LEVERAGE OUTCOMES YOU CAN DRAW ON FOR EXPLANATION:\n"
            )
            for o in top_outcomes:
                learning_context += f"- Recommendation: '{o.recommendation_text}' -> Outcome: {o.outcome} (Leverage Generated: {o.leverage_generated}, Status: {o.status})\n"

        system_prompt = (
            "You are JAY's Explainer. JAY's deterministic ranker has already selected the HIGHEST LEVERAGE ACTION.\n"
            "Your job is ONLY to explain WHY this action is valuable. DO NOT change the action itself.\n"
            f"Apply lessons from {learning_context} if relevant.\n"
            "Return a strictly valid JSON object with the following schema:\n"
            '{ "reason": "A 1-2 sentence compelling explanation of why this action matters right now." }'
        )

        user_prompt = f"SELECTED ACTION: {top_action.statement}\nRAW REASON: {top_action.reason}\nIMPACT SCORE: {top_action.impact}\nFINAL SCORE: {final_score}"

        settings = get_settings()

        llm_reason = top_action.reason
        try:
            import asyncio
            from jay.engines.llm import generate_chat
            import asyncio
            
            def _run_llm():
                return generate_chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3
                )
                
            response = await asyncio.to_thread(_run_llm)
            content = response["choices"][0]["message"]["content"].strip()
            
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            data = json.loads(content.strip())
            llm_reason = data.get("reason", top_action.reason)
        except Exception:
            llm_reason = top_action.reason

        # Save to RecommendationLedger
        rec_id = uuid.uuid4()
        rec_ledger = RecommendationLedger(
            id=rec_id,
            statement=top_action.statement,
            impact_score=top_action.impact,
            urgency_score=top_action.urgency,
            intent_alignment_score=top_action.intent_alignment,
            trust_score=top_action.trust,
            reversibility_score=top_action.reversibility,
            final_score=final_score,
            llm_explanation=llm_reason,
        )
        self.session.add(rec_ledger)
        self.session.commit()

        # Get Polymath Expert Advice
        expert_advice = await self.polymath.apply_framework(
            top_action.statement, llm_reason
        )

        return HighestLeverageAction(
            recommendation_id=str(rec_id),
            statement=top_action.statement,
            reason=llm_reason,
            impact_score=round(top_action.impact, 1),
            estimated_leverage="+10 hours",  # Simplification for now
            confidence_score=round(final_score, 2),
            expert_advice=expert_advice,
        )
