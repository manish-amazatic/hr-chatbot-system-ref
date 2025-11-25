"""
Health Check Endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from utils.config import settings

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
            "database": "pending"  # TODO: Check database
        }
    }


@router.get("/system/stats")
async def system_stats():
    """System statistics"""
    # TODO: Add real statistics
    return {
        "employees": 5,
        "leave_requests": 0,
        "attendance_records": 0,
        "payroll_records": 0
    }
