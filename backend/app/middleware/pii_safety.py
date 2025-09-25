"""
🛡️ PII Safety Middleware
Automatically tokenizes PII before external API calls and handles user permissions
"""

import logging
from typing import Dict, Any, Optional, Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.pii_tokenization import pii_tokenizer
from app.core.auth import get_current_user_from_token

logger = logging.getLogger(__name__)

class PIISafetyMiddleware(BaseHTTPMiddleware):
    """
    🔒 PII Safety Middleware
    
    Intercepts requests containing text content, tokenizes PII automatically,
    and requires user permission for processing sensitive data.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.protected_endpoints = {
            "/api/v1/airms-plus/detect",
            "/api/v1/airms-plus/score", 
            "/api/v1/airms-plus/misinformation",
            "/api/v1/airms-plus/educate",
            "/api/v1/enhanced-risk/assess"
        }
        self.bypass_tokenization = {
            "/api/v1/auth/",
            "/api/v1/notifications/",
            "/api/v1/analytics/",
            "/health",
            "/docs"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch logic"""
        
        # Skip middleware for non-protected endpoints
        if not self._should_process_request(request):
            return await call_next(request)
        
        try:
            # Extract user information
            user_id = await self._get_user_id_from_request(request)
            
            # Get request body
            body = await request.body()
            if not body:
                return await call_next(request)
            
            # Parse JSON body
            import json
            try:
                request_data = json.loads(body.decode())
            except json.JSONDecodeError:
                return await call_next(request)
            
            # Extract text content for tokenization
            text_content = self._extract_text_content(request_data)
            if not text_content:
                return await call_next(request)
            
            # Tokenize PII in the content
            tokenization_result = await pii_tokenizer.tokenize_text(
                text_content, 
                user_id=user_id,
                request_permission=True
            )
            
            # Check if user permission is required
            if tokenization_result["requires_user_consent"]:
                # Check if user has granted permission
                permission_granted = self._check_user_permission(request, tokenization_result)
                
                if not permission_granted:
                    return await self._request_user_permission(tokenization_result)
            
            # Replace original text with tokenized version
            modified_data = self._replace_text_content(request_data, tokenization_result["tokenized_text"])
            
            # Create new request with tokenized content
            modified_request = await self._create_modified_request(request, modified_data)
            
            # Add tokenization metadata to request state
            modified_request.state.pii_tokenization = {
                "pii_detected": tokenization_result["pii_count"] > 0,
                "pii_count": tokenization_result["pii_count"],
                "detected_types": [pii["type"] for pii in tokenization_result["detected_pii"]],
                "processing_safe": tokenization_result["processing_safe"],
                "tokenization_id": tokenization_result.get("tokenization_id")
            }
            
            # Process the request
            response = await call_next(modified_request)
            
            # Add PII safety headers to response
            response.headers["X-PII-Safety"] = "enabled"
            response.headers["X-PII-Detected"] = str(tokenization_result["pii_count"])
            response.headers["X-Processing-Safe"] = str(tokenization_result["processing_safe"])
            
            return response
            
        except Exception as e:
            logger.error(f"PII Safety Middleware error: {e}")
            # Continue without tokenization on error
            return await call_next(request)
    
    def _should_process_request(self, request: Request) -> bool:
        """Check if request should be processed by PII middleware"""
        path = request.url.path
        
        # Skip bypass endpoints
        for bypass_path in self.bypass_tokenization:
            if path.startswith(bypass_path):
                return False
        
        # Only process POST requests with content
        if request.method != "POST":
            return False
        
        # Check if endpoint is protected
        return any(path.startswith(endpoint) for endpoint in self.protected_endpoints)
    
    async def _get_user_id_from_request(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        try:
            # Try to get from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                user = await get_current_user_from_token(token)
                return str(user.get("id")) if user else None
        except Exception:
            pass
        
        return None
    
    def _extract_text_content(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract text content from request data"""
        # Common text fields to check
        text_fields = ["text", "content", "message", "input", "query", "prompt"]
        
        for field in text_fields:
            if field in request_data and isinstance(request_data[field], str):
                return request_data[field]
        
        # Check for nested content
        if "data" in request_data:
            return self._extract_text_content(request_data["data"])
        
        return None
    
    def _replace_text_content(self, request_data: Dict[str, Any], tokenized_text: str) -> Dict[str, Any]:
        """Replace text content with tokenized version"""
        modified_data = request_data.copy()
        
        text_fields = ["text", "content", "message", "input", "query", "prompt"]
        
        for field in text_fields:
            if field in modified_data and isinstance(modified_data[field], str):
                modified_data[field] = tokenized_text
                break
        
        # Handle nested data
        if "data" in modified_data and isinstance(modified_data["data"], dict):
            modified_data["data"] = self._replace_text_content(modified_data["data"], tokenized_text)
        
        return modified_data
    
    async def _create_modified_request(self, original_request: Request, modified_data: Dict[str, Any]) -> Request:
        """Create new request with modified data"""
        import json
        from starlette.requests import Request as StarletteRequest
        
        # Convert modified data back to JSON
        modified_body = json.dumps(modified_data).encode()
        
        # Create new request with modified body
        scope = original_request.scope.copy()
        scope["body"] = modified_body
        
        # Create new request object
        modified_request = Request(scope)
        modified_request._body = modified_body
        
        return modified_request
    
    def _check_user_permission(self, request: Request, tokenization_result: Dict[str, Any]) -> bool:
        """Check if user has granted permission for PII processing"""
        # Check for permission header
        permission_header = request.headers.get("X-PII-Permission-Granted")
        if permission_header and permission_header.lower() == "true":
            return True
        
        # Check for permission in request body
        try:
            import json
            body = request._body if hasattr(request, '_body') else None
            if body:
                data = json.loads(body.decode())
                return data.get("pii_permission_granted", False)
        except:
            pass
        
        return False
    
    async def _request_user_permission(self, tokenization_result: Dict[str, Any]) -> JSONResponse:
        """Return permission request response"""
        return JSONResponse(
            status_code=403,
            content={
                "error": "PII_PERMISSION_REQUIRED",
                "message": "Personal information detected. User permission required to proceed.",
                "pii_detected": {
                    "count": tokenization_result["pii_count"],
                    "types": [pii["type"] for pii in tokenization_result["detected_pii"]],
                    "permission_required": tokenization_result["permission_required"]
                },
                "instructions": {
                    "method_1": "Add header: X-PII-Permission-Granted: true",
                    "method_2": "Add to request body: pii_permission_granted: true",
                    "note": "Only grant permission if you consent to processing your personal information"
                },
                "detected_pii_preview": [
                    {
                        "type": pii["type"],
                        "risk_level": next(
                            (p["risk_level"] for p in tokenization_result["permission_required"] 
                             if p["pii_type"] == pii["type"]), "unknown"
                        ),
                        "description": next(
                            (p["description"] for p in tokenization_result["permission_required"] 
                             if p["pii_type"] == pii["type"]), "Personal information"
                        )
                    }
                    for pii in tokenization_result["detected_pii"]
                ]
            }
        )

class PIIPermissionManager:
    """
    🔐 PII Permission Manager
    
    Handles user permissions for PII processing
    """
    
    def __init__(self):
        self.permission_cache = {}  # In production, use Redis
    
    async def grant_permission(self, user_id: str, session_id: str, pii_types: list) -> Dict[str, Any]:
        """Grant permission for specific PII types"""
        try:
            permission_key = f"{user_id}:{session_id}"
            
            permission_data = {
                "user_id": user_id,
                "session_id": session_id,
                "pii_types": pii_types,
                "granted_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),  # 1 hour expiry
                "is_active": True
            }
            
            # Store in cache (use Redis in production)
            self.permission_cache[permission_key] = permission_data
            
            # Also store in database for audit
            from app.core.database import get_database_operations
            db_ops = await get_database_operations()
            
            await db_ops.db.pii_permissions.insert_one(permission_data)
            
            return {
                "permission_granted": True,
                "session_id": session_id,
                "expires_in": 3600,  # 1 hour
                "pii_types_allowed": pii_types
            }
            
        except Exception as e:
            logger.error(f"Failed to grant PII permission: {e}")
            return {"permission_granted": False, "error": str(e)}
    
    async def check_permission(self, user_id: str, session_id: str, pii_types: list) -> bool:
        """Check if user has permission for specific PII types"""
        try:
            permission_key = f"{user_id}:{session_id}"
            
            # Check cache first
            if permission_key in self.permission_cache:
                permission_data = self.permission_cache[permission_key]
                
                # Check if permission is still valid
                from datetime import datetime
                expires_at = datetime.fromisoformat(permission_data["expires_at"])
                if datetime.utcnow() < expires_at:
                    # Check if all required PII types are allowed
                    allowed_types = set(permission_data["pii_types"])
                    required_types = set(pii_types)
                    return required_types.issubset(allowed_types)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check PII permission: {e}")
            return False
    
    async def revoke_permission(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Revoke PII processing permission"""
        try:
            permission_key = f"{user_id}:{session_id}"
            
            # Remove from cache
            if permission_key in self.permission_cache:
                del self.permission_cache[permission_key]
            
            # Mark as revoked in database
            from app.core.database import get_database_operations
            db_ops = await get_database_operations()
            
            await db_ops.db.pii_permissions.update_one(
                {"user_id": user_id, "session_id": session_id},
                {"$set": {"is_active": False, "revoked_at": datetime.utcnow().isoformat()}}
            )
            
            return {"permission_revoked": True}
            
        except Exception as e:
            logger.error(f"Failed to revoke PII permission: {e}")
            return {"permission_revoked": False, "error": str(e)}

# Global permission manager
pii_permission_manager = PIIPermissionManager()
