from pydantic import BaseModel, Field
from typing import Dict, Any, Callable, Optional

class ToolManifest(BaseModel):
    name: str = Field(..., description="Unique string identifier for the tool")
    description: str = Field(..., description="Detailed explanation of what the tool does")
    risk_score: float = Field(..., description="0.0 (safe) to 1.0 (dangerous) risk score")
    reversibility_score: float = Field(..., description="0.0 (irreversible) to 1.0 (easily reversible)")
    
    def __hash__(self):
        return hash(self.name)
