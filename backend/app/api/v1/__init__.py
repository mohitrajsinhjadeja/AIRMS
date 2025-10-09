"""AIRMS+ API v1 Routes
"""
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Create main v1 router
router = APIRouter()

# Import and include all module routers
try:
    from .auth import router as auth_router
    router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    logger.info("✅ Auth router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load auth router: {e}")

try:
    from .risk import router as risk_router
    router.include_router(risk_router, prefix="/risk", tags=["Risk Analysis"])
    logger.info("✅ Risk router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load risk router: {e}")

try:
    from .chat import router as chat_router
    router.include_router(chat_router, prefix="/chat", tags=["Chat"])
    logger.info("✅ Chat router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load chat router: {e}")

try:
    from .pii import router as pii_router
    router.include_router(pii_router, prefix="/pii", tags=["PII Detection"])
    logger.info("✅ PII router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load pii router: {e}")

try:
    from .education import router as education_router
    router.include_router(education_router, prefix="/education", tags=["Education"])
    logger.info("✅ Education router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load education router: {e}")

try:
    from .analytics import router as analytics_router
    router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
    logger.info("✅ Analytics router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load analytics router: {e}")

try:
    from .fact_check import router as fact_check_router
    router.include_router(fact_check_router, prefix="/fact-check", tags=["Fact Checking"])
    logger.info("✅ Fact check router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load fact_check router: {e}")

try:
    from .api_keys import router as api_keys_router
    router.include_router(api_keys_router, prefix="/api-keys", tags=["API Keys"])
    logger.info("✅ API Keys router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load api_keys router: {e}")

try:
    from .notifications import router as notifications_router
    router.include_router(notifications_router, tags=["Notifications"])
    logger.info("✅ Notifications router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load notifications router: {e}")

# Add a simple test endpoint to v1 router
@router.get("/")
async def v1_root():
    return {
        "message": "AIRMS+ API v1",
        "available_endpoints": [
            "/auth", "/risk", "/chat", "/pii", 
            "/education", "/analytics", "/fact-check", "/api-keys"
        ]
    }

# Add test endpoint for chat specifically
@router.get("/test/chat")
async def test_chat_endpoint():
    return {
        "message": "Chat endpoint is accessible",
        "chat_endpoints": [
            "POST /v1/chat/completion",
            "GET /v1/chat/risk-stats",
            "POST /v1/chat/test-risk"
        ]
    }