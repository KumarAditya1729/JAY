import json
from enum import Enum
from pydantic import BaseModel, Field
from jay.engines.llm import generate_chat
from jay.db import SessionLocal
from jay.engines.models import ObservationLedger

class ObservationType(str, Enum):
    VOICE = "VOICE"
    TERMINAL = "TERMINAL"
    GITHUB = "GITHUB"
    DOCUMENT = "DOCUMENT"
    DECISION = "DECISION"
    MEETING = "MEETING"
    IDEA = "IDEA"
    PROJECT_PROGRESS = "PROJECT_PROGRESS"
    CUSTOMER_SIGNAL = "CUSTOMER_SIGNAL"
    REVENUE_SIGNAL = "REVENUE_SIGNAL"
    SYSTEM_EVENT = "SYSTEM_EVENT"

from jay.engines.memory.schemas import NormalizedKnowledge, MemoryType
from jay.engines.memory.engine import MemoryEngine
from jay.engines.communication.extractor import CommunicationEngine

class ObservationAnalysis(BaseModel):
    normalized_text: str = Field(..., description="The highly structured, normalized string format of the knowledge.")
    memory_type: MemoryType = Field(..., description="The semantic category of this observation/knowledge.")
    importance_score: float = Field(..., description="0.0 to 1.0. How important is this for the Founder's overall mission?")
    confidence_score: float = Field(..., description="0.0 to 1.0. How confident are we in the accuracy of this data?")
    source_reliability: float = Field(..., description="0.0 to 1.0. How reliable is the source (e.g., GitHub is 1.0, raw voice is 0.6)?")
    business_relevance: float = Field(..., description="0.0 to 1.0. Does this directly impact revenue, product shipping, or customer satisfaction?")

class ObservationRouter:
    @staticmethod
    def route_observation(source: str, raw_text: str, session_id: str = None) -> ObservationLedger:
        """
        Takes raw string data from various inputs, uses the LLM to structure it into 'Knowledge', 
        assigns quality scores, and saves it into the database.
        """
        system_prompt = (
            "You are the JAY Observation Router. Your job is to classify raw data streams into High-Quality Normalized Knowledge.\n"
            "Analyze the following observation and output strict JSON with its type, quality scores, and a heavily structured 'normalized_text'.\n"
            "Scores range from 0.0 to 1.0.\n"
            "Example of normalized_text:\n"
            "'Customer: Enterprise Client A | Signal: Revenue Event | Amount: $1200 | Impact: Positive'\n"
            "Do NOT output raw strings. Extract the pure structural knowledge.\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Source: {source}\nRaw Text: {raw_text}"}
        ]
        
        try:
            response = generate_chat(
                messages=messages,
                temperature=0.0,
                response_format={
                    "type": "json_object",
                    "schema": ObservationAnalysis.model_json_schema()
                }
            )
            content = response["choices"][0]["message"]["content"]
            analysis = ObservationAnalysis(**json.loads(content))
        except Exception as e:
            # Fallback if LLM fails
            analysis = ObservationAnalysis(
                normalized_text=f"Raw text (Failed Normalization): {raw_text}",
                memory_type=MemoryType.FACT,
                importance_score=0.1,
                confidence_score=0.5,
                source_reliability=0.5,
                business_relevance=0.1
            )
            
        # Bridge to Vector Memory (Phase 9.6)
        try:
            memory_engine = MemoryEngine()
            knowledge = NormalizedKnowledge(
                normalized_text=analysis.normalized_text,
                memory_type=analysis.memory_type,
                importance=analysis.importance_score,
                confidence=analysis.confidence_score,
                mission_relevance=analysis.business_relevance
            )
            memory_engine.embed_and_store(knowledge)
        except Exception as e:
            import logging
            logging.error(f"Failed to embed knowledge into Qdrant: {e}")
            
        # Bridge to Communication OS (Phase 10.0)
        if analysis.memory_type == MemoryType.MEETING:
            try:
                # We extract the contact name from the normalized text if possible, otherwise 'Unknown Contact'
                # In a full system, we would parse the exact person name from the source metadata.
                CommunicationEngine.process(raw_text=raw_text, channel=source, person_name="Detected Contact")
            except Exception as e:
                import logging
                logging.error(f"Communication OS extraction failed: {e}")
            
        with SessionLocal() as db:
            ledger = ObservationLedger(
                session_id=session_id,
                source=source,
                observation_type=analysis.memory_type.value,
                payload={"raw_text": raw_text, "normalized": analysis.normalized_text},
                importance_score=analysis.importance_score,
                confidence_score=analysis.confidence_score,
                source_reliability=analysis.source_reliability,
                business_relevance=analysis.business_relevance,
                status="Unprocessed"
            )
            db.add(ledger)
            db.commit()
            db.refresh(ledger)
            return ledger
