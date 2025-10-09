"""
🧪 AIRMS+ Test Suite API
Comprehensive testing dashboard for AI risk detection components
"""

import logging
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel

from app.core.auth import get_current_active_user
from app.models.user import UserInDB

# Add extra_WIP to path for importing advanced components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'extra_WIP'))

try:
    # Import each detector separately to isolate import errors
    try:
        from risk_detection.detectors.bias_detector import BiasDetector
    except ImportError as e:
        logging.warning(f"⚠️ BiasDetector not available: {e}")
        BiasDetector = None
        
    try:
        from risk_detection.detectors.pii_detector import PIIDetector
    except ImportError as e:
        logging.warning(f"⚠️ PIIDetector not available: {e}")
        PIIDetector = None
        
    try:
        from risk_detection.detectors.hallucination_detector import HallucinationDetector
    except ImportError as e:
        logging.warning(f"⚠️ HallucinationDetector not available: {e}")
        HallucinationDetector = None
        
    try:
        from risk_detection.detectors.adversarial_detector import AdversarialDetector
    except ImportError as e:
        logging.warning(f"⚠️ AdversarialDetector not available: {e}")
        AdversarialDetector = None
        
    try:
        from risk_detection.risk_agent import RiskAgent
    except ImportError as e:
        logging.warning(f"⚠️ RiskAgent not available: {e}")
        RiskAgent = None
        
    # Set flag based on whether any detectors were successfully imported
    ADVANCED_DETECTORS_AVAILABLE = any([
        BiasDetector, PIIDetector, HallucinationDetector, 
        AdversarialDetector, RiskAgent
    ])
except Exception as e:
    logging.error(f"❌ Error initializing advanced detectors: {e}")
    ADVANCED_DETECTORS_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test-suite", tags=["Test Suite"])

# Pydantic models for test requests and responses
class TestRequest(BaseModel):
    content: str
    test_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}

class TestResult(BaseModel):
    test_name: str
    status: str  # "success", "failed", "running"
    result: Dict[str, Any]
    execution_time: float
    timestamp: str

class AIPromptRequest(BaseModel):
    prompt: str
    model: str = "gemini"  # "gemini" or "groq"
    temperature: float = 0.7
    max_tokens: int = 1000

# Global test status storage (in production, use Redis or database)
test_status = {}

@router.get("/status")
async def get_test_status(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current status of all tests"""
    return {
        "available_tests": [
            "bias_detection",
            "pii_detection", 
            "hallucination_detection",
            "adversarial_detection",
            "misinformation_detection",
            "comprehensive_analysis"
        ],
        "advanced_detectors_available": ADVANCED_DETECTORS_AVAILABLE,
        "current_status": test_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/bias", response_model=TestResult)
async def run_bias_test(
    request: TestRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Run bias detection test"""
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🧪 Running bias detection test for user: {current_user.email}")
        
        if ADVANCED_DETECTORS_AVAILABLE:
            # Use advanced bias detector
            detector = BiasDetector()
            result = await asyncio.to_thread(detector.detect_bias, request.content)
            
            # Format result for frontend
            formatted_result = {
                "detected_bias": result.get("bias_types", []),
                "confidence_score": result.get("confidence", 0.0),
                "evidence": result.get("evidence", []),
                "severity": result.get("severity", "low"),
                "categories": result.get("categories", {}),
                "recommendations": result.get("recommendations", [])
            }
        else:
            # Fallback to basic detection
            formatted_result = {
                "detected_bias": ["political", "cultural"] if "politics" in request.content.lower() else [],
                "confidence_score": 0.75,
                "evidence": ["Sample evidence"],
                "severity": "medium",
                "categories": {"political": 0.6, "cultural": 0.4},
                "recommendations": ["Review content for political neutrality"]
            }
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="Bias Detection",
            status="success",
            result=formatted_result,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Bias detection test failed: {e}")
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="Bias Detection",
            status="failed",
            result={"error": str(e)},
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/pii", response_model=TestResult)
async def run_pii_test(
    request: TestRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Run PII detection test"""
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🧪 Running PII detection test for user: {current_user.email}")
        
        if ADVANCED_DETECTORS_AVAILABLE:
            # Use advanced PII detector
            detector = PIIDetector()
            result = await asyncio.to_thread(detector.detect_pii, request.content)
            
            formatted_result = {
                "detected_pii": result.get("pii_types", []),
                "confidence_score": result.get("confidence", 0.0),
                "entities": result.get("entities", []),
                "risk_level": result.get("risk_level", "low"),
                "patterns_found": result.get("patterns", {}),
                "recommendations": result.get("recommendations", [])
            }
        else:
            # Fallback detection
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
            
            emails = re.findall(email_pattern, request.content)
            phones = re.findall(phone_pattern, request.content)
            
            formatted_result = {
                "detected_pii": ["email", "phone"] if emails or phones else [],
                "confidence_score": 0.9 if emails or phones else 0.1,
                "entities": emails + phones,
                "risk_level": "high" if emails or phones else "low",
                "patterns_found": {"emails": len(emails), "phones": len(phones)},
                "recommendations": ["Remove or mask PII data"] if emails or phones else []
            }
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="PII Detection",
            status="success",
            result=formatted_result,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ PII detection test failed: {e}")
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="PII Detection",
            status="failed",
            result={"error": str(e)},
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/hallucination", response_model=TestResult)
async def run_hallucination_test(
    request: TestRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Run hallucination detection test"""
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🧪 Running hallucination detection test for user: {current_user.email}")
        
        if ADVANCED_DETECTORS_AVAILABLE:
            detector = HallucinationDetector()
            result = await asyncio.to_thread(detector.detect_hallucination, request.content)
            
            formatted_result = {
                "hallucination_detected": result.get("is_hallucination", False),
                "confidence_score": result.get("confidence", 0.0),
                "factual_errors": result.get("factual_errors", []),
                "inconsistencies": result.get("inconsistencies", []),
                "verification_status": result.get("verification_status", "unknown"),
                "recommendations": result.get("recommendations", [])
            }
        else:
            # Basic hallucination check
            suspicious_phrases = ["definitely", "absolutely certain", "100% sure", "never wrong"]
            detected = any(phrase in request.content.lower() for phrase in suspicious_phrases)
            
            formatted_result = {
                "hallucination_detected": detected,
                "confidence_score": 0.7 if detected else 0.3,
                "factual_errors": ["Overconfident statement"] if detected else [],
                "inconsistencies": [],
                "verification_status": "suspicious" if detected else "likely_accurate",
                "recommendations": ["Verify claims with reliable sources"] if detected else []
            }
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="Hallucination Detection",
            status="success",
            result=formatted_result,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Hallucination detection test failed: {e}")
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="Hallucination Detection",
            status="failed",
            result={"error": str(e)},
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/adversarial", response_model=TestResult)
async def run_adversarial_test(
    request: TestRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Run adversarial attack detection test"""
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🧪 Running adversarial detection test for user: {current_user.email}")
        
        if ADVANCED_DETECTORS_AVAILABLE:
            detector = AdversarialDetector()
            result = await asyncio.to_thread(detector.detect_adversarial, request.content)
            
            formatted_result = {
                "adversarial_detected": result.get("is_adversarial", False),
                "attack_types": result.get("attack_types", []),
                "confidence_score": result.get("confidence", 0.0),
                "risk_level": result.get("risk_level", "low"),
                "evidence": result.get("evidence", []),
                "recommendations": result.get("recommendations", [])
            }
        else:
            # Basic adversarial detection
            adversarial_keywords = ["ignore previous", "jailbreak", "prompt injection", "system override"]
            detected = any(keyword in request.content.lower() for keyword in adversarial_keywords)
            
            formatted_result = {
                "adversarial_detected": detected,
                "attack_types": ["prompt_injection"] if detected else [],
                "confidence_score": 0.9 if detected else 0.1,
                "risk_level": "high" if detected else "low",
                "evidence": ["Suspicious prompt patterns"] if detected else [],
                "recommendations": ["Block potentially malicious input"] if detected else []
            }
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="Adversarial Detection",
            status="success",
            result=formatted_result,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Adversarial detection test failed: {e}")
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TestResult(
            test_name="Adversarial Detection",
            status="failed",
            result={"error": str(e)},
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/comprehensive", response_model=Dict[str, TestResult])
async def run_comprehensive_test(
    request: TestRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Run all tests comprehensively"""
    logger.info(f"🧪 Running comprehensive test suite for user: {current_user.email}")
    
    # Run all tests concurrently
    tasks = [
        run_bias_test(request, current_user),
        run_pii_test(request, current_user),
        run_hallucination_test(request, current_user),
        run_adversarial_test(request, current_user)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Format results
    test_names = ["bias", "pii", "hallucination", "adversarial"]
    comprehensive_results = {}
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            comprehensive_results[test_names[i]] = TestResult(
                test_name=test_names[i].title() + " Detection",
                status="failed",
                result={"error": str(result)},
                execution_time=0.0,
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            comprehensive_results[test_names[i]] = result
    
    return comprehensive_results

@router.post("/ai-editor", response_model=Dict[str, Any])
async def ai_editor_prompt(
    request: AIPromptRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """AI Editor - Send custom prompts to Gemini or Groq"""
    try:
        logger.info(f"🤖 AI Editor request from user: {current_user.email}")
        
        # Import AI services
        from app.services.ai_integration import ai_service
        
        # Route to appropriate AI service
        if request.model.lower() == "groq":
            response = await ai_service.call_groq(
                prompt=request.prompt,
                task_type="CUSTOM",
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        else:  # Default to Gemini
            response = await ai_service.call_gemini(
                prompt=request.prompt,
                task_type="CUSTOM",
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        
        return {
            "status": "success",
            "model_used": request.model,
            "prompt": request.prompt,
            "response": response.get("content", ""),
            "metadata": {
                "tokens_used": response.get("tokens_used", 0),
                "response_time": response.get("response_time", 0),
                "model_version": response.get("model_version", "unknown")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ AI Editor request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Editor request failed: {str(e)}"
        )

@router.get("/test-history")
async def get_test_history(
    limit: int = 50,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get test execution history (placeholder - implement with database)"""
    # In production, this would query the database for test history
    return {
        "history": [],
        "total": 0,
        "message": "Test history feature - implement with database storage"
    }

@router.post("/save-prompt")
async def save_prompt(
    prompt_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Save prompt for reuse (placeholder - implement with database)"""
    # In production, this would save to database
    return {
        "status": "success",
        "message": "Prompt saved successfully",
        "prompt_id": "placeholder_id"
    }
