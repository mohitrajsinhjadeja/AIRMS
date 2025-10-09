from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

class RequestLog(BaseModel):
    requestId: str
    userId: str
    timestamp: datetime
    input: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    mitigation: Dict[str, Any]
    llm_output: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "requestId": "req_20240925153000_user123",
                "userId": "user123",
                "timestamp": "2024-09-25T15:30:00Z",
                "input": {
                    "original": "Original user input",
                    "sanitized": "Sanitized input",
                    "entities": ["PII", "LOCATION"]
                },
                "risk_assessment": {
                    "riskScore": 7.5,
                    "detectors": {
                        "pii": {"detected": True, "score": 0.8},
                        "bias": {"detected": False, "score": 0.2},
                        "hallucination": {"detected": True, "score": 0.6},
                        "adversarial": {"detected": False, "score": 0.0}
                    }
                },
                "mitigation": {
                    "action": "block",
                    "reason": "High risk content detected",
                    "risk_score": 7.5,
                    "timestamp": "2024-09-25T15:30:00Z"
                },
                "llm_output": {
                    "original": "Original LLM response",
                    "sanitized": "Sanitized LLM response"
                }
            }
        }