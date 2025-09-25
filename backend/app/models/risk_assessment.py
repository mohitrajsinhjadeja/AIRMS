"""
Risk Assessment data models for enterprise risk detection
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class RiskCategory(str, Enum):
    """Risk categories for classification"""
    MISINFORMATION = "misinformation"
    SECURITY_THREAT = "security_threat"
    ANOMALY = "anomaly"
    COMPLIANCE_VIOLATION = "compliance_violation"
    CONTENT_SAFETY = "content_safety"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    DATA_PRIVACY = "data_privacy"
    BIAS_DISCRIMINATION = "bias_discrimination"


class RiskSeverity(str, Enum):
    """Risk severity levels"""
    CRITICAL = "critical"  # 90-100
    HIGH = "high"         # 70-89
    MEDIUM = "medium"     # 40-69
    LOW = "low"          # 20-39
    MINIMAL = "minimal"   # 0-19


class ContentType(str, Enum):
    """Types of content that can be assessed"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOG_ENTRY = "log_entry"
    API_REQUEST = "api_request"


class DetectionMethod(str, Enum):
    """Methods used for risk detection"""
    NLP_TRANSFORMER = "nlp_transformer"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_MATCHING = "pattern_matching"
    ML_CLASSIFIER = "ml_classifier"
    RULE_BASED = "rule_based"
    ENSEMBLE = "ensemble"


class RiskEvidence(BaseModel):
    """Evidence supporting a risk assessment"""
    type: str = Field(..., description="Type of evidence")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    description: str = Field(..., description="Human-readable description")
    data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")
    source: Optional[str] = Field(None, description="Source of evidence")


class MitigationAction(BaseModel):
    """Recommended mitigation action"""
    action_type: str = Field(..., description="Type of mitigation action")
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest)")
    description: str = Field(..., description="Action description")
    automated: bool = Field(False, description="Can be automated")
    estimated_effort: Optional[str] = Field(None, description="Estimated effort")


class RiskAssessmentBase(BaseModel):
    """Base risk assessment model"""
    content_id: str = Field(..., description="Unique identifier for content")
    content_type: ContentType = Field(..., description="Type of content")
    content_hash: Optional[str] = Field(None, description="Hash of content for deduplication")
    
    # Risk scoring
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall risk score")
    risk_severity: RiskSeverity = Field(..., description="Risk severity level")
    risk_categories: List[RiskCategory] = Field(..., description="Detected risk categories")
    
    # Detection details
    detection_methods: List[DetectionMethod] = Field(..., description="Methods used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    evidence: List[RiskEvidence] = Field(default_factory=list, description="Supporting evidence")
    
    # Context
    source_ip: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    session_id: Optional[str] = Field(None, description="Session identifier")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    
    # Mitigation
    mitigation_actions: List[MitigationAction] = Field(default_factory=list)
    auto_mitigated: bool = Field(False, description="Was automatically mitigated")
    
    # Metadata
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    model_version: Optional[str] = Field(None, description="Model version used")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RiskAssessmentCreate(RiskAssessmentBase):
    """Create risk assessment model"""
    user_id: Optional[str] = Field(None, description="User who submitted content")


class RiskAssessmentInDB(RiskAssessmentBase):
    """Risk assessment model as stored in database"""
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: Optional[ObjectId] = Field(None, description="User who submitted content")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    
    # Status tracking
    status: Literal["pending", "completed", "failed", "reviewed"] = "completed"
    reviewed_by: Optional[ObjectId] = Field(None, description="Admin who reviewed")
    reviewed_at: Optional[datetime] = Field(None)
    
    # Escalation
    escalated: bool = Field(False, description="Was escalated to human review")
    escalated_at: Optional[datetime] = Field(None)
    escalation_reason: Optional[str] = Field(None)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response model"""
    id: str
    content_id: str
    content_type: str
    content_hash: Optional[str] = None
    
    # Risk scoring
    risk_score: float
    risk_severity: str
    risk_categories: List[str]
    
    # Detection details
    detection_methods: List[str]
    confidence: float
    evidence: List[RiskEvidence]
    
    # Context
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    organization_id: Optional[str] = None
    
    # Mitigation
    mitigation_actions: List[MitigationAction]
    auto_mitigated: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Status
    status: str
    escalated: bool
    
    # Performance
    processing_time_ms: Optional[float] = None
    model_version: Optional[str] = None


class BulkRiskAssessmentRequest(BaseModel):
    """Bulk risk assessment request"""
    items: List[Dict[str, Any]] = Field(..., max_items=100, description="Items to assess")
    priority: Literal["low", "normal", "high"] = "normal"
    callback_url: Optional[str] = Field(None, description="Webhook URL for results")
    batch_id: Optional[str] = Field(None, description="Batch identifier")


class RiskAssessmentStats(BaseModel):
    """Risk assessment statistics"""
    total_assessments: int
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    by_status: Dict[str, int]
    average_risk_score: float
    average_processing_time_ms: float
    escalation_rate: float
    auto_mitigation_rate: float


class RiskTrend(BaseModel):
    """Risk trend data point"""
    timestamp: datetime
    risk_score: float
    assessment_count: int
    severity_distribution: Dict[str, int]


class RiskAssessmentFilter(BaseModel):
    """Filter parameters for risk assessments"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    severities: Optional[List[RiskSeverity]] = None
    categories: Optional[List[RiskCategory]] = None
    content_types: Optional[List[ContentType]] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    escalated_only: Optional[bool] = None
    status: Optional[str] = None
    limit: int = Field(50, ge=1, le=1000)
    skip: int = Field(0, ge=0)
