from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from .base import BaseSchema

class RiskAnalysisRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=32768)
    config: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "detectors": ["pii", "bias", "hallucination"],
            "threshold": 0.7
        }
    )

class DetectorResult(BaseModel):
    detected: bool
    score: float = Field(ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)

class RiskAnalysisResponse(BaseSchema):
    input_hash: str
    risk_score: float = Field(ge=0.0, le=10.0)
    detectors: Dict[str, DetectorResult]
    mitigation: Optional[Dict[str, Any]]
    recommendations: List[str] = Field(default_factory=list)