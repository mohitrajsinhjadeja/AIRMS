from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class RiskAnalysisRequest(BaseModel):
    input: str = Field(
        ...,
        description="Text input to analyze for risks",
        min_length=1,
        max_length=32768
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context for risk analysis"
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional configuration for risk analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "input": "Sample text to analyze for risks",
                "context": {
                    "user_type": "developer",
                    "environment": "production"
                },
                "config": {
                    "detectors": ["pii", "bias", "hallucination"],
                    "risk_threshold": 0.7
                }
            }
        }