"""
🔍 Fact-Checking API Endpoints
Comprehensive misinformation detection and verification
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.services.fact_checking import fact_check_claim, ComprehensiveFactChecker, FactCheckStatus, FactCheckingService
from app.core.database import get_database_operations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fact-checking", tags=["Fact Checking"])

# Pydantic models
class FactCheckRequest(BaseModel):
    claim: str = Field(..., description="The claim to fact-check", min_length=10, max_length=1000)
    context: Optional[str] = Field(None, description="Additional context for the claim", max_length=2000)
    save_result: bool = Field(True, description="Whether to save the result to database")

class BulkFactCheckRequest(BaseModel):
    claims: List[str] = Field(..., description="List of claims to fact-check", max_items=10)
    context: Optional[str] = Field(None, description="Shared context for all claims")
    save_results: bool = Field(True, description="Whether to save results to database")

class FactCheckResponse(BaseModel):
    claim: str
    status: str
    confidence: float
    sources_count: int
    evidence_count: int
    contradictions_count: int
    explanation: str
    sources: List[Dict[str, Any]]
    evidence: List[str]
    contradictions: List[str]
    timestamp: str
    processing_time_ms: int

class BulkFactCheckResponse(BaseModel):
    total_claims: int
    processed_claims: int
    results: List[FactCheckResponse]
    processing_time_ms: int
    summary: Dict[str, Any]

@router.post("/check", response_model=FactCheckResponse)
async def fact_check_single_claim(
    request: FactCheckRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🔍 Fact-Check Single Claim
    
    Performs comprehensive fact-checking using multiple sources including
    Google Fact Check API, NewsAPI, and Wikipedia.
    """
    start_time = datetime.utcnow()
    
    try:
        # Perform fact-checking
        result = await fact_check_claim(request.claim, request.context)
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Save to database if requested
        if request.save_result:
            background_tasks.add_task(
                _save_fact_check_result,
                result,
                current_user.get("id"),
                processing_time
            )
        
        return FactCheckResponse(
            claim=result.claim,
            status=result.status.value,
            confidence=result.confidence,
            sources_count=len(result.sources),
            evidence_count=len(result.evidence),
            contradictions_count=len(result.contradictions),
            explanation=result.explanation,
            sources=result.sources,
            evidence=result.evidence,
            contradictions=result.contradictions,
            timestamp=result.timestamp.isoformat(),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Fact-checking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fact-checking failed: {str(e)}")

@router.post("/check-bulk", response_model=BulkFactCheckResponse)
async def fact_check_multiple_claims(
    request: BulkFactCheckRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🔍 Bulk Fact-Check Multiple Claims
    
    Efficiently processes multiple claims in parallel for batch verification.
    """
    start_time = datetime.utcnow()
    
    try:
        results = []
        
        # Process claims in parallel
        async with ComprehensiveFactChecker() as checker:
            import asyncio
            
            tasks = [
                checker.comprehensive_fact_check(claim, request.context)
                for claim in request.claims
            ]
            
            fact_check_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(fact_check_results):
                if isinstance(result, Exception):
                    logger.error(f"Fact-check failed for claim {i}: {result}")
                    continue
                
                claim_processing_time = 100  # Approximate per-claim time
                
                results.append(FactCheckResponse(
                    claim=result.claim,
                    status=result.status.value,
                    confidence=result.confidence,
                    sources_count=len(result.sources),
                    evidence_count=len(result.evidence),
                    contradictions_count=len(result.contradictions),
                    explanation=result.explanation,
                    sources=result.sources,
                    evidence=result.evidence,
                    contradictions=result.contradictions,
                    timestamp=result.timestamp.isoformat(),
                    processing_time_ms=claim_processing_time
                ))
                
                # Save to database if requested
                if request.save_results:
                    background_tasks.add_task(
                        _save_fact_check_result,
                        result,
                        current_user.get("id"),
                        claim_processing_time
                    )
        
        total_processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Generate summary
        summary = _generate_bulk_summary(results)
        
        return BulkFactCheckResponse(
            total_claims=len(request.claims),
            processed_claims=len(results),
            results=results,
            processing_time_ms=total_processing_time,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Bulk fact-checking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk fact-checking failed: {str(e)}")

@router.get("/history")
async def get_fact_check_history(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📋 Get Fact-Check History
    
    Retrieve user's fact-checking history with filtering options.
    """
    try:
        db_ops = await get_database_operations()
        user_id = str(current_user.get("id"))
        
        # Build query
        query = {"user_id": user_id}
        if status_filter:
            query["status"] = status_filter
        
        # Get fact-check history
        fact_checks = await db_ops.db.fact_check_results.find(query) \
            .sort("timestamp", -1) \
            .skip(offset) \
            .limit(limit) \
            .to_list(length=limit)
        
        # Get total count
        total_count = await db_ops.db.fact_check_results.count_documents(query)
        
        return {
            "fact_checks": fact_checks,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(fact_checks) < total_count
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve fact-check history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@router.get("/statistics")
async def get_fact_check_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📊 Get Fact-Check Statistics
    
    Retrieve comprehensive statistics about fact-checking activities.
    """
    try:
        db_ops = await get_database_operations()
        user_id = str(current_user.get("id"))
        
        # User statistics
        user_stats = await db_ops.db.fact_check_results.aggregate([
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"}
                }
            }
        ]).to_list(length=10)
        
        # System-wide statistics (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        system_stats = await db_ops.db.fact_check_results.aggregate([
            {"$match": {"timestamp": {"$gte": thirty_days_ago}}},
            {
                "$group": {
                    "_id": None,
                    "total_checks": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"},
                    "avg_processing_time": {"$avg": "$processing_time_ms"}
                }
            }
        ]).to_list(length=1)
        
        # Status distribution
        status_distribution = {}
        total_user_checks = 0
        
        for stat in user_stats:
            status = stat["_id"]
            count = stat["count"]
            status_distribution[status] = {
                "count": count,
                "avg_confidence": round(stat["avg_confidence"], 2)
            }
            total_user_checks += count
        
        return {
            "user_statistics": {
                "total_fact_checks": total_user_checks,
                "status_distribution": status_distribution,
                "most_common_status": max(status_distribution.keys(), key=lambda k: status_distribution[k]["count"]) if status_distribution else None
            },
            "system_statistics": {
                "total_checks_30_days": system_stats[0]["total_checks"] if system_stats else 0,
                "avg_confidence_30_days": round(system_stats[0]["avg_confidence"], 2) if system_stats else 0.0,
                "avg_processing_time_ms": round(system_stats[0]["avg_processing_time"], 2) if system_stats else 0.0
            },
            "source_reliability": {
                "google_fact_check": "high",
                "newsapi": "medium", 
                "wikipedia": "high"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@router.get("/sources/status")
async def get_fact_check_sources_status():
    """
    🔧 Get Fact-Check Sources Status
    
    Check the availability and configuration of fact-checking sources.
    """
    try:
        from app.core.config import settings
        
        sources_status = {
            "google_fact_check": {
                "enabled": settings.GOOGLE_FACT_CHECK_ENABLED,
                "configured": bool(settings.GOOGLE_FACT_CHECK_API_KEY),
                "reliability": "high",
                "description": "Google Fact Check Tools API for verified fact-checks"
            },
            "newsapi": {
                "enabled": settings.NEWSAPI_ENABLED,
                "configured": bool(settings.NEWSAPI_KEY),
                "reliability": "medium",
                "description": "NewsAPI for recent news coverage analysis"
            },
            "wikipedia": {
                "enabled": settings.WIKIPEDIA_ENABLED,
                "configured": True,  # No API key required
                "reliability": "high",
                "description": "Wikipedia knowledge base for entity verification"
            }
        }
        
        # Count enabled sources
        enabled_sources = sum(1 for source in sources_status.values() if source["enabled"] and source["configured"])
        
        return {
            "sources": sources_status,
            "enabled_sources_count": enabled_sources,
            "system_status": "operational" if enabled_sources > 0 else "limited",
            "recommendations": _get_source_recommendations(sources_status)
        }
        
    except Exception as e:
        logger.error(f"Failed to get sources status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sources status: {str(e)}")

@router.post("/test")
async def test_fact_checking_system():
    """
    🧪 Test Fact-Checking System
    
    Run a comprehensive test of the fact-checking system with sample claims.
    """
    try:
        test_claims = [
            "The Earth is round",
            "Water boils at 100 degrees Celsius at sea level",
            "The COVID-19 vaccine contains microchips"
        ]
        
        results = []
        
        for claim in test_claims:
            try:
                result = await fact_check_claim(claim)
                results.append({
                    "claim": claim,
                    "status": result.status.value,
                    "confidence": result.confidence,
                    "sources_used": len(result.sources),
                    "processing_successful": True
                })
            except Exception as e:
                results.append({
                    "claim": claim,
                    "status": "error",
                    "confidence": 0.0,
                    "sources_used": 0,
                    "processing_successful": False,
                    "error": str(e)
                })
        
        successful_tests = sum(1 for r in results if r["processing_successful"])
        
        return {
            "test_results": results,
            "total_tests": len(test_claims),
            "successful_tests": successful_tests,
            "success_rate": successful_tests / len(test_claims),
            "system_health": "healthy" if successful_tests == len(test_claims) else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fact-checking system test failed: {e}")
        raise HTTPException(status_code=500, detail=f"System test failed: {str(e)}")

# New verification endpoint
@router.post("/verify", response_model=FactCheckResponse)
async def verify_facts(
    request: FactCheckRequest,
    current_user = Depends(get_current_user),
    fact_service: FactCheckingService = Depends()
):
    """
    🔍 Verify Facts
    
    Quickly verify facts using multiple trusted sources.
    """
    try:
        result = await fact_service.verify(request.claim)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fact checking failed: {str(e)}"
        )

# Helper functions
async def _save_fact_check_result(result, user_id: str, processing_time: int):
    """Save fact-check result to database"""
    try:
        db_ops = await get_database_operations()
        
        fact_check_data = {
            "user_id": user_id,
            "claim": result.claim,
            "status": result.status.value,
            "confidence": result.confidence,
            "sources": result.sources,
            "evidence": result.evidence,
            "contradictions": result.contradictions,
            "explanation": result.explanation,
            "processing_time_ms": processing_time,
            "timestamp": result.timestamp,
            "created_at": datetime.utcnow()
        }
        
        await db_ops.db.fact_check_results.insert_one(fact_check_data)
        
    except Exception as e:
        logger.error(f"Failed to save fact-check result: {e}")

def _generate_bulk_summary(results: List[FactCheckResponse]) -> Dict[str, Any]:
    """Generate summary for bulk fact-check results"""
    if not results:
        return {"message": "No results to summarize"}
    
    status_counts = {}
    total_confidence = 0.0
    total_sources = 0
    total_evidence = 0
    total_contradictions = 0
    
    for result in results:
        status = result.status
        status_counts[status] = status_counts.get(status, 0) + 1
        total_confidence += result.confidence
        total_sources += result.sources_count
        total_evidence += result.evidence_count
        total_contradictions += result.contradictions_count
    
    return {
        "status_distribution": status_counts,
        "average_confidence": round(total_confidence / len(results), 2),
        "total_sources_consulted": total_sources,
        "total_evidence_found": total_evidence,
        "total_contradictions_found": total_contradictions,
        "most_common_status": max(status_counts.keys(), key=status_counts.get) if status_counts else None
    }

def _get_source_recommendations(sources_status: Dict[str, Any]) -> List[str]:
    """Get recommendations for improving fact-checking capabilities"""
    recommendations = []
    
    if not sources_status["google_fact_check"]["configured"]:
        recommendations.append("Configure Google Fact Check API key for enhanced fact-checking accuracy")
    
    if not sources_status["newsapi"]["configured"]:
        recommendations.append("Configure NewsAPI key for recent news coverage analysis")
    
    enabled_count = sum(1 for source in sources_status.values() if source["enabled"] and source["configured"])
    
    if enabled_count == 0:
        recommendations.append("Enable at least one fact-checking source for basic functionality")
    elif enabled_count == 1:
        recommendations.append("Enable multiple sources for more comprehensive fact-checking")
    
    return recommendations
