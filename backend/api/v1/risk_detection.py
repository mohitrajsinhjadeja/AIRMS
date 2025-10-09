from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.requests import RiskAnalysisRequest
from schemas.responses import RiskAnalysisResponse
from services.risk.enhanced_pipeline import EnhancedRiskPipeline, get_enhanced_risk_pipeline
from api.middleware.rate_limiter import RateLimiter
from core.security import get_current_user
from utils.helpers import generate_request_id
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/risk", tags=["risk"])

# Initialize rate limiter
rate_limiter = RateLimiter()

@router.post("/analyze", response_model=dict)
async def analyze_risks(
    request: RiskAnalysisRequest,
    http_request: Request,
    current_user = Depends(get_current_user),
    risk_pipeline: EnhancedRiskPipeline = Depends(get_enhanced_risk_pipeline)
):
    """
    Comprehensive AI-powered risk analysis endpoint
    Detects PII, misinformation, security threats, and applies mitigation strategies
    """
    start_time = time.time()
    request_id = generate_request_id()
    
    try:
        # Apply rate limiting
        await rate_limiter.check_rate_limit(
            http_request, 
            current_user.id if current_user else None,
            'analysis_endpoint'
        )
        
        # Prepare analysis context
        context = {
            "request_id": request_id,
            "user_id": current_user.id if current_user else None,
            "timestamp": datetime.utcnow(),
            "client_ip": rate_limiter._get_client_ip(http_request),
            "user_agent": http_request.headers.get('user-agent', '')
        }
        
        logger.info(f"Starting risk analysis for request {request_id}")
        
        # Run comprehensive analysis
        result = await risk_pipeline.process_comprehensive_analysis(
            input_text=request.input,
            context=context,
            config=request.config
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Risk analysis completed for {request_id} in {processing_time:.2f}ms")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like rate limiting)
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Risk analysis failed for {request_id}: {e}", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Risk analysis failed",
                "request_id": request_id,
                "message": str(e),
                "processing_time_ms": processing_time
            }
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the risk analysis service"""
    return {
        "status": "healthy",
        "service": "risk_analysis",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "pii_detector": "operational",
            "misinformation_detector": "operational",
            "input_sanitizer": "operational",
            "rate_limiter": "operational"
        }
    }

@router.get("/stats/{user_id}")
async def get_user_risk_stats(
    user_id: str,
    current_user = Depends(get_current_user)
):
    """Get risk analysis statistics for a user"""
    # Verify user can access these stats
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get rate limit stats
    stats = await rate_limiter.get_rate_limit_stats(user_id)
    
    return {
        "user_id": user_id,
        "rate_limit_stats": stats,
        "timestamp": datetime.utcnow().isoformat()
    }