"""
🔑 API Keys Management Router - MongoDB Integration
Comprehensive API key management with MongoDB persistence and analytics
"""

import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, ValidationError
from bson import ObjectId

from app.core.database import get_database_operations
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-keys", tags=["API Keys Management"])

# Pydantic Models
class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="API key name", alias="key_name")
    description: Optional[str] = Field(None, max_length=500, description="API key description")
    expires_in_days: Optional[int] = Field(365, ge=1, le=3650, description="Expiration in days (1-3650)")
    permissions: List[str] = Field(default_factory=lambda: ["read", "write"], description="API key permissions")
    usage_limit: Optional[int] = Field(None, ge=1, description="Maximum number of API calls allowed")
    
    class Config:
        populate_by_name = True  # Allow both 'key_name' and 'name'

class APIKeyResponse(BaseModel):
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    key_preview: str = Field(..., description="First 8 characters of API key")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    is_active: bool = Field(..., description="Whether key is active")
    usage_count: int = Field(0, description="Number of times key was used")
    last_used: Optional[str] = Field(None, description="Last usage timestamp")
    permissions: List[str] = Field(..., description="API key permissions")
    created_by: str = Field(..., description="User who created the key")

class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None

class APIKeyUsageLog(BaseModel):
    api_key_id: str
    endpoint: str
    method: str
    timestamp: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    response_status: int
    execution_time_ms: Optional[int] = None

# Database Operations
async def get_db_ops():
    """Get database operations instance"""
    return await get_database_operations()

def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"airms_{secrets.token_urlsafe(32)}"

def is_valid_api_key(api_key: str) -> bool:
    """Validate API key format"""
    return api_key.startswith("airms_") and len(api_key) > 10

async def log_api_key_usage(
    db_ops,
    api_key_id: str,
    endpoint: str,
    method: str,
    status_code: int,
    execution_time_ms: int = None
):
    """Log API key usage for analytics"""
    try:
        usage_log = {
            "api_key_id": api_key_id,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": None,
            "user_agent": None,
            "response_status": status_code,
            "execution_time_ms": execution_time_ms
        }
        
        # Store in api_key_usage collection
        await db_ops.create_document("api_key_usage", usage_log)
        
        # Update usage count in api_keys collection
        await db_ops.update_document(
            "api_keys",
            {"_id": ObjectId(api_key_id)},
            {
                "$inc": {"usage_count": 1},
                "$set": {"last_used": datetime.utcnow().isoformat()}
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log API key usage: {e}")

# API Endpoints
@router.get("/", response_model=List[APIKeyResponse])
@router.get("", response_model=List[APIKeyResponse])  # Without trailing slash
async def get_api_keys(
    db_ops = Depends(get_db_ops),
    limit: int = 50,
    skip: int = 0
) -> List[APIKeyResponse]:
    """
    🔑 **Get All API Keys**
    
    Retrieve all API keys with pagination and usage statistics.
    
    **Features:**
    - MongoDB persistence
    - Usage analytics
    - Secure key preview (only first 8 chars)
    - Pagination support
    """
    try:
        logger.info(f"📋 Retrieving API keys (limit: {limit}, skip: {skip})")
        
        # Query MongoDB for API keys
        query = {}
        sort = [("created_at", -1)]  # Most recent first
        
        api_keys_data = await db_ops.find_documents(
            "api_keys", 
            query, 
            limit=limit, 
            skip=skip, 
            sort=sort
        )
        
        # Convert to response format
        api_keys = []
        for key_data in api_keys_data:
            # Handle datetime conversion
            created_at = key_data["created_at"]
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            
            expires_at = key_data.get("expires_at")
            if expires_at and isinstance(expires_at, datetime):
                expires_at = expires_at.isoformat()
            
            last_used = key_data.get("last_used")
            if last_used and isinstance(last_used, datetime):
                last_used = last_used.isoformat()
            
            api_keys.append(APIKeyResponse(
                id=str(key_data["_id"]),
                name=key_data["name"],
                description=key_data.get("description"),
                key_preview=key_data["key"][:8] + "..." if len(key_data["key"]) > 8 else key_data["key"],
                created_at=created_at,
                expires_at=expires_at,
                is_active=key_data["is_active"],
                usage_count=key_data.get("usage_count", 0),
                last_used=last_used,
                permissions=key_data.get("permissions", ["read", "write"]),
                created_by=key_data.get("created_by", "system")
            ))
        
        logger.info(f"✅ Retrieved {len(api_keys)} API keys")
        return api_keys
        
    except Exception as e:
        logger.error(f"❌ Error retrieving API keys: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve API keys: {str(e)}")

@router.post("/", response_model=APIKeyResponse)
@router.post("", response_model=APIKeyResponse)  # Without trailing slash
async def create_api_key(
    key_data: APIKeyCreate,
    background_tasks: BackgroundTasks,
    db_ops = Depends(get_db_ops),
    current_user: UserInDB = Depends(get_current_user)
) -> APIKeyResponse:
    """
    🔑 **Create New API Key**
    
    Create a new API key with MongoDB persistence and audit logging.
    
    **Features:**
    - Secure key generation
    - MongoDB storage
    - Expiration management
    - Permission-based access
    - Audit logging
    """
    try:
        logger.info(f"🔑 Creating new API key: {key_data.name}")
        logger.info(f"🔍 Raw request data: {key_data.dict()}")
        logger.info(f"🔍 Request data: name={key_data.name}, permissions={key_data.permissions}, usage_limit={key_data.usage_limit}")
        logger.info(f"🔍 User: {current_user.email if current_user else 'None'}")
        logger.info(f"🔍 User ID: {current_user.id if current_user else 'None'}")
        
        # Generate secure API key
        api_key = generate_api_key()
        key_id = str(ObjectId())
        
        # Calculate expiration
        created_at = datetime.utcnow()
        expires_at = None
        if key_data.expires_in_days:
            expires_at = created_at + timedelta(days=key_data.expires_in_days)
        
        # Prepare key document for MongoDB
        key_document = {
            "_id": ObjectId(key_id),
            "key": api_key,
            "name": key_data.name,
            "description": key_data.description,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_active": True,
            "usage_count": 0,
            "last_used": None,
            "permissions": key_data.permissions,
            "created_by": current_user.email,
            "metadata": {
                "created_ip": None,  # TODO: Get from request
                "created_user_agent": None  # TODO: Get from request
            }
        }
        
        logger.info(f"🔍 Key document to store: {key_document}")
        
        # Store in MongoDB
        await db_ops.create_document("api_keys", key_document)
        
        # Log creation event
        background_tasks.add_task(
            log_api_key_usage,
            db_ops,
            key_id,
            "/api/v1/api-keys",
            "POST",
            201
        )
        
        # Return response (include full key only on creation)
        response = APIKeyResponse(
            id=key_id,
            name=key_document["name"],
            description=key_document.get("description"),
            key_preview=api_key,  # Show full key on creation
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat() if expires_at else None,
            is_active=key_document["is_active"],
            usage_count=0,
            permissions=key_document["permissions"],
            created_by=key_document["created_by"]
        )
        
        logger.info(f"✅ Created API key: {key_data.name} (ID: {key_id})")
        return response
        
    except ValidationError as e:
        logger.error(f"❌ Validation error creating API key: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error creating API key: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")

@router.put("/{key_id}", response_model=APIKeyResponse)
@router.put("/{key_id}/", response_model=APIKeyResponse)  # Without trailing slash
async def update_api_key(
    key_id: str,
    update_data: APIKeyUpdate,
    background_tasks: BackgroundTasks,
    db_ops = Depends(get_db_ops)
) -> APIKeyResponse:
    """
    🔑 **Update API Key**
    
    Update an existing API key's metadata and permissions.
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(key_id):
            raise HTTPException(status_code=400, detail="Invalid API key ID format")
        
        logger.info(f"📝 Updating API key: {key_id}")
        
        # Check if key exists
        existing_key = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        if not existing_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Prepare update data
        update_fields = {}
        if update_data.name is not None:
            update_fields["name"] = update_data.name
        if update_data.description is not None:
            update_fields["description"] = update_data.description
        if update_data.is_active is not None:
            update_fields["is_active"] = update_data.is_active
        if update_data.permissions is not None:
            update_fields["permissions"] = update_data.permissions
        
        update_fields["updated_at"] = datetime.utcnow().isoformat()
        
        # Update in MongoDB
        await db_ops.update_document(
            "api_keys",
            {"_id": ObjectId(key_id)},
            {"$set": update_fields}
        )
        
        # Get updated document
        updated_key = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        
        # Log update event
        background_tasks.add_task(
            log_api_key_usage,
            db_ops,
            key_id,
            f"/api/v1/api-keys/{key_id}",
            "PUT",
            200
        )
        
        # Return updated response
        response = APIKeyResponse(
            id=key_id,
            name=updated_key["name"],
            description=updated_key.get("description"),
            key_preview=updated_key["key"][:8] + "...",
            created_at=updated_key["created_at"],
            expires_at=updated_key.get("expires_at"),
            is_active=updated_key["is_active"],
            usage_count=updated_key.get("usage_count", 0),
            last_used=updated_key.get("last_used"),
            permissions=updated_key.get("permissions", ["read", "write"]),
            created_by=updated_key.get("created_by", "system")
        )
        
        logger.info(f"✅ Updated API key: {key_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update API key: {str(e)}")

@router.delete("/{key_id}", response_model=Dict[str, str])
@router.delete("/{key_id}/", response_model=Dict[str, str])  # Without trailing slash
async def delete_api_key(
    key_id: str,
    background_tasks: BackgroundTasks,
    db_ops = Depends(get_db_ops)
) -> Dict[str, str]:
    """
    🔑 **Delete API Key**
    
    Permanently delete an API key from MongoDB.
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(key_id):
            raise HTTPException(status_code=400, detail="Invalid API key ID format")
        
        logger.info(f"🗑️ Deleting API key: {key_id}")
        
        # Check if key exists
        existing_key = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        if not existing_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        key_name = existing_key["name"]
        
        # Delete from MongoDB
        await db_ops.delete_document("api_keys", {"_id": ObjectId(key_id)})
        
        # Log deletion event
        background_tasks.add_task(
            log_api_key_usage,
            db_ops,
            key_id,
            f"/api/v1/api-keys/{key_id}",
            "DELETE",
            200
        )
        
        logger.info(f"✅ Deleted API key: {key_name} (ID: {key_id})")
        return {"message": f"API key '{key_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete API key: {str(e)}")

@router.get("/{key_id}", response_model=APIKeyResponse)
@router.get("/{key_id}/", response_model=APIKeyResponse)  # Without trailing slash
async def get_api_key(
    key_id: str,
    db_ops = Depends(get_db_ops)
) -> APIKeyResponse:
    """
    🔑 **Get Specific API Key**
    
    Retrieve a specific API key by ID with usage statistics.
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(key_id):
            raise HTTPException(status_code=400, detail="Invalid API key ID format")
        
        # Find key in MongoDB
        key_data = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        if not key_data:
            raise HTTPException(status_code=404, detail="API key not found")
        
        response = APIKeyResponse(
            id=key_id,
            name=key_data["name"],
            description=key_data.get("description"),
            key_preview=key_data["key"][:8] + "...",
            created_at=key_data["created_at"],
            expires_at=key_data.get("expires_at"),
            is_active=key_data["is_active"],
            usage_count=key_data.get("usage_count", 0),
            last_used=key_data.get("last_used"),
            permissions=key_data.get("permissions", ["read", "write"]),
            created_by=key_data.get("created_by", "system")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve API key: {str(e)}")

@router.post("/{key_id}/regenerate", response_model=APIKeyResponse)
@router.post("/{key_id}/regenerate/", response_model=APIKeyResponse)  # Without trailing slash
async def regenerate_api_key(
    key_id: str,
    background_tasks: BackgroundTasks,
    db_ops = Depends(get_db_ops)
) -> APIKeyResponse:
    """
    🔑 **Regenerate API Key**
    
    Generate a new key value while keeping metadata intact.
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(key_id):
            raise HTTPException(status_code=400, detail="Invalid API key ID format")
        
        logger.info(f"🔄 Regenerating API key: {key_id}")
        
        # Check if key exists
        existing_key = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        if not existing_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Generate new key
        new_api_key = generate_api_key()
        
        # Update in MongoDB
        await db_ops.update_document(
            "api_keys",
            {"_id": ObjectId(key_id)},
            {
                "$set": {
                    "key": new_api_key,
                    "usage_count": 0,  # Reset usage count
                    "last_used": None,
                    "regenerated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Get updated document
        updated_key = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        
        # Log regeneration event
        background_tasks.add_task(
            log_api_key_usage,
            db_ops,
            key_id,
            f"/api/v1/api-keys/{key_id}/regenerate",
            "POST",
            200
        )
        
        response = APIKeyResponse(
            id=key_id,
            name=updated_key["name"],
            description=updated_key.get("description"),
            key_preview=new_api_key,  # Show full key on regeneration
            created_at=updated_key["created_at"],
            expires_at=updated_key.get("expires_at"),
            is_active=updated_key["is_active"],
            usage_count=0,
            permissions=updated_key.get("permissions", ["read", "write"]),
            created_by=updated_key.get("created_by", "system")
        )
        
        logger.info(f"✅ Regenerated API key: {key_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error regenerating API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate API key: {str(e)}")

@router.get("/{key_id}/usage", response_model=Dict[str, Any])
@router.get("/{key_id}/usage/", response_model=Dict[str, Any])  # Without trailing slash
async def get_api_key_usage(
    key_id: str,
    days: int = 30,
    db_ops = Depends(get_db_ops)
) -> Dict[str, Any]:
    """
    📊 **Get API Key Usage Analytics**
    
    Retrieve detailed usage statistics for an API key.
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(key_id):
            raise HTTPException(status_code=400, detail="Invalid API key ID format")
        
        # Check if key exists
        existing_key = await db_ops.find_document("api_keys", {"_id": ObjectId(key_id)})
        if not existing_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query usage logs
        usage_query = {
            "api_key_id": key_id,
            "timestamp": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }
        
        usage_logs = await db_ops.find_documents("api_key_usage", usage_query, limit=1000)
        
        # Calculate analytics
        total_requests = len(usage_logs)
        successful_requests = len([log for log in usage_logs if log["response_status"] < 400])
        failed_requests = total_requests - successful_requests
        
        # Group by endpoint
        endpoint_stats = {}
        for log in usage_logs:
            endpoint = log["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"count": 0, "success": 0, "failed": 0}
            endpoint_stats[endpoint]["count"] += 1
            if log["response_status"] < 400:
                endpoint_stats[endpoint]["success"] += 1
            else:
                endpoint_stats[endpoint]["failed"] += 1
        
        # Calculate average response time
        response_times = [log.get("execution_time_ms", 0) for log in usage_logs if log.get("execution_time_ms")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        analytics = {
            "key_id": key_id,
            "key_name": existing_key["name"],
            "period_days": days,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "endpoint_statistics": endpoint_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving API key usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve usage analytics: {str(e)}")

@router.post("/test", response_model=Dict[str, Any])
async def test_create_api_key(
    key_data: APIKeyCreate,
    db_ops = Depends(get_db_ops)
) -> Dict[str, Any]:
    """
    🔑 **Test API Key Creation (No Auth)**
    
    Test endpoint to debug API key creation without authentication.
    """
    try:
        logger.info(f"🧪 Testing API key creation: {key_data.name}")
        logger.info(f"🔍 Raw request data: {key_data.dict()}")
        logger.info(f"🔍 Request data: name={key_data.name}, permissions={key_data.permissions}, usage_limit={key_data.usage_limit}")
        
        return {
            "status": "success",
            "message": "Validation passed",
            "data": key_data.dict(),
            "name": key_data.name,
            "permissions": key_data.permissions,
            "usage_limit": key_data.usage_limit,
            "expires_in_days": key_data.expires_in_days,
            "description": key_data.description
        }
        
    except ValidationError as e:
        logger.error(f"❌ Validation error in test: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Initialize default API keys
async def initialize_default_keys():
    """Initialize with default API keys for testing"""
    try:
        db_ops = await get_database_operations()
        
        # Check if any keys exist
        existing_keys = await db_ops.find_documents("api_keys", {}, limit=1)
        
        if not existing_keys:
            # Create default API key
            default_key_doc = {
                "_id": ObjectId(),
                "key": "airms_default_test_key_12345678901234567890",
                "name": "Default Test Key",
                "description": "Default API key for testing AIRMS+ dashboard",
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": None,
                "is_active": True,
                "usage_count": 0,
                "last_used": None,
                "permissions": ["read", "write", "admin"],
                "created_by": "system",
                "metadata": {
                    "is_default": True
                }
            }
            
            await db_ops.create_document("api_keys", default_key_doc)
            logger.info("✅ Initialized default API key for testing")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize default keys: {e}")

# Auto-initialize on import (will be called when server starts)
# Note: This will be called by the main application startup
