"""
🚀 AIRMS+ Main Application
AI-Powered Risk Mitigation & Misinformation Detection System
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import mongodb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting AIRMS+ API")
    
    # Connect to MongoDB
    try:
        await mongodb.connect()
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
    
    yield
    
    # Close MongoDB connection
    try:
        await mongodb.disconnect()
        logger.info("👋 MongoDB disconnected")
    except:
        pass
    logger.info("👋 Shutting down AIRMS+ API")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Risk Mitigation & Misinformation Detection System",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
try:
    from app.api.middleware.rate_limiter import rate_limit_middleware
    app.middleware("http")(rate_limit_middleware)
    logger.info("✅ Rate limiting middleware loaded")
except Exception as e:
    logger.warning(f"⚠️ Rate limiting middleware not loaded: {e}")

# Import and include API routes
try:
    from app.api.v1 import router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")
    logger.info("✅ API v1 routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load API routes: {e}")

# Add a debug endpoint to list all routes
@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            route_info = {
                "path": route.path,
                "name": getattr(route, 'name', 'unknown'),
                "methods": list(getattr(route, 'methods', []))
            }
            routes.append(route_info)
    
    return {
        "total_routes": len(routes),
        "routes": routes
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AIRMS+ API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "api_v1": "/api/v1",
            "debug_routes": "/debug/routes"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-09-26T01:19:24.082Z",
        "version": settings.APP_VERSION
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)}
    )
