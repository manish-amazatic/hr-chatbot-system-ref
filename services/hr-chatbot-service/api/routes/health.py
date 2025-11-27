"""
Health Check Endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "up",
            "database": "pending",  # TODO: Check database
            "milvus": "pending",     # TODO: Check Milvus
            "hrms_api": "pending"    # TODO: Check HRMS API
        }
    }


@router.get("/config")
async def get_config():
    """Get application configuration (non-sensitive)"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "milvus_collection": settings.milvus_collection_name,
        "debug": settings.debug
    }
