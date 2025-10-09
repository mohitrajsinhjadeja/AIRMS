"""
🗄️ MongoDB Models for AIRMS Risk Detection System
Comprehensive data models for storing risk analysis results
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic compatibility"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class RiskSeverity(str, Enum):
    """Risk severity levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionStatus(str, Enum):
    """Detection processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MitigationAction(str, Enum):
    """Available mitigation actions"""
    BLOCK = "block"
    FLAG = "flag"
    WARN = "warn"
    MONITOR = "monitor"
    SANITIZE = "sanitize"
    REDACT = "redact"

# PII Detection Models
class PIIDetectionResult(BaseModel):
    """Individual PII detection result"""
    pii_type: str = Field(..., description="Type of PII detected")
    value: str = Field(..., description="Original PII value")
    hashed_value: str = Field(..., description="Securely hashed PII value")
    severity: RiskSeverity = Field(..., description="Risk severity level")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence score")
    description: str = Field(..., description="Human-readable description")
    position: int = Field(..., description="Position in original text")
    detection_method: str = Field(..., description="Method used for detection")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PIIAnalysis(BaseModel):
    """Complete PII analysis result"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User who made the request")
    original_text_hash: str = Field(..., description="Hash of original input text")
    
    # Detection results
    pii_found: List[PIIDetectionResult] = Field(default_factory=list)
    risk_score: float = Field(..., ge=0, le=100, description="Overall PII risk score")
    severity: RiskSeverity = Field(..., description="Overall severity level")
    masked_text: str = Field(..., description="Text with PII masked/redacted")
    
    # Metadata
    detection_timestamp: datetime = Field(default_factory=datetime.utcnow)
    detection_methods: List[str] = Field(default_factory=list)
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    # Hashed PII storage for compliance
    hashed_pii_store: Dict[str, Dict] = Field(default_factory=dict)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Misinformation Detection Models
class MisinformationIndicator(BaseModel):
    """Individual misinformation indicator"""
    indicator_type: str = Field(..., description="Type of indicator")
    category: str = Field(..., description="Indicator category")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    description: str = Field(..., description="Human-readable description")
    severity: RiskSeverity = Field(..., description="Severity level")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence")
    detection_method: str = Field(..., description="Detection method used")

class SourceAnalysis(BaseModel):
    """Source credibility analysis"""
    total_urls: int = Field(default=0)
    credible_sources: int = Field(default=0)
    unreliable_sources: int = Field(default=0)
    unknown_sources: int = Field(default=0)
    domain_analysis: List[Dict[str, str]] = Field(default_factory=list)
    credibility_score: float = Field(default=50, ge=0, le=100)

class FactCheckResult(BaseModel):
    """Fact-checking result"""
    source: str = Field(..., description="Fact-checking source")
    claim_reviewed: str = Field(..., description="Claim that was reviewed")
    rating: str = Field(..., description="Fact-check rating")
    confidence: float = Field(..., ge=0, le=1)
    review_url: Optional[str] = Field(None)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MisinformationAnalysis(BaseModel):
    """Complete misinformation analysis result"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User who made the request")
    content_hash: str = Field(..., description="Hash of analyzed content")
    
    # Detection results
    misinformation_indicators: List[MisinformationIndicator] = Field(default_factory=list)
    risk_score: float = Field(..., ge=0, le=100, description="Misinformation risk score")
    credibility_score: float = Field(..., ge=0, le=100, description="Content credibility score")
    severity: RiskSeverity = Field(..., description="Overall severity level")
    
    # Analysis components
    source_analysis: Optional[SourceAnalysis] = Field(None)
    fact_check_results: List[FactCheckResult] = Field(default_factory=list)
    content_analysis: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    detection_timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_methods: List[str] = Field(default_factory=list)
    processing_time_ms: Optional[float] = Field(None)
    urls_analyzed: List[str] = Field(default_factory=list)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Input Sanitization Models
class SecurityIssue(BaseModel):
    """Security issue detected during sanitization"""
    issue_type: str = Field(..., description="Type of security issue")
    severity: RiskSeverity = Field(..., description="Issue severity")
    description: str = Field(..., description="Issue description")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evidence: Optional[str] = Field(None, description="Evidence of the issue")

class SanitizationResult(BaseModel):
    """Input sanitization result"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User who made the request")
    
    # Input data
    input_type: str = Field(..., description="Type of input processed")
    original_input_hash: str = Field(..., description="Hash of original input")
    input_length: int = Field(..., description="Length of original input")
    
    # Sanitization results
    sanitized_input_hash: str = Field(..., description="Hash of sanitized input")
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    risk_score: float = Field(..., ge=0, le=100, description="Security risk score")
    is_safe: bool = Field(..., description="Whether input is safe for processing")
    
    # Processing metadata
    applied_filters: List[str] = Field(default_factory=list)
    sanitization_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = Field(None)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Comprehensive Risk Analysis Models
class RiskAnalysisRequest(BaseModel):
    """Risk analysis request model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User who made the request")
    
    # Request data
    input_text: str = Field(..., description="Original input text")
    input_type: str = Field(default="text", description="Type of input")
    context: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Request metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_ip: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MitigationAction(BaseModel):
    """Mitigation action taken"""
    action_type: MitigationAction = Field(..., description="Type of action taken")
    reason: str = Field(..., description="Reason for the action")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    automated: bool = Field(default=True, description="Whether action was automated")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional action details")

class RiskAnalysisResponse(BaseModel):
    """Comprehensive risk analysis response"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User who made the request")
    
    # Overall risk assessment
    overall_risk_score: float = Field(..., ge=0, le=100, description="Combined risk score")
    overall_severity: RiskSeverity = Field(..., description="Overall severity level")
    is_safe_for_processing: bool = Field(..., description="Whether content is safe")
    
    # Component analysis results
    pii_analysis_id: Optional[str] = Field(None, description="Reference to PII analysis")
    misinformation_analysis_id: Optional[str] = Field(None, description="Reference to misinformation analysis")
    sanitization_result_id: Optional[str] = Field(None, description="Reference to sanitization result")
    
    # Risk breakdown
    risk_categories: Dict[str, float] = Field(default_factory=dict)
    detected_risks: List[str] = Field(default_factory=list)
    
    # Mitigation
    recommended_actions: List[str] = Field(default_factory=list)
    applied_mitigations: List[MitigationAction] = Field(default_factory=list)
    
    # Processing metadata
    processing_status: DetectionStatus = Field(default=DetectionStatus.COMPLETED)
    total_processing_time_ms: float = Field(..., description="Total processing time")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Compliance and audit
    compliance_flags: List[str] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Rate Limiting and Security Models
class RateLimitViolation(BaseModel):
    """Rate limit violation record"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    identifier: str = Field(..., description="Rate limit identifier")
    client_ip: str = Field(..., description="Client IP address")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    
    # Violation details
    violation_type: str = Field(..., description="Type of rate limit violated")
    limit_exceeded: int = Field(..., description="Limit that was exceeded")
    actual_count: int = Field(..., description="Actual request count")
    time_window: int = Field(..., description="Time window in seconds")
    
    # Request context
    endpoint: str = Field(..., description="API endpoint accessed")
    method: str = Field(..., description="HTTP method")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    suspicion_score: float = Field(default=0, ge=0, le=1)
    action_taken: Optional[str] = Field(None, description="Action taken in response")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SecurityEvent(BaseModel):
    """General security event record"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    event_type: str = Field(..., description="Type of security event")
    severity: RiskSeverity = Field(..., description="Event severity")
    
    # Event details
    description: str = Field(..., description="Event description")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    
    # Event data
    event_data: Dict[str, Any] = Field(default_factory=dict)
    indicators: List[str] = Field(default_factory=list)
    
    # Response
    response_actions: List[str] = Field(default_factory=list)
    resolved: bool = Field(default=False)
    resolution_notes: Optional[str] = Field(None)
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    detection_method: str = Field(..., description="How the event was detected")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Analytics and Reporting Models
class RiskStatistics(BaseModel):
    """Risk analysis statistics"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    date: datetime = Field(..., description="Statistics date")
    
    # Request statistics
    total_requests: int = Field(default=0)
    successful_analyses: int = Field(default=0)
    failed_analyses: int = Field(default=0)
    
    # Risk distribution
    risk_distribution: Dict[str, int] = Field(default_factory=dict)  # severity -> count
    category_distribution: Dict[str, int] = Field(default_factory=dict)  # category -> count
    
    # Performance metrics
    avg_processing_time_ms: float = Field(default=0)
    max_processing_time_ms: float = Field(default=0)
    min_processing_time_ms: float = Field(default=0)
    
    # Security metrics
    security_incidents: int = Field(default=0)
    rate_limit_violations: int = Field(default=0)
    blocked_requests: int = Field(default=0)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Database Collections Configuration
COLLECTIONS = {
    'pii_analyses': PIIAnalysis,
    'misinformation_analyses': MisinformationAnalysis,
    'sanitization_results': SanitizationResult,
    'risk_analysis_requests': RiskAnalysisRequest,
    'risk_analysis_responses': RiskAnalysisResponse,
    'rate_limit_violations': RateLimitViolation,
    'security_events': SecurityEvent,
    'risk_statistics': RiskStatistics
}

# Database Indexes for Performance
DATABASE_INDEXES = {
    'pii_analyses': [
        [('request_id', 1)],
        [('user_id', 1)],
        [('detection_timestamp', -1)],
        [('severity', 1)],
        [('risk_score', -1)]
    ],
    'misinformation_analyses': [
        [('request_id', 1)],
        [('user_id', 1)],
        [('detection_timestamp', -1)],
        [('severity', 1)],
        [('risk_score', -1)],
        [('content_hash', 1)]
    ],
    'sanitization_results': [
        [('request_id', 1)],
        [('user_id', 1)],
        [('sanitization_timestamp', -1)],
        [('is_safe', 1)],
        [('risk_score', -1)]
    ],
    'risk_analysis_requests': [
        [('request_id', 1)],
        [('user_id', 1)],
        [('timestamp', -1)],
        [('client_ip', 1)]
    ],
    'risk_analysis_responses': [
        [('request_id', 1)],
        [('user_id', 1)],
        [('analysis_timestamp', -1)],
        [('overall_severity', 1)],
        [('overall_risk_score', -1)]
    ],
    'rate_limit_violations': [
        [('identifier', 1)],
        [('client_ip', 1)],
        [('timestamp', -1)],
        [('violation_type', 1)]
    ],
    'security_events': [
        [('event_type', 1)],
        [('severity', 1)],
        [('timestamp', -1)],
        [('source_ip', 1)],
        [('resolved', 1)]
    ],
    'risk_statistics': [
        [('date', -1)]
    ]
}
