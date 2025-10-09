from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime

class RiskAnalysisResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    risk_score: float = Field(..., ge=0.0, le=10.0)
    detectors: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Results from each risk detector"
    )
    mitigation: Dict[str, Any] = Field(
        ...,
        description="Mitigation actions and recommendations"
    )
    safe_output: str | None = Field(
        None,
        description="Sanitized output if processing was allowed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_20240925153000",
                "timestamp": "2024-09-25T15:30:00Z",
                "risk_score": 3.5,
                "detectors": {
                    "pii": {"detected": False, "score": 0.0},
                    "bias": {"detected": True, "score": 0.7},
                    "hallucination": {"detected": False, "score": 0.1}
                },
                "mitigation": {
                    "action": "warn",
                    "reason": "Medium bias risk detected",
                    "recommendations": ["Consider rephrasing for neutrality"]
                },
                "safe_output": "Sanitized response text"
            }
        }