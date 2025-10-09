from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AnalyticsSummary(BaseModel):
    """Analytics summary data"""
    total_users: int = 0
    active_users: int = 0
    total_assessments: int = 0
    high_risk_count: int = 0

class AnalyticsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    detectors: List[str] = ["pii", "bias", "hallucination"]

class AnalyticsResponse(BaseModel):
    """Analytics API response"""
    success: bool = True
    message: Optional[str] = None
    data: AnalyticsSummary
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TimelinePoint(BaseModel):
    """Single point in analytics timeline"""
    timestamp: datetime
    value: float
    label: str

class TimelineResponse(BaseModel):
    """Timeline data response"""
    success: bool = True
    data: List[TimelinePoint]
    period: str

class DashboardResponse(BaseModel):
    """Dashboard data response"""
    success: bool = True
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)