from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseSchema

class FactCheckRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=1000)
    sources: Optional[List[str]] = Field(
        default=["google", "newsapi", "wikipedia"],
        description="List of fact checking sources to use"
    )

class FactCheckResult(BaseModel):
    source: str
    status: str
    confidence: float = Field(ge=0.0, le=1.0)
    details: Optional[Dict[str, Any]] = None

class FactCheckResponse(BaseSchema):
    claim: str
    verification_status: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    sources: int
    results: List[FactCheckResult]
    timestamp: datetime