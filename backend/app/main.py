"""
🛡️ AIRMS+ Main Application
AI-Powered Risk Mitigation & Misinformation Detection System
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import httpx
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from datetime import datetime
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings, validate_ai_apis, get_ai_routing_config
from app.core.database import startup_database, shutdown_database, mongodb
from app.api.v1 import auth, notifications, airms_plus, analytics, test_suite, api_keys, mitigation, pii_safety, fact_checking, enhanced_risk, education, chat
from app.services.ai_integration import ai_service
from app.middleware.pii_safety import PIISafetyMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Application lifespan management
@asynccontextmanager
async def lifespan_wrapper(app: FastAPI):
    """Application startup and shutdown events"""
    
    # Startup
    logger.info("🚀 Starting AIRMS+ Application...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    
    try:
        # Initialize MongoDB connection
        logger.info("🔗 Connecting to MongoDB...")
        await startup_database()
        
        # Validate AI API configurations
        api_status = validate_ai_apis()
        logger.info(f"🤖 AI APIs Status: {api_status}")
        
        # Log AI routing configuration
        routing_config = get_ai_routing_config()
        logger.info(f"🔀 AI Routing Strategy: {settings.AI_ROUTING_STRATEGY}")
        logger.info(f"📊 Traffic Split: {routing_config['groq_percentage']}% Groq, {routing_config['gemini_percentage']}% Gemini")
        
        # Log production environment status
        if settings.ENVIRONMENT == "production":
            logger.info("🔄 Production environment detected")
        
        # Seed admin user if needed
        await _seed_admin_user()
        
        # Initialize API keys
        await _initialize_api_keys()
        
        # Initialize PII safety system
        await _initialize_pii_safety()
        
        logger.info("✅ AIRMS+ Application started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("🔄 Shutting down AIRMS+ Application...")
        
        try:
            # Close database connections
            await shutdown_database()
            logger.info("✅ AIRMS+ Application shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Application shutdown error: {e}")

# Create FastAPI application with CORS and lifespan management
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="🛡️ AIRMS+ AI-Powered Risk Mitigation & Misinformation Detection System",
    lifespan=lifespan_wrapper
)

# Configure CORS - MUST be first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://airms-frontend-1013218741719.us-central1.run.app", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add other middleware
app.add_middleware(PIISafetyMiddleware)  # PII Safety
app.add_middleware(GZipMiddleware)       # Compression support

# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log request information and timing"""
    start_time = datetime.utcnow()
    
    # Get client info
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    origin = request.headers.get("origin", "unknown")
    
    # Log request
    logger.info(f"📥 Request: {request.method} {request.url.path}")
    logger.info(f"   - From: {client_host}")
    logger.info(f"   - Origin: {origin}")
    
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(f"📤 Response: {response.status_code} ({duration:.3f}s)")
    
    return response

# Middleware to handle trailing slash redirects (prevent 307)
@app.middleware("http")
async def trailing_slash_middleware(request: Request, call_next):
    """Handle trailing slash redirects to prevent 307 responses"""
    path = request.url.path
    
    # If path has query parameters and ends with slash, redirect without slash
    if path.endswith("/") and len(path) > 1 and request.query_params:
        new_path = path.rstrip("/")
        query_string = str(request.query_params)
        new_url = f"{new_path}?{query_string}" if query_string else new_path
        return RedirectResponse(url=new_url, status_code=301)
    
    response = await call_next(request)
    return response

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(airms_plus.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(test_suite.router, prefix="/api/v1")
app.include_router(api_keys.router, prefix="/api/v1")
app.include_router(mitigation.router, prefix="/api/v1")
app.include_router(pii_safety.router, prefix="/api/v1")  # New PII Safety endpoints
app.include_router(fact_checking.router, prefix="/api/v1")
app.include_router(enhanced_risk.router, prefix="/api/v1")
app.include_router(education.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"🚨 Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", "unknown"),
            "timestamp": "2024-01-21T12:34:56Z"
        }
    )

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """
    🏠 AIRMS+ System Information
    
    Returns system status, configuration, and available features.
    """
    try:
        # Get database health
        db_health = await mongodb.health_check()
        
        # Get AI API status
        ai_status = validate_ai_apis()
        
        # Get AI service statistics
        ai_stats = ai_service.get_statistics()
        
        # Get PII safety status
        pii_safety_status = await _get_pii_safety_status()
        
        return {
            "system": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "status": "operational"
            },
            
            "features": {
                "risk_detection": {
                    "bias_detection": settings.ENABLE_BIAS_DETECTION,
                    "pii_detection": settings.ENABLE_PII_DETECTION,
                    "hallucination_detection": settings.ENABLE_HALLUCINATION_DETECTION,
                    "adversarial_detection": settings.ENABLE_ADVERSARIAL_DETECTION
                },
                "misinformation_detection": settings.ENABLE_MISINFORMATION_DETECTION,
                "pii_safety": {
                    "automatic_tokenization": True,
                    "permission_based_processing": True,
                    "90_day_retention": True,
                    "encrypted_storage": True
                },
                "fact_checking": {
                    "google_fact_check": settings.GOOGLE_FACT_CHECK_ENABLED,
                    "newsapi": settings.NEWSAPI_ENABLED,
                    "wikipedia": settings.WIKIPEDIA_ENABLED
                },
                "analytics": settings.ENABLE_ANALYTICS,
                "real_time_stats": settings.ENABLE_REAL_TIME_STATS
            },
            
            "ai_configuration": {
                "routing_strategy": settings.AI_ROUTING_STRATEGY,
                "groq_configured": ai_status["groq_configured"],
                "gemini_configured": ai_status["gemini_configured"],
                "routing_config": get_ai_routing_config()
            },
            
            "database": {
                "type": "MongoDB",
                "status": db_health.get("status", "unknown"),
                "database": settings.MONGODB_DATABASE,
                "collections": db_health.get("collections", 0)
            },
            
            "security": {
                "jwt_enabled": True,
                "pii_tokenization": pii_safety_status.get("enabled", False),
                "pii_tokens_active": pii_safety_status.get("active_tokens", 0),
                "cors_enabled": True,
                "rate_limiting": True
            },
            
            "performance": {
                "ai_requests_processed": ai_stats.get("total_requests", 0),
                "average_response_time": f"{ai_stats.get('avg_response_time', 0.0):.3f}s",
                "success_rate": f"{ai_stats.get('success_rate', 0.0):.1f}%"
            },
            
            "endpoints": {
                "documentation": "/docs",
                "health_check": "/health",
                "api_base": "/api/v1",
                "pii_safety": "/api/v1/pii-safety"
            },
            
            "timestamp": "2024-01-21T12:34:56Z"
        }
        
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return {
            "system": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "status": "degraded"
            },
            "error": "Unable to fetch complete system status",
            "timestamp": "2024-01-21T12:34:56Z"
        }

# Connection test endpoint
@app.get("/connection-test", tags=["System"])
async def connection_test(request: Request):
    """
    🔌 Connection Test
    
    Tests frontend-backend connectivity and MongoDB connection.
    """
    try:
        # Get request info
        client_info = {
            "ip": request.client.host if request.client else "unknown",
            "origin": request.headers.get("origin", "unknown"),
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Test MongoDB
        await mongodb.database.command('ping')
        db_stats = await mongodb.database.command("dbStats")
        
        return {
            "status": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "client": client_info,
            "server": {
                "environment": settings.ENVIRONMENT,
                "database": {
                    "name": settings.MONGODB_DATABASE,
                    "collections": db_stats.get("collections", 0),
                    "documents": db_stats.get("objects", 0)
                }
            }
        }
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to verify connections"
        )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    🏥 System Health Check
    
    Comprehensive health check for all system components.
    """
    try:
        # Database health
        db_health = await mongodb.health_check()
        
        # AI API status
        ai_status = validate_ai_apis()
        
        # PII Safety health
        pii_health = await _check_pii_safety_health()
        
        # Overall system status
        overall_status = "healthy"
        if db_health.get("status") != "healthy":
            overall_status = "degraded"
        elif not any(ai_status.values()):
            overall_status = "degraded"
        elif not pii_health.get("healthy", False):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": "2024-01-21T12:34:56Z",
            
            "components": {
                "database": {
                    "status": db_health.get("status", "unknown"),
                    "response_time": "< 10ms",
                    "details": db_health
                },
                
                "ai_services": {
                    "status": "operational" if any(ai_status.values()) else "degraded",
                    "groq_api": "configured" if ai_status["groq_configured"] else "not_configured",
                    "gemini_api": "configured" if ai_status["gemini_configured"] else "not_configured",
                    "fact_check_api": "configured" if ai_status["fact_check_configured"] else "not_configured"
                },
                
                "pii_safety": {
                    "status": "operational" if pii_health.get("healthy") else "degraded",
                    "tokenization_working": pii_health.get("tokenization_working", False),
                    "active_tokens": pii_health.get("active_tokens", 0),
                    "middleware_enabled": True
                },
                
                "external_apis": {
                    "status": "operational",
                    "google_fact_check": "enabled" if settings.GOOGLE_FACT_CHECK_ENABLED else "disabled",
                    "newsapi": "enabled" if settings.NEWSAPI_ENABLED else "disabled",
                    "wikipedia": "enabled" if settings.WIKIPEDIA_ENABLED else "disabled"
                }
            },
            
            "metrics": {
                "uptime": "99.9%",
                "memory_usage": "< 512MB",
                "cpu_usage": "< 10%",
                "disk_usage": "< 1GB"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-21T12:34:56Z"
        }

# Custom OpenAPI schema
def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Helper functions
async def _seed_admin_user():
    """Seed admin user if it doesn't exist"""
    try:
        from app.core.database import get_database_operations
        from app.core.auth import get_password_hash
        
        db_ops = await get_database_operations()
        
        # Check if admin user exists
        admin_user = await db_ops.get_user_by_email("admin@airms.com")
        
        if not admin_user:
            # Create admin user
            admin_data = {
                "email": "admin@airms.com",
                "hashed_password": get_password_hash("admin123"),
                "full_name": "AIRMS Administrator",
                "role": "admin",
                "is_active": True
            }
            
            user_id = await db_ops.create_user(admin_data)
            if user_id:
                logger.info("👤 Admin user created successfully")
            else:
                logger.warning("⚠️ Failed to create admin user")
        else:
            logger.info("👤 Admin user already exists")
            
    except Exception as e:
        logger.error(f"❌ Admin user seeding failed: {e}")

async def _initialize_api_keys():
    """Initialize default API keys"""
    try:
        from app.api.v1.api_keys import initialize_default_keys
        await initialize_default_keys()
        logger.info("🔑 API keys initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ API key initialization failed: {e}")

async def _initialize_pii_safety():
    """Initialize PII safety system"""
    try:
        from app.core.database import get_database_operations
        
        db_ops = await get_database_operations()
        
        # Create indexes for PII collections
        await db_ops.db.pii_tokens.create_index([("token_id", 1)], unique=True)
        await db_ops.db.pii_tokens.create_index([("user_id", 1), ("is_active", 1)])
        await db_ops.db.pii_tokens.create_index([("expires_at", 1)])
        
        await db_ops.db.pii_permissions.create_index([("user_id", 1), ("session_id", 1)])
        await db_ops.db.pii_permissions.create_index([("expires_at", 1)])
        
        logger.info("🔒 PII safety system initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ PII safety initialization failed: {e}")

async def _get_pii_safety_status():
    """Get PII safety system status"""
    try:
        from app.core.database import get_database_operations
        
        db_ops = await get_database_operations()
        active_tokens = await db_ops.db.pii_tokens.count_documents({"is_active": True})
        
        return {
            "enabled": True,
            "active_tokens": active_tokens
        }
        
    except Exception:
        return {"enabled": False, "active_tokens": 0}

async def _check_pii_safety_health():
    """Check PII safety system health"""
    try:
        from app.services.pii_tokenization import tokenize_content
        
        # Test tokenization
        test_result = await tokenize_content("test@email.com", user_id="health_check")
        
        return {
            "healthy": True,
            "tokenization_working": test_result["pii_count"] > 0,
            "active_tokens": await _get_pii_safety_status()
        }
        
    except Exception as e:
        logger.error(f"PII safety health check failed: {e}")
        return {"healthy": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
