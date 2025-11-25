"""
HRMS Mock API - Main FastAPI Application
Provides mock HR data APIs for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from utils.config import settings
from utils.database import init_db, close_db
from api.routes import health, auth, leave  # attendance, payroll - DISABLED due to Pydantic recursion error

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Create data directory
    os.makedirs("data", exist_ok=True)

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down HRMS Mock API")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Mock HRMS API for development and testing",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(leave.router, prefix="/api/v1/leave", tags=["Leave Management"])
# app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance Management"])  # DISABLED - Pydantic recursion error
# app.include_router(payroll.router, prefix="/api/v1/payroll", tags=["Payroll Management"])  # DISABLED - Pydantic recursion error

# TODO: Add employee router


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
