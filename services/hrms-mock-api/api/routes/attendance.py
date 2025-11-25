"""
Attendance Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time
from typing import Optional, List

from utils.database import get_db
from services.attendance_service import AttendanceService
from utils.jwt_utils import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()


async def get_current_employee(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current employee from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload


# Request/Response Models
class MarkAttendanceRequest(BaseModel):
    """Mark attendance request"""
    date: date = Field(..., description="Attendance date")
    check_in_time: Optional[time] = Field(None, description="Check-in time")
    check_out_time: Optional[time] = Field(None, description="Check-out time")
    status: str = Field(default="Present", description="Attendance status")
    notes: Optional[str] = Field(None, description="Additional notes")


class CheckInRequest(BaseModel):
    """Check-in request"""
    check_in_time: Optional[time] = Field(None, description="Check-in time (defaults to now)")


class CheckOutRequest(BaseModel):
    """Check-out request"""
    check_out_time: Optional[time] = Field(None, description="Check-out time (defaults to now)")


class UpdateAttendanceRequest(BaseModel):
    """Update attendance request"""
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AttendanceResponse(BaseModel):
    """Attendance record response"""
    id: str
    employee_id: str
    date: str
    check_in_time: Optional[str]
    check_out_time: Optional[str]
    work_hours: Optional[str]
    status: str
    notes: Optional[str]
    created_at: str
    updated_at: str


class MonthlySummaryResponse(BaseModel):
    """Monthly summary response"""
    employee_id: str
    month: int
    year: int
    total_days: int
    present_days: int
    absent_days: int
    leave_days: int
    half_days: int
    total_work_hours: float
    attendance_percentage: float


@router.post("/check-in", response_model=AttendanceResponse)
async def check_in(
    request: CheckInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Check in for today

    Marks the current day's attendance with check-in time
    """
    try:
        attendance = await AttendanceService.check_in(
            db,
            current_user["user_id"],
            request.check_in_time
        )
        return attendance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/check-out", response_model=AttendanceResponse)
async def check_out(
    request: CheckOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Check out for today

    Marks check-out time and calculates total work hours
    """
    try:
        attendance = await AttendanceService.check_out(
            db,
            current_user["user_id"],
            request.check_out_time
        )
        return attendance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/mark", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    request: MarkAttendanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Mark attendance for a specific date

    Allows marking attendance with full details (admin/manager function)
    """
    try:
        attendance = await AttendanceService.mark_attendance(
            db,
            current_user["user_id"],
            request.date,
            request.check_in_time,
            request.check_out_time,
            request.status,
            request.notes
        )
        return attendance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/records", response_model=List[AttendanceResponse])
async def get_attendance_records(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get attendance records

    Retrieve attendance records with optional date and status filters
    """
    try:
        records = await AttendanceService.get_attendance_records(
            db,
            current_user["user_id"],
            start_date,
            end_date,
            status_filter
        )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/records/date/{attendance_date}", response_model=AttendanceResponse)
async def get_attendance_by_date(
    attendance_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Get attendance record for a specific date"""
    try:
        attendance = await AttendanceService.get_attendance_by_date(
            db,
            current_user["user_id"],
            attendance_date
        )

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found for this date"
            )

        return attendance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/summary/{month}/{year}", response_model=MonthlySummaryResponse)
async def get_monthly_summary(
    month: int,
    year: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get monthly attendance summary

    Returns statistics including total days, present/absent counts, and attendance percentage
    """
    if not 1 <= month <= 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12"
        )

    try:
        summary = await AttendanceService.get_monthly_summary(
            db,
            current_user["user_id"],
            month,
            year
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/records/{record_id}", response_model=AttendanceResponse)
async def update_attendance(
    record_id: str,
    request: UpdateAttendanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Update an attendance record

    Allows updating check-in/check-out times, status, and notes
    """
    try:
        attendance = await AttendanceService.update_attendance(
            db,
            record_id,
            current_user["user_id"],
            request.check_in_time,
            request.check_out_time,
            request.status,
            request.notes
        )
        return attendance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Delete an attendance record"""
    try:
        await AttendanceService.delete_attendance(
            db,
            record_id,
            current_user["user_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
