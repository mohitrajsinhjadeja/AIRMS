"""
🔒 PII Safety API Endpoints
Manage PII tokenization and user permissions
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.services.pii_tokenization import pii_tokenizer, tokenize_content, detokenize_content
from app.middleware.pii_safety import pii_permission_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pii-safety", tags=["PII Safety"])

# Pydantic models
class TokenizeRequest(BaseModel):
    text: str = Field(..., description="Text content to tokenize")
    request_permission: bool = Field(True, description="Whether to request user permission")

class TokenizeResponse(BaseModel):
    original_text: str
    tokenized_text: str
    detected_pii: List[Dict[str, Any]]
    pii_count: int
    permission_required: List[Dict[str, Any]]
    requires_user_consent: bool
    processing_safe: bool
    tokenization_timestamp: str

class DetokenizeRequest(BaseModel):
    tokenized_text: str = Field(..., description="Text with tokens to replace")
    permission_granted: bool = Field(False, description="Whether user granted permission")

class DetokenizeResponse(BaseModel):
    detokenized_text: str
    tokens_replaced: int
    permission_granted: bool
    message: str

class PermissionGrantRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for permission tracking")
    pii_types: List[str] = Field(..., description="PII types to grant permission for")

class PermissionResponse(BaseModel):
    permission_granted: bool
    session_id: str
    expires_in: int
    pii_types_allowed: List[str]

@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text_endpoint(
    request: TokenizeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🔒 Tokenize PII in Text
    
    Automatically detects and tokenizes personally identifiable information
    in the provided text content.
    """
    try:
        user_id = str(current_user.get("id", ""))
        
        result = await pii_tokenizer.tokenize_text(
            text=request.text,
            user_id=user_id,
            request_permission=request.request_permission
        )
        
        return TokenizeResponse(**result)
        
    except Exception as e:
        logger.error(f"Text tokenization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tokenization failed: {str(e)}")

@router.post("/detokenize", response_model=DetokenizeResponse)
async def detokenize_text_endpoint(
    request: DetokenizeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🔓 Detokenize Text (Requires Permission)
    
    Replaces tokens with original PII values. Requires explicit user permission.
    """
    try:
        user_id = str(current_user.get("id", ""))
        
        result = await pii_tokenizer.detokenize_text(
            tokenized_text=request.tokenized_text,
            user_id=user_id,
            permission_granted=request.permission_granted
        )
        
        return DetokenizeResponse(**result)
        
    except Exception as e:
        logger.error(f"Text detokenization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detokenization failed: {str(e)}")

@router.post("/grant-permission", response_model=PermissionResponse)
async def grant_pii_permission(
    request: PermissionGrantRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    ✅ Grant PII Processing Permission
    
    Grant permission to process specific types of PII for a session.
    """
    try:
        user_id = str(current_user.get("id", ""))
        
        result = await pii_permission_manager.grant_permission(
            user_id=user_id,
            session_id=request.session_id,
            pii_types=request.pii_types
        )
        
        if not result.get("permission_granted"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to grant permission"))
        
        return PermissionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Permission grant failed: {e}")
        raise HTTPException(status_code=500, detail=f"Permission grant failed: {str(e)}")

@router.post("/revoke-permission")
async def revoke_pii_permission(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    ❌ Revoke PII Processing Permission
    
    Revoke permission to process PII for a specific session.
    """
    try:
        user_id = str(current_user.get("id", ""))
        
        result = await pii_permission_manager.revoke_permission(
            user_id=user_id,
            session_id=session_id
        )
        
        return {
            "message": "Permission revoked successfully",
            "session_id": session_id,
            **result
        }
        
    except Exception as e:
        logger.error(f"Permission revocation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Permission revocation failed: {str(e)}")

@router.get("/permissions")
async def get_user_permissions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📋 Get User PII Permissions
    
    Retrieve all active PII processing permissions for the current user.
    """
    try:
        from app.core.database import get_database_operations
        
        user_id = str(current_user.get("id", ""))
        db_ops = await get_database_operations()
        
        # Get active permissions from database
        permissions = await db_ops.db.pii_permissions.find({
            "user_id": user_id,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow().isoformat()}
        }).to_list(length=100)
        
        return {
            "user_id": user_id,
            "active_permissions": len(permissions),
            "permissions": [
                {
                    "session_id": p["session_id"],
                    "pii_types": p["pii_types"],
                    "granted_at": p["granted_at"],
                    "expires_at": p["expires_at"]
                }
                for p in permissions
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve permissions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve permissions: {str(e)}")

@router.get("/status")
async def get_pii_safety_status():
    """
    📊 PII Safety System Status
    
    Get current status and statistics of the PII safety system.
    """
    try:
        from app.core.database import get_database_operations
        
        db_ops = await get_database_operations()
        
        # Get statistics
        total_tokens = await db_ops.db.pii_tokens.count_documents({"is_active": True})
        active_permissions = await db_ops.db.pii_permissions.count_documents({
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow().isoformat()}
        })
        
        # Get token distribution by type
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$token_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        token_distribution = await db_ops.db.pii_tokens.aggregate(pipeline).to_list(length=20)
        
        return {
            "system_status": "operational",
            "pii_safety_enabled": True,
            "statistics": {
                "total_active_tokens": total_tokens,
                "active_permissions": active_permissions,
                "token_distribution": {
                    item["_id"]: item["count"] for item in token_distribution
                }
            },
            "supported_pii_types": [
                "aadhaar", "pan", "phone", "email", "credit_card", 
                "bank_account", "ifsc", "name", "address"
            ],
            "security_features": {
                "automatic_tokenization": True,
                "permission_based_access": True,
                "90_day_retention": True,
                "encrypted_storage": True,
                "audit_logging": True
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get PII safety status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/cleanup-expired")
async def cleanup_expired_tokens(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🧹 Cleanup Expired Tokens
    
    Remove expired PII tokens (90-day retention policy).
    Requires admin role.
    """
    try:
        # Check if user is admin
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await pii_tokenizer.cleanup_expired_tokens()
        
        return {
            "message": "Token cleanup completed",
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.get("/test-tokenization")
async def test_pii_tokenization():
    """
    🧪 Test PII Tokenization
    
    Test endpoint to demonstrate PII tokenization with sample data.
    """
    try:
        # Sample text with various PII types
        sample_text = """
        Hello, my name is John Doe and my Aadhaar number is 1234 5678 9012.
        You can reach me at john.doe@email.com or call 9876543210.
        My PAN is ABCDE1234F and my credit card is 4532 1234 5678 9012.
        """
        
        result = await tokenize_content(sample_text, user_id="test_user")
        
        return {
            "test_description": "Sample PII tokenization demonstration",
            "sample_input": sample_text.strip(),
            "tokenization_result": result,
            "explanation": {
                "original_text": "Contains multiple PII types",
                "tokenized_text": "PII replaced with secure tokens",
                "detected_pii": "Shows what PII was found",
                "processing_safe": "Indicates if safe for external APIs"
            }
        }
        
    except Exception as e:
        logger.error(f"Test tokenization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def pii_safety_health():
    """PII Safety system health check"""
    try:
        # Test tokenization functionality
        test_result = await tokenize_content("test@email.com", user_id="health_check")
        
        return {
            "status": "healthy",
            "tokenization_working": test_result["pii_count"] > 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
