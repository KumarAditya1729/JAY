import json
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

from jay.db import SessionLocal
from jay.engines.llm import generate_chat
from jay.engines.models import RelationshipLedger, CommunicationLedger, CommitmentLedger

class ExtractedCommitment(BaseModel):
    promise_text: str = Field(..., description="The exact commitment made (e.g. 'I will send the proposal tomorrow')")
    owner: str = Field(..., description="Who owes the commitment? Must be 'Founder' or 'Contact'.")

class CommunicationAnalysis(BaseModel):
    summary: str = Field(..., description="A crisp 1-sentence summary of the interaction.")
    sentiment: float = Field(..., description="0.0 to 1.0 (0=negative, 0.5=neutral, 1.0=positive)")
    importance: float = Field(..., description="0.0 to 1.0. How strategically important was this exchange?")
    mission_relevance: float = Field(..., description="0.0 to 1.0. Does this advance an active mission?")
    commitments: List[ExtractedCommitment] = Field(default_factory=list, description="All promises or action items made during the communication.")
    role: str = Field(..., description="The role of the contact (e.g. Customer, Investor, Partner, Employee).")

class CommunicationEngine:
    @staticmethod
    def process(raw_text: str, channel: str, person_name: str):
        """Parses a raw communication and injects it into the Founder Relationship Graph."""
        system_prompt = (
            "You are JAY's Communication Engine. You analyze interactions between the Founder and contacts.\n"
            "Extract a strict JSON summary, calculate sentiments, and extract all COMMITMENTS.\n"
            "If someone says 'I will do X', that is a commitment.\n"
            "If the Founder says 'I will do X', owner is 'Founder'. If the contact says it, owner is 'Contact'.\n"
        )

        try:
            response = generate_chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contact Name: {person_name}\nChannel: {channel}\nTranscript/Text:\n{raw_text}"}
                ],
                temperature=0.1,
                response_format={
                    "type": "json_object",
                    "schema": CommunicationAnalysis.model_json_schema()
                }
            )
            content = response["choices"][0]["message"]["content"]
            analysis = CommunicationAnalysis(**json.loads(content))
        except Exception as e:
            import logging
            logging.error(f"Communication LLM parsing failed: {e}")
            return None

        with SessionLocal() as db:
            # 1. Update or Create Relationship
            rel = db.query(RelationshipLedger).filter(RelationshipLedger.name == person_name).first()
            if not rel:
                rel = RelationshipLedger(
                    name=person_name,
                    role=analysis.role,
                    trust_level=0.5,
                    revenue_generated=0.0,
                    strategic_value=analysis.importance,
                    health_score=1.0,
                    last_contact_date=datetime.now(timezone.utc)
                )
                db.add(rel)
                db.flush()
            else:
                rel.last_contact_date = datetime.now(timezone.utc)
                # Adjust health and trust slightly based on sentiment
                if analysis.sentiment > 0.7:
                    rel.health_score = min(1.0, rel.health_score + 0.05)
                elif analysis.sentiment < 0.3:
                    rel.health_score = max(0.0, rel.health_score - 0.05)
            
            # 2. Record Communication
            comm = CommunicationLedger(
                relationship_id=rel.id,
                channel=channel,
                summary=analysis.summary,
                sentiment=analysis.sentiment,
                importance=analysis.importance,
                mission_relevance=analysis.mission_relevance,
                occurred_at=datetime.now(timezone.utc)
            )
            db.add(comm)
            db.flush()

            # 3. Extract Commitments
            for extracted in analysis.commitments:
                c = CommitmentLedger(
                    communication_id=comm.id,
                    relationship_id=rel.id,
                    promise_text=extracted.promise_text,
                    owner=extracted.owner,
                    status="Pending",
                    created_at=datetime.now(timezone.utc)
                )
                db.add(c)
                
            db.commit()
            return comm
