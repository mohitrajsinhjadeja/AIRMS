"""
Enterprise Risk Detection API Endpoints
Real-time AI-powered risk assessment with comprehensive functionality
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.auth import get_current_active_user, get_current_user
from app.models.user import UserInDB
from app.models.risk_assessment import (
    RiskAssessmentResponse,
    RiskAssessmentStats,
    RiskAssessmentFilter,
    BulkRiskAssessmentRequest,
    ContentType,
    RiskCategory,
    RiskSeverity
)
from app.services.risk_detection_service import risk_detection_service
from app.services.notification_service import notification_service
from app.models.notification import NotificationCreate
from app.services.risk_pipeline import RiskPipeline
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk-detection", tags=["Risk Detection"])
settings = get_settings()

risk_pipeline = RiskPipeline(
    mongodb_uri=settings.MONGODB_URI,
    llm_config=settings.LLM_CONFIG
)


class ContentAssessmentRequest(BaseModel):
    """Request model for content assessment"""
    content: str = Field(..., min_length=1, max_length=50000, description="Content to assess")
    content_type: ContentType = Field(ContentType.TEXT, description="Type of content")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    notify_on_high_risk: bool = Field(True, description="Send notification for high-risk content")


class BulkAssessmentStatus(BaseModel):
    """Status of bulk assessment job"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    total_items: int
    processed_items: int
    failed_items: int
    started_at: str
    completed_at: Optional[str] = None
    results_url: Optional[str] = None


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_content(
    request: ContentAssessmentRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Assess content for AI risks using multiple detection methods
    
    This endpoint provides real-time risk assessment for various content types
    including text, images, documents, and API requests.
    """
    try:
        # Prepare context with user information
        context = request.context or {}
        context.update({
            "user_id": str(current_user.id),
            "user_email": current_user.email,
            "organization_id": getattr(current_user, 'organization_id', None)
        })
        
        # Perform risk assessment
        assessment = await risk_detection_service.assess_content(
            content=request.content,
            content_type=request.content_type,
            user_id=str(current_user.id),
            context=context
        )
        
        # Send notification for high-risk content
        if (request.notify_on_high_risk and 
            assessment.risk_severity in ["high", "critical"]):
            
            background_tasks.add_task(
                send_risk_notification,
                assessment,
                current_user
            )
        
        logger.info(f"✅ Content assessed for user {current_user.email}: "
                   f"Score {assessment.risk_score}, Severity {assessment.risk_severity}")
        
        return assessment
        
    except Exception as e:
        logger.error(f"❌ Content assessment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment failed: {str(e)}"
        )


@router.post("/assess-bulk", response_model=Dict[str, str])
async def assess_content_bulk(
    request: BulkRiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Assess multiple content items in bulk (async processing)
    
    For large-scale content assessment with webhook callbacks
    """
    try:
        # Generate job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            process_bulk_assessment,
            job_id,
            request,
            str(current_user.id)
        )
        
        logger.info(f"✅ Bulk assessment job {job_id} started for user {current_user.email}")
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": f"Bulk assessment job started with {len(request.items)} items"
        }
        
    except Exception as e:
        logger.error(f"❌ Bulk assessment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk assessment failed: {str(e)}"
        )


@router.get("/assessments", response_model=List[RiskAssessmentResponse])
async def get_risk_assessments(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    min_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    max_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    severities: Optional[List[RiskSeverity]] = Query(None),
    categories: Optional[List[RiskCategory]] = Query(None),
    content_types: Optional[List[ContentType]] = Query(None),
    escalated_only: Optional[bool] = Query(False),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get risk assessments with advanced filtering
    
    Supports filtering by date range, risk scores, severities, categories, and more
    """
    try:
        from datetime import datetime
        
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format."
                )
        
        if end_date:
            try:
                parsed_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format."
                )
        
        # Create filter
        filter_params = RiskAssessmentFilter(
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            min_risk_score=min_risk_score,
            max_risk_score=max_risk_score,
            severities=severities,
            categories=categories,
            content_types=content_types,
            user_id=str(current_user.id),
            escalated_only=escalated_only,
            limit=limit,
            skip=skip
        )
        
        # Get assessments
        assessments = await risk_detection_service.get_assessments(filter_params)
        
        logger.info(f"✅ Retrieved {len(assessments)} risk assessments for user {current_user.email}")
        return assessments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get risk assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve risk assessments"
        )


@router.get("/stats", response_model=RiskAssessmentStats)
async def get_risk_statistics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get comprehensive risk assessment statistics
    
    Includes totals, averages, distributions, and performance metrics
    """
    try:
        stats = await risk_detection_service.get_stats(user_id=str(current_user.id))
        
        logger.info(f"✅ Retrieved risk statistics for user {current_user.email}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get risk statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve risk statistics"
        )


@router.get("/categories", response_model=List[Dict[str, str]])
async def get_risk_categories():
    """
    Get available risk categories with descriptions
    """
    categories = [
        {
            "value": RiskCategory.MISINFORMATION.value,
            "label": "Misinformation",
            "description": "False or misleading information"
        },
        {
            "value": RiskCategory.SECURITY_THREAT.value,
            "label": "Security Threat",
            "description": "Potential security vulnerabilities or attacks"
        },
        {
            "value": RiskCategory.ADVERSARIAL_ATTACK.value,
            "label": "Adversarial Attack",
            "description": "Attempts to manipulate AI systems"
        },
        {
            "value": RiskCategory.CONTENT_SAFETY.value,
            "label": "Content Safety",
            "description": "Harmful or inappropriate content"
        },
        {
            "value": RiskCategory.COMPLIANCE_VIOLATION.value,
            "label": "Compliance Violation",
            "description": "Violations of regulatory requirements"
        },
        {
            "value": RiskCategory.DATA_PRIVACY.value,
            "label": "Data Privacy",
            "description": "Privacy and data protection concerns"
        },
        {
            "value": RiskCategory.BIAS_DISCRIMINATION.value,
            "label": "Bias & Discrimination",
            "description": "Biased or discriminatory content"
        },
        {
            "value": RiskCategory.ANOMALY.value,
            "label": "Anomaly",
            "description": "Unusual patterns or behaviors"
        }
    ]
    
    return categories


@router.get("/severities", response_model=List[Dict[str, Any]])
async def get_risk_severities():
    """
    Get risk severity levels with score ranges
    """
    severities = [
        {
            "value": RiskSeverity.CRITICAL.value,
            "label": "Critical",
            "description": "Immediate action required",
            "score_range": "90-100",
            "color": "#dc2626"
        },
        {
            "value": RiskSeverity.HIGH.value,
            "label": "High",
            "description": "High priority attention needed",
            "score_range": "70-89",
            "color": "#ea580c"
        },
        {
            "value": RiskSeverity.MEDIUM.value,
            "label": "Medium",
            "description": "Moderate risk level",
            "score_range": "40-69",
            "color": "#d97706"
        },
        {
            "value": RiskSeverity.LOW.value,
            "label": "Low",
            "description": "Low risk, monitor",
            "score_range": "20-39",
            "color": "#65a30d"
        },
        {
            "value": RiskSeverity.MINIMAL.value,
            "label": "Minimal",
            "description": "Very low or no risk",
            "score_range": "0-19",
            "color": "#16a34a"
        }
    ]
    
    return severities


@router.get("/system-status", response_model=Dict[str, Any])
async def get_system_status():
    """
    Get risk detection system status and health metrics
    """
    try:
        # Check database connectivity
        from app.core.database import mongodb
        db_status = "connected" if mongodb.is_connected else "disconnected"
        
        # Get basic stats
        stats = await risk_detection_service.get_stats()
        
        # System health metrics
        status_info = {
            "status": "operational",
            "database": {
                "status": db_status,
                "collections": ["risk_assessments", "notifications", "users"]
            },
            "detection_engine": {
                "version": "1.0.0",
                "methods": ["pattern_matching", "anomaly_detection", "ml_classifier"],
                "categories": len(RiskCategory),
                "severities": len(RiskSeverity)
            },
            "performance": {
                "total_assessments": stats.total_assessments,
                "average_processing_time_ms": stats.average_processing_time_ms,
                "escalation_rate": stats.escalation_rate,
                "auto_mitigation_rate": stats.auto_mitigation_rate
            },
            "last_updated": "2025-01-21T06:24:00Z"
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"❌ Failed to get system status: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "last_updated": "2025-01-21T06:24:00Z"
        }


@router.post("/analyze")
async def analyze_input(
    request: Dict[str, Any],
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    try:
        result = await risk_pipeline.process_input(
            user_input=request["input"],
            user_id=current_user.id,
            db_config=request.get("db_config")
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


# Background task functions
async def send_risk_notification(assessment: RiskAssessmentResponse, user: UserInDB):
    """Send notification for high-risk content"""
    try:
        notification_data = NotificationCreate(
            title=f"{assessment.risk_severity.title()} Risk Detected",
            message=f"Content assessment scored {assessment.risk_score}/100 "
                   f"with {len(assessment.risk_categories)} risk categories detected",
            type="warning" if assessment.risk_severity == "high" else "error",
            category="risk",
            priority="high" if assessment.risk_severity == "high" else "critical",
            action_url=f"/dashboard/risk/assessments/{assessment.id}",
            metadata={
                "assessment_id": assessment.id,
                "risk_score": assessment.risk_score,
                "risk_categories": assessment.risk_categories
            },
            user_id=str(user.id)
        )
        
        await notification_service.create(notification_data)
        logger.info(f"✅ Risk notification sent to user {user.email}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send risk notification: {e}")


async def process_bulk_assessment(job_id: str, request: BulkRiskAssessmentRequest, user_id: str):
    """Process bulk assessment in background"""
    try:
        logger.info(f"🔄 Starting bulk assessment job {job_id}")
        
        results = []
        failed_items = 0
        
        for i, item in enumerate(request.items):
            try:
                # Extract content and type from item
                content = item.get("content", "")
                content_type = ContentType(item.get("content_type", "text"))
                context = item.get("context", {})
                
                # Perform assessment
                assessment = await risk_detection_service.assess_content(
                    content=content,
                    content_type=content_type,
                    user_id=user_id,
                    context=context
                )
                
                results.append({
                    "item_index": i,
                    "assessment": assessment.dict()
                })
                
            except Exception as e:
                logger.error(f"❌ Failed to assess item {i}: {e}")
                failed_items += 1
                results.append({
                    "item_index": i,
                    "error": str(e)
                })
        
        # Send completion notification
        completion_notification = NotificationCreate(
            title="Bulk Assessment Complete",
            message=f"Processed {len(request.items)} items. "
                   f"Success: {len(request.items) - failed_items}, Failed: {failed_items}",
            type="success" if failed_items == 0 else "warning",
            category="system",
            priority="medium",
            metadata={
                "job_id": job_id,
                "total_items": len(request.items),
                "failed_items": failed_items
            },
            user_id=user_id
        )
        
        await notification_service.create(completion_notification)
        
        # TODO: Store results and send webhook if callback_url provided
        logger.info(f"✅ Bulk assessment job {job_id} completed")
        
    except Exception as e:
        logger.error(f"❌ Bulk assessment job {job_id} failed: {e}")
        
        # Send failure notification
        failure_notification = NotificationCreate(
            title="Bulk Assessment Failed",
            message=f"Job {job_id} failed: {str(e)}",
            type="error",
            category="system",
            priority="high",
            metadata={"job_id": job_id, "error": str(e)},
            user_id=user_id
        )
        
        await notification_service.create(failure_notification)
