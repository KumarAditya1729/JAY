from enum import Enum
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    FACT = "FACT"
    DECISION = "DECISION"
    LESSON = "LESSON"
    PROJECT = "PROJECT"
    MISSION = "MISSION"
    PERSON = "PERSON"
    MEETING = "MEETING"
    DOCUMENT = "DOCUMENT"
    IDEA = "IDEA"
    CUSTOMER = "CUSTOMER"
    RESEARCH = "RESEARCH"

class NormalizedKnowledge(BaseModel):
    normalized_text: str = Field(..., description="The highly structured string format of the knowledge.")
    memory_type: MemoryType = Field(..., description="The semantic category of this memory.")
    importance: float = Field(..., description="0.0 to 1.0 importance score.")
    confidence: float = Field(..., description="0.0 to 1.0 confidence score.")
    mission_relevance: float = Field(..., description="0.0 to 1.0 relevance to active missions.")
