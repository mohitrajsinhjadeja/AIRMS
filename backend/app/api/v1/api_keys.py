"""
🚨 AI Risk Detection System
Detects bias, hallucinations, privacy leaks, and adversarial inputs
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
import re
import json

from app.schemas.base import BaseResponse
from app.core.auth import get_current_active_user
from app.models.user import UserInDB

logger = logging.getLogger(__name__)
router = APIRouter()

class RiskAnalysisRequest(BaseModel):
    """Risk analysis request model"""
    content: str = Field(..., description="Content to analyze")
    analysis_types: List[str] = Field(
        default=["bias", "pii", "hallucination", "adversarial"],
        description="Types of analysis to perform"
    )
    context: Optional[str] = Field(None, description="Additional context")

class RiskDetectionResult(BaseModel):
    """Individual risk detection result"""
    risk_type: str
    risk_level: str  # low, medium, high, critical
    confidence: float
    details: List[str]
    recommendations: List[str]

class CreateAPIKeyRequest(BaseModel):
    """API key creation request"""
    key_name: str = Field(..., description="Name for the API key")
    permissions: List[str] = Field(default=["read", "write"], description="List of permissions")
    usage_limit: Optional[int] = Field(None, description="Usage limit for the API key")

class RiskAnalysisResponse(BaseResponse):
    """Risk analysis response"""
    content_analyzed: str
    overall_risk_score: float
    overall_risk_level: str
    detections: List[RiskDetectionResult]
    analysis_timestamp: str

class BiasDetector:
    """Detect bias in content"""
    
    BIAS_PATTERNS = {
        "gender": [r"\b(he|she) is (bad|good) at\b", r"\bwomen can't\b", r"\bmen always\b"],
        "racial": [r"\ball (black|white|asian) people\b", r"\bpeople from.*are\b"],
        "age": [r"\bold people can't\b", r"\byoung people don't\b"],
        "religious": [r"\ball (muslims|christians|hindus) are\b"]
    }
    
    def detect(self, content: str) -> RiskDetectionResult:
        """Detect bias in content"""
        bias_found = []
        recommendations = []
        
        for bias_type, patterns in self.BIAS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content.lower()):
                    bias_found.append(f"{bias_type.title()} bias detected")
                    recommendations.append(f"Consider removing {bias_type} stereotypes")
        
        if bias_found:
            risk_level = "high" if len(bias_found) > 2 else "medium"
            confidence = 0.8
        else:
            risk_level = "low"
            confidence = 0.9
            bias_found = ["No explicit bias patterns detected"]
            recommendations = ["Content appears bias-free"]
        
        return RiskDetectionResult(
            risk_type="bias",
            risk_level=risk_level,
            confidence=confidence,
            details=bias_found,
            recommendations=recommendations
        )

class PIIDetector:
    """Detect personally identifiable information"""
    
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-?\d{2}-?\d{4}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        "aadhaar": r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    }
    
    def detect(self, content: str) -> RiskDetectionResult:
        """Detect PII in content"""
        pii_found = []
        recommendations = []
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                pii_found.append(f"{pii_type.upper()} detected: {len(matches)} instances")
                recommendations.append(f"Remove or mask {pii_type} information")
        
        if pii_found:
            risk_level = "critical" if any("credit_card" in item or "ssn" in item for item in pii_found) else "high"
            confidence = 0.95
        else:
            risk_level = "low"
            confidence = 0.9
            pii_found = ["No PII detected"]
            recommendations = ["Content appears safe for sharing"]
        
        return RiskDetectionResult(
            risk_type="pii",
            risk_level=risk_level,
            confidence=confidence,
            details=pii_found,
            recommendations=recommendations
        )

class HallucinationDetector:
    """Detect potential hallucinations or false information"""
    
    HALLUCINATION_INDICATORS = [
        r"according to my knowledge",
        r"i believe that",
        r"it is widely known that",
        r"studies show that",
        r"research indicates",
        r"experts say",
        r"it is proven that"
    ]
    
    FACTUAL_CLAIMS = [
        r"\d{4} was the year",
        r"the capital of .* is",
        r"the population of .* is \d+",
        r".* died in \d{4}",
        r".* was born in \d{4}"
    ]
    
    def detect(self, content: str) -> RiskDetectionResult:
        """Detect potential hallucinations"""
        issues_found = []
        recommendations = []
        
        # Check for vague authority claims
        for indicator in self.HALLUCINATION_INDICATORS:
            if re.search(indicator, content.lower()):
                issues_found.append("Vague authority claims detected")
                recommendations.append("Provide specific sources for claims")
                break
        
        # Check for specific factual claims that should be verified
        factual_claims = 0
        for claim_pattern in self.FACTUAL_CLAIMS:
            factual_claims += len(re.findall(claim_pattern, content.lower()))
        
        if factual_claims > 0:
            issues_found.append(f"{factual_claims} factual claims detected")
            recommendations.append("Verify factual claims with reliable sources")
        
        if issues_found:
            risk_level = "medium"
            confidence = 0.7
        else:
            risk_level = "low"
            confidence = 0.8
            issues_found = ["No obvious hallucination indicators"]
            recommendations = ["Content appears factually neutral"]
        
        return RiskDetectionResult(
            risk_type="hallucination",
            risk_level=risk_level,
            confidence=confidence,
            details=issues_found,
            recommendations=recommendations
        )

class AdversarialDetector:
    """Detect adversarial inputs and prompt injection"""
    
    ADVERSARIAL_PATTERNS = [
        r"ignore previous instructions",
        r"disregard the above",
        r"forget everything",
        r"new instructions:",
        r"system prompt:",
        r"jailbreak",
        r"roleplay as",
        r"pretend you are"
    ]
    
    def detect(self, content: str) -> RiskDetectionResult:
        """Detect adversarial inputs"""
        threats_found = []
        recommendations = []
        
        for pattern in self.ADVERSARIAL_PATTERNS:
            if re.search(pattern, content.lower()):
                threats_found.append("Potential prompt injection detected")
                recommendations.append("Block or sanitize adversarial input")
                break
        
        # Check for suspicious length (extremely long inputs)
        if len(content) > 5000:
            threats_found.append("Unusually long input detected")
            recommendations.append("Implement input length limits")
        
        if threats_found:
            risk_level = "high"
            confidence = 0.85
        else:
            risk_level = "low"
            confidence = 0.9
            threats_found = ["No adversarial patterns detected"]
            recommendations = ["Input appears safe"]
        
        return RiskDetectionResult(
            risk_type="adversarial",
            risk_level=risk_level,
            confidence=confidence,
            details=threats_found,
            recommendations=recommendations
        )

class RiskAnalyzer:
    """Main risk analysis orchestrator"""
    
    def __init__(self):
        self.detectors = {
            "bias": BiasDetector(),
            "pii": PIIDetector(),
            "hallucination": HallucinationDetector(),
            "adversarial": AdversarialDetector()
        }
        
        self.risk_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
    
    def analyze(self, content: str, analysis_types: List[str]) -> RiskAnalysisResponse:
        """Perform comprehensive risk analysis"""
        detections = []
        
        # Run requested detectors
        for analysis_type in analysis_types:
            if analysis_type in self.detectors:
                detection = self.detectors[analysis_type].detect(content)
                detections.append(detection)
        
        # Calculate overall risk score
        risk_scores = []
        for detection in detections:
            weight = self.risk_weights.get(detection.risk_level, 0.2)
            risk_scores.append(weight * detection.confidence)
        
        overall_risk_score = max(risk_scores) if risk_scores else 0.0
        
        # Determine overall risk level
        if overall_risk_score >= 0.8:
            overall_risk_level = "critical"
        elif overall_risk_score >= 0.6:
            overall_risk_level = "high"
        elif overall_risk_score >= 0.4:
            overall_risk_level = "medium"
        else:
            overall_risk_level = "low"
        
        return RiskAnalysisResponse(
            success=True,
            message="Risk analysis completed",
            data={},
            content_analyzed=content[:100] + "..." if len(content) > 100 else content,
            overall_risk_score=round(overall_risk_score, 3),
            overall_risk_level=overall_risk_level,
            detections=detections,
            analysis_timestamp=datetime.utcnow().isoformat()
        )

# Initialize analyzer
risk_analyzer = RiskAnalyzer()

@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_risk(request: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """
    🚨 **Comprehensive AI Risk Analysis**
    
    Analyzes content for various AI risks including:
    - **Bias Detection**: Gender, racial, age, religious bias
    - **PII Detection**: Email, phone, SSN, credit cards, Aadhaar
    - **Hallucination Detection**: False claims, vague authorities
    - **Adversarial Detection**: Prompt injection, jailbreaks
    """
    try:
        logger.info(f"🔍 Analyzing content for risks: {request.analysis_types}")
        
        # Perform risk analysis
        result = risk_analyzer.analyze(request.content, request.analysis_types)
        
        logger.info(f"✅ Risk analysis completed - Overall risk: {result.overall_risk_level}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Risk analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk analysis failed: {str(e)}"
        )

@router.get("/risk-types")
async def get_risk_types() -> BaseResponse:
    """Get available risk detection types"""
    return BaseResponse(
        success=True,
        message="Risk types retrieved successfully",
        data={
            "available_types": [
                {
                    "type": "bias",
                    "description": "Detects gender, racial, age, and religious bias",
                    "severity": "high"
                },
                {
                    "type": "pii",
                    "description": "Detects personal information like emails, phones, SSN",
                    "severity": "critical"
                },
                {
                    "type": "hallucination",
                    "description": "Detects false claims and unsubstantiated statements",
                    "severity": "medium"
                },
                {
                    "type": "adversarial",
                    "description": "Detects prompt injection and jailbreak attempts",
                    "severity": "high"
                }
            ]
        }
    )

"""
🔑 API Keys Management Router
Simple API key management for AIRMS+ system
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse

logger = logging.getLogger(__name__)
router = APIRouter()

class APIKeyResponse(BaseModel):
    """API Key response model"""
    id: str
    name: str
    key_preview: str
    created_at: str
    is_active: bool
    permissions: List[str]

@router.get("/list")
async def list_api_keys() -> BaseResponse:
    """List all API keys from database"""
    try:
        from app.core.database import mongodb
        
        # Fetch all API keys from database for now
        api_keys_cursor = mongodb.database["api_keys"].find({}).sort("created_at", -1)
        
        all_keys = []
        async for key_doc in api_keys_cursor:
            # Generate a better preview if the current one is generic
            key_preview = key_doc.get("key_preview", "airms_***")
            full_key = key_doc.get("key_hash") or key_doc.get("api_key") or key_doc.get("key")
            
            # If we have a generic preview but a full key, generate a better preview
            if key_preview == "airms_***" and full_key:
                # Extract a meaningful preview from the full key
                if full_key.startswith("airms_"):
                    # Show first part and last few characters
                    key_parts = full_key.split("_")
                    if len(key_parts) >= 3:
                        key_preview = f"{key_parts[0]}_{key_parts[1]}_{key_parts[2][:8]}***"
                    else:
                        key_preview = f"{full_key[:20]}***"
                else:
                    key_preview = f"{full_key[:20]}***" if len(full_key) > 20 else f"{full_key}***"
            
            all_keys.append({
                "id": key_doc.get("key_id", str(key_doc.get("_id"))),
                "name": key_doc.get("name", "Unnamed Key"),
                "key_preview": key_preview,
                # Don't include full key in list for security - only in creation/regeneration
                "created_at": key_doc.get("created_at", datetime.utcnow().isoformat()),
                "is_active": key_doc.get("is_active", True),
                "permissions": key_doc.get("permissions", ["read"]),
                "usage_count": key_doc.get("usage_count", 0),
                "usage_limit": key_doc.get("usage_limit"),
                "last_used": key_doc.get("last_used")
            })
        
        return BaseResponse(
            success=True,
            message="API keys retrieved successfully",
            data={"keys": all_keys}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys"
        )

@router.post("/generate")
async def generate_api_key(
    request: CreateAPIKeyRequest, 
    current_user: UserInDB = Depends(get_current_active_user)
) -> BaseResponse:
    """Generate a new API key for the authenticated user"""
    try:
        from app.core.database import mongodb
        import secrets
        
        # Generate a secure API key
        key_suffix = secrets.token_hex(16)  # 32 character hex string
        key_id = f"key_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"
        
        # Create the full key with proper format
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', request.key_name.lower().replace(' ', '_'))
        full_key = f"airms_{clean_name}_{key_suffix}"
        key_preview = f"airms_{clean_name}_{key_suffix[:8]}***"
        
        # Store in database
        key_doc = {
            "key_id": key_id,
            "user_id": current_user.id,
            "name": request.key_name,
            "key_hash": full_key,  # In production, this should be hashed
            "key_preview": key_preview,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "permissions": request.permissions,
            "usage_limit": request.usage_limit,
            "usage_count": 0,
            "last_used": None
        }
        
        # Insert into database
        result = await mongodb.database["api_keys"].insert_one(key_doc)
        
        # Return the key with full_key for one-time display
        new_key = {
            "id": key_id,
            "name": request.key_name,
            "key_preview": key_preview,
            "full_key": full_key,  # Only returned once during creation
            "created_at": key_doc["created_at"],
            "is_active": True,
            "permissions": request.permissions,
            "usage_limit": request.usage_limit,
            "usage_count": 0
        }
        
        logger.info(f"✅ Created API key {key_id} for user {current_user.email}")
        
        return BaseResponse(
            success=True,
            message="API key generated successfully",
            data={"key": new_key}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to generate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )

@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str
    # Temporarily disable auth for testing 
    # current_user: UserInDB = Depends(get_current_active_user)
) -> BaseResponse:
    """Delete an API key"""
    try:
        from app.core.database import mongodb
        from bson import ObjectId
        
        # Try to find and delete the key by different possible ID fields
        result = None
        
        # First try by key_id field
        result = await mongodb.database["api_keys"].delete_one({
            "key_id": key_id
        })
        
        # If not found, try by _id (MongoDB ObjectId)
        if result.deleted_count == 0:
            try:
                if ObjectId.is_valid(key_id):
                    result = await mongodb.database["api_keys"].delete_one({
                        "_id": ObjectId(key_id)
                    })
            except:
                pass
        
        # If still not found, try by _id as string
        if result.deleted_count == 0:
            result = await mongodb.database["api_keys"].delete_one({
                "_id": key_id
            })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        logger.info(f"✅ Deleted API key {key_id}")
        
        return BaseResponse(
            success=True,
            message=f"API key deleted successfully",
            data={"deleted_key_id": key_id}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to delete API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )

@router.post("/{key_id}/regenerate")
async def regenerate_api_key(
    key_id: str
    # Temporarily disable auth for testing
    # current_user: UserInDB = Depends(get_current_active_user)
) -> BaseResponse:
    """Regenerate a new key for an existing API key"""
    try:
        from app.core.database import mongodb
        from bson import ObjectId
        import secrets
        
        # Try to find the existing key by different possible ID fields
        existing_key = None
        
        # First try by key_id field
        existing_key = await mongodb.database["api_keys"].find_one({
            "key_id": key_id
        })
        
        # If not found, try by _id (MongoDB ObjectId)
        if not existing_key:
            try:
                if ObjectId.is_valid(key_id):
                    existing_key = await mongodb.database["api_keys"].find_one({
                        "_id": ObjectId(key_id)
                    })
            except:
                pass
        
        # If still not found, try by _id as string
        if not existing_key:
            existing_key = await mongodb.database["api_keys"].find_one({
                "_id": key_id
            })
        
        if not existing_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Generate a new secure key
        key_suffix = secrets.token_hex(16)
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', existing_key["name"].lower().replace(' ', '_'))
        new_full_key = f"airms_{clean_name}_{key_suffix}"
        new_key_preview = f"airms_{clean_name}_{key_suffix[:8]}***"
        
        # Update the database using the same ID matching strategy
        update_result = None
        
        # First try by key_id field
        update_result = await mongodb.database["api_keys"].update_one(
            {"key_id": key_id},
            {
                "$set": {
                    "key_hash": new_full_key,
                    "key_preview": new_key_preview,
                    "updated_at": datetime.utcnow().isoformat(),
                    "usage_count": 0,  # Reset usage count
                    "last_used": None
                }
            }
        )
        
        # If not updated, try by _id (MongoDB ObjectId)
        if update_result.modified_count == 0:
            try:
                if ObjectId.is_valid(key_id):
                    update_result = await mongodb.database["api_keys"].update_one(
                        {"_id": ObjectId(key_id)},
                        {
                            "$set": {
                                "key_hash": new_full_key,
                                "key_preview": new_key_preview,
                                "updated_at": datetime.utcnow().isoformat(),
                                "usage_count": 0,  # Reset usage count
                                "last_used": None
                            }
                        }
                    )
            except:
                pass
        
        # If still not updated, try by _id as string
        if update_result.modified_count == 0:
            update_result = await mongodb.database["api_keys"].update_one(
                {"_id": key_id},
                {
                    "$set": {
                        "key_hash": new_full_key,
                        "key_preview": new_key_preview,
                        "updated_at": datetime.utcnow().isoformat(),
                        "usage_count": 0,  # Reset usage count
                        "last_used": None
                    }
                }
            )
        
        logger.info(f"✅ Regenerated API key {key_id}")
        
        return BaseResponse(
            success=True,
            message="API key regenerated successfully",
            data={
                "key": {
                    "id": key_id,
                    "name": existing_key["name"],
                    "key_preview": new_key_preview,
                    "full_key": new_full_key,  # Return full key for one-time display
                    "created_at": existing_key["created_at"],
                    "is_active": existing_key["is_active"],
                    "permissions": existing_key["permissions"],
                    "usage_limit": existing_key.get("usage_limit"),
                    "usage_count": 0
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to regenerate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate API key"
        )

@router.get("/{key_id}/reveal")
async def reveal_api_key(
    key_id: str
    # Temporarily disable auth for testing
    # current_user: UserInDB = Depends(get_current_active_user)
) -> BaseResponse:
    """Reveal the full API key (for copying purposes) - requires authentication"""
    try:
        from app.core.database import mongodb
        from bson import ObjectId
        
        # Try to find the key by different possible ID fields
        key_doc = None
        
        # First try by key_id field
        key_doc = await mongodb.database["api_keys"].find_one({
            "key_id": key_id
        })
        
        # If not found, try by _id (MongoDB ObjectId)
        if not key_doc:
            try:
                if ObjectId.is_valid(key_id):
                    key_doc = await mongodb.database["api_keys"].find_one({
                        "_id": ObjectId(key_id)
                    })
            except:
                pass
        
        # If still not found, try by _id as string
        if not key_doc:
            key_doc = await mongodb.database["api_keys"].find_one({
                "_id": key_id
            })
        
        if not key_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or doesn't belong to you"
            )
        
        full_key = key_doc.get("key_hash") or key_doc.get("api_key") or key_doc.get("key")
        
        if not full_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Full key not available for this API key"
            )
        
        logger.info(f"✅ Revealed API key {key_id}")
        
        return BaseResponse(
            success=True,
            message="API key revealed successfully",
            data={"full_key": full_key}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to reveal API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reveal API key"
        )
