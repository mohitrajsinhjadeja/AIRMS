"""
🛡️ AIRMS+ Mitigation API Router
API endpoints for risk mitigation and reporting services
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.mitigation_service import get_mitigation_service, RiskReport, RiskLevel, RiskType, MitigationService
from app.core.database import get_database_operations, DatabaseOperations
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mitigation", tags=["Mitigation & Reporting"])

# Request/Response Models
class RiskAnalysisRequest(BaseModel):
    content: str = Field(..., description="Content to analyze for risks")
    risk_analysis: Dict[str, Any] = Field(..., description="Risk analysis results from detection engine")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")

class MitigationReportResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    report: RiskReport = Field(..., description="Generated risk report")
    message: str = Field(..., description="Response message")

class AnalyticsSummaryResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    analytics: Dict[str, Any] = Field(..., description="Analytics summary data")
    message: str = Field(..., description="Response message")

class ReportQueryRequest(BaseModel):
    days: Optional[int] = Field(30, description="Number of days to query", ge=1, le=365)
    risk_level: Optional[RiskLevel] = Field(None, description="Filter by risk level")
    risk_types: Optional[List[RiskType]] = Field(None, description="Filter by risk types")
    limit: Optional[int] = Field(100, description="Maximum number of reports", ge=1, le=1000)

@router.post("/generate-report", response_model=MitigationReportResponse)
async def generate_mitigation_report(
    request: RiskAnalysisRequest,
    background_tasks: BackgroundTasks,
    mitigation_service: MitigationService = Depends(get_mitigation_service),
    current_user: dict = Depends(get_current_user)
):
    """
    🛡️ Generate Comprehensive Risk Mitigation Report
    
    Analyzes risk detection results and generates structured mitigation strategies,
    compliance flags, immediate actions, and monitoring recommendations.
    
    **Features:**
    - Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)
    - Tailored mitigation strategies for each risk type
    - Compliance flags (GDPR, CCPA, etc.)
    - Immediate action recommendations
    - Long-term monitoring suggestions
    - MongoDB persistence for audit trails
    
    **Risk Types Supported:**
    - BIAS: Demographic, political, cultural bias detection
    - PII: Personal information exposure risks
    - HALLUCINATION: Fabricated or unverifiable content
    - ADVERSARIAL: Prompt injection, jailbreak attempts
    - MISINFORMATION: False or misleading information
    """
    try:
        logger.info(f"Generating mitigation report for user: {current_user.get('email', 'unknown')}")
        
        # Generate comprehensive risk report
        report = await mitigation_service.generate_risk_report(
            content=request.content,
            risk_analysis=request.risk_analysis,
            user_context=request.user_context
        )
        
        # Log successful report generation
        logger.info(f"Risk report generated successfully: {report.report_id}")
        
        return MitigationReportResponse(
            success=True,
            report=report,
            message=f"Risk mitigation report generated successfully. Report ID: {report.report_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to generate mitigation report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate mitigation report: {str(e)}"
        )

@router.get("/analytics", response_model=AnalyticsSummaryResponse)
async def get_mitigation_analytics(
    days: int = 30,
    mitigation_service: MitigationService = Depends(get_mitigation_service),
    current_user: dict = Depends(get_current_user)
):
    """
    📊 Get Mitigation Analytics Summary
    
    Provides comprehensive analytics on risk reports and mitigation effectiveness
    over a specified time period.
    
    **Analytics Include:**
    - Total number of reports generated
    - Risk level distribution (LOW, MEDIUM, HIGH, CRITICAL)
    - Risk type frequency analysis
    - Average risk scores by category
    - Trend analysis and patterns
    - Mitigation strategy effectiveness
    
    **Parameters:**
    - days: Number of days to analyze (1-365, default: 30)
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        logger.info(f"Generating analytics summary for {days} days")
        
        # Get analytics summary
        analytics = await mitigation_service.get_analytics_summary(days=days)
        
        if not analytics:
            return AnalyticsSummaryResponse(
                success=True,
                analytics={
                    "period_days": days,
                    "total_reports": 0,
                    "message": "No data available for the specified period"
                },
                message="No analytics data available for the specified period"
            )
        
        return AnalyticsSummaryResponse(
            success=True,
            analytics=analytics,
            message=f"Analytics summary generated for {days} days"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate analytics summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics summary: {str(e)}"
        )

@router.get("/reports", response_model=Dict[str, Any])
async def get_risk_reports(
    days: int = 30,
    risk_level: Optional[str] = None,
    risk_types: Optional[str] = None,
    limit: int = 100,
    mitigation_service: MitigationService = Depends(get_mitigation_service),
    current_user: dict = Depends(get_current_user),
    db_ops: DatabaseOperations = Depends(get_database_operations)
):
    """
    📋 Get Risk Reports with Filtering
    
    Retrieves risk reports from MongoDB with optional filtering by risk level,
    risk types, and time period.
    
    **Query Parameters:**
    - days: Number of days to query (default: 30)
    - risk_level: Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)
    - risk_types: Comma-separated risk types (BIAS, PII, HALLUCINATION, etc.)
    - limit: Maximum number of reports to return (default: 100, max: 1000)
    
    **Returns:**
    - Filtered list of risk reports
    - Query metadata (total count, filters applied)
    - Pagination information
    """
    try:
        # Validate parameters
        if limit > 1000:
            limit = 1000
        
        # Build query filter
        query_filter = {}
        
        # Date range filter
        if days > 0:
            from datetime import datetime, timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            query_filter["timestamp"] = {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        
        # Risk level filter
        if risk_level and risk_level.upper() in RiskLevel.__members__:
            query_filter["risk_level"] = risk_level.upper()
        
        # Risk types filter
        if risk_types:
            risk_type_list = [rt.strip().upper() for rt in risk_types.split(",")]
            valid_risk_types = [rt for rt in risk_type_list if rt in RiskType.__members__]
            if valid_risk_types:
                query_filter["risk_types"] = {"$in": valid_risk_types}
        
        logger.info(f"Querying risk reports with filter: {query_filter}")
        
        # Query reports from MongoDB
        reports = await db_ops.find_documents(
            collection="risk_reports",
            query=query_filter,
            limit=limit,
            sort=[("timestamp", -1)]  # Sort by newest first
        )
        
        # Get total count for pagination
        total_count = await db_ops.count_documents("risk_reports", query_filter)
        
        return {
            "success": True,
            "reports": reports,
            "metadata": {
                "total_count": total_count,
                "returned_count": len(reports),
                "query_parameters": {
                    "days": days,
                    "risk_level": risk_level,
                    "risk_types": risk_types,
                    "limit": limit
                },
                "filters_applied": query_filter,
                "generated_at": datetime.utcnow().isoformat()
            },
            "message": f"Retrieved {len(reports)} risk reports"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve risk reports: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve risk reports: {str(e)}"
        )

@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_risk_report_by_id(
    report_id: str,
    mitigation_service: MitigationService = Depends(get_mitigation_service),
    current_user: dict = Depends(get_current_user),
    db_ops: DatabaseOperations = Depends(get_database_operations)
):
    """
    📄 Get Specific Risk Report by ID
    
    Retrieves a specific risk report by its unique identifier.
    
    **Parameters:**
    - report_id: Unique report identifier
    
    **Returns:**
    - Complete risk report with all mitigation strategies
    - Report metadata and generation details
    """
    try:
        logger.info(f"Retrieving risk report: {report_id}")
        
        # Query specific report
        report = await db_ops.find_document(
            collection="risk_reports",
            query={"report_id": report_id}
        )
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Risk report not found: {report_id}"
            )
        
        return {
            "success": True,
            "report": report,
            "message": f"Risk report retrieved successfully: {report_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve risk report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve risk report: {str(e)}"
        )

@router.delete("/reports/{report_id}")
async def delete_risk_report(
    report_id: str,
    mitigation_service: MitigationService = Depends(get_mitigation_service),
    current_user: dict = Depends(get_current_user),
    db_ops: DatabaseOperations = Depends(get_database_operations)
):
    """
    🗑️ Delete Risk Report
    
    Deletes a specific risk report from the database.
    Requires admin privileges for data governance compliance.
    
    **Parameters:**
    - report_id: Unique report identifier to delete
    
    **Security:**
    - Admin role required
    - Audit log entry created
    - Soft delete with retention period
    """
    try:
        # Check admin privileges
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to delete risk reports"
            )
        
        logger.info(f"Deleting risk report: {report_id} by admin: {current_user.get('email')}")
        
        # Check if report exists
        existing_report = await db_ops.find_document(
            collection="risk_reports",
            query={"report_id": report_id}
        )
        
        if not existing_report:
            raise HTTPException(
                status_code=404,
                detail=f"Risk report not found: {report_id}"
            )
        
        # Soft delete - mark as deleted instead of removing
        await db_ops.update_document(
            collection="risk_reports",
            query={"report_id": report_id},
            update={
                "$set": {
                    "deleted": True,
                    "deleted_at": datetime.utcnow().isoformat(),
                    "deleted_by": current_user.get("email")
                }
            }
        )
        
        logger.info(f"Risk report soft-deleted successfully: {report_id}")
        
        return {
            "success": True,
            "message": f"Risk report deleted successfully: {report_id}",
            "report_id": report_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete risk report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete risk report: {str(e)}"
        )

@router.get("/strategies", response_model=Dict[str, Any])
async def get_mitigation_strategies(
    risk_type: Optional[str] = None,
    mitigation_service: MitigationService = Depends(get_mitigation_service),
    current_user: dict = Depends(get_current_user)
):
    """
    🛠️ Get Available Mitigation Strategies
    
    Returns available mitigation strategies, optionally filtered by risk type.
    
    **Parameters:**
    - risk_type: Optional filter by risk type (BIAS, PII, HALLUCINATION, etc.)
    
    **Returns:**
    - List of mitigation strategies with implementation details
    - Strategy metadata (priority, effort, impact, timeline)
    - Implementation steps and required resources
    """
    try:
        logger.info(f"Retrieving mitigation strategies, filter: {risk_type}")
        
        strategies = mitigation_service.strategies
        
        # Filter by risk type if specified
        if risk_type and risk_type.upper() in RiskType.__members__:
            risk_type_enum = RiskType(risk_type.upper())
            filtered_strategies = {risk_type_enum: strategies.get(risk_type_enum, [])}
        else:
            filtered_strategies = strategies
        
        # Convert to serializable format
        result = {}
        for rt, strats in filtered_strategies.items():
            result[rt.value] = [strat.dict() for strat in strats]
        
        return {
            "success": True,
            "strategies": result,
            "total_strategies": sum(len(strats) for strats in result.values()),
            "risk_types_available": list(result.keys()),
            "message": f"Retrieved mitigation strategies" + (f" for {risk_type}" if risk_type else "")
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve mitigation strategies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve mitigation strategies: {str(e)}"
        )

@router.get("/health")
async def mitigation_service_health(
    mitigation_service: MitigationService = Depends(get_mitigation_service)
):
    """
    🏥 Mitigation Service Health Check
    
    Checks the health and status of the mitigation service components.
    """
    try:
        # Test database connectivity
        db_health = await mitigation_service.db_ops.health_check() if hasattr(mitigation_service.db_ops, 'health_check') else {"status": "unknown"}
        
        # Check strategy loading
        strategies_loaded = len(mitigation_service.strategies) > 0
        total_strategies = sum(len(strats) for strats in mitigation_service.strategies.values())
        
        return {
            "status": "healthy",
            "service": "mitigation_service",
            "components": {
                "database": db_health.get("status", "unknown"),
                "strategies_loaded": strategies_loaded,
                "total_strategies": total_strategies
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mitigation service health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "mitigation_service",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
