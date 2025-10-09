from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field

class RequestLog(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    input_hash: str  # Hashed version of input for privacy
    risk_scores: Dict[str, float]
    mitigation_action: str
    llm_provider: str | None
    processing_time: float
    
    class Config:
        collection = "request_logs"
        indexes = [
            "request_id",
            ("user_id", "timestamp"),
            "mitigation_action"
        ]