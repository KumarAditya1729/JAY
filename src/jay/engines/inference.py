from sqlalchemy.orm import Session
from jay.engines.models import (
    ObservationLedger,
    TaskLedger,
    OutcomeLedger,
    WorkSessionLedger,
)


from pydantic import BaseModel, Field
from typing import List, Optional
import json

class TaskCompletionInference(BaseModel):
    task_id: str
    confidence: float
    reason: str

class SessionInferenceOutput(BaseModel):
    session_summary: str
    completed_tasks: List[TaskCompletionInference]

class ContextCorrelator:
    def __init__(self, session: Session):
        self.session = session

    async def infer_outcomes(self):
        # Only process high-importance observations
        unprocessed = (
            self.session.query(ObservationLedger)
            .filter(ObservationLedger.status == "Unprocessed")
            .filter(ObservationLedger.importance_score > 0.5)
            .limit(100)
            .all()
        )
        if not unprocessed:
            return

        session_ids = list(set(obs.session_id for obs in unprocessed if obs.session_id))

        tasks = (
            self.session.query(TaskLedger).filter(TaskLedger.status == "Pending").all()
        )
        task_list_str = (
            "\n".join([f"ID: {t.id} | Task: {t.statement}" for t in tasks])
            if tasks
            else "No open tasks."
        )

        for sid in session_ids:
            work_session = (
                self.session.query(WorkSessionLedger)
                .filter(WorkSessionLedger.id == sid)
                .first()
            )
            if not work_session:
                continue
                
            mission_context = "No active mission assigned to this session."
            if work_session.primary_project_id:
                from jay.engines.models import ProjectLedger, MissionLedger
                proj = self.session.query(ProjectLedger).filter(ProjectLedger.id == work_session.primary_project_id).first()
                if proj:
                    mission = self.session.query(MissionLedger).filter(MissionLedger.id == proj.mission_id).first()
                    if mission:
                        mission_context = f"Mission: {mission.title}\nProject: {proj.title}\nDescription: {mission.description}"

            all_obs = (
                self.session.query(ObservationLedger)
                .filter(ObservationLedger.session_id == sid)
                .filter(ObservationLedger.importance_score > 0.5)
                .order_by(ObservationLedger.created_at.asc())
                .limit(100)
                .all()
            )

            obs_str_list = []
            for o in all_obs:
                # Include observation type and business relevance
                obs_str_list.append(
                    f"[{o.created_at.strftime('%H:%M:%S')}] [{o.observation_type}] {o.source}: {json.dumps(o.payload)} (Relevance: {o.business_relevance})"
                )

            obs_history_str = "\n".join(obs_str_list)

            system_prompt = (
                "You are JAY's Context Correlator. Your role is to correlate Knowledge into actionable Mission progress.\n"
                f"CURRENT ACTIVE MISSION CONTEXT:\n{mission_context}\n\n"
                f"OPEN TASKS:\n{task_list_str}\n\n"
                "Analyze the provided high-quality Session Knowledge timeline. Determine if any open tasks were COMPLETED based on the Mission Context.\n"
                "Return a strict JSON response."
            )

            try:
                import asyncio
                from jay.engines.llm import generate_chat
                
                def _run_llm():
                    return generate_chat(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {
                                "role": "user",
                                "content": f"Session Knowledge Graph:\n{obs_history_str}",
                            },
                        ],
                        temperature=0.1,
                        response_format={
                            "type": "json_object",
                            "schema": SessionInferenceOutput.model_json_schema()
                        }
                    )
                
                response = await asyncio.to_thread(_run_llm)
                content = response["choices"][0]["message"]["content"].strip()
                
                data = json.loads(content)
                inference = SessionInferenceOutput(**data)

                work_session.session_summary = inference.session_summary

                for ct in inference.completed_tasks:
                    if ct.confidence > 0.7:
                        task = (
                            self.session.query(TaskLedger)
                            .filter(TaskLedger.id == ct.task_id)
                            .first()
                        )
                        if task:
                            existing = (
                                self.session.query(OutcomeLedger)
                                .filter(
                                    OutcomeLedger.recommendation_text == task.statement,
                                    OutcomeLedger.status == "INFERRED",
                                )
                                .first()
                            )

                            if not existing:
                                outcome = OutcomeLedger(
                                    execution_id=sid,
                                    recommendation_text=task.statement,
                                    status="INFERRED",
                                    outcome=f"Mission Progress: {ct.reason}",
                                    domain="Execution",
                                    impact_score=task.impact,
                                    hours_saved=1.0,
                                    hours_invested=0.0,
                                    leverage_generated=task.impact,
                                    inferred=True,
                                )
                                self.session.add(outcome)

                for o in all_obs:
                    if o.status == "Unprocessed":
                        o.status = "Inferred"

            except Exception as e:
                import logging
                logging.error(f"Context Correlator failed: {e}")

        self.session.commit()
