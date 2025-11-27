"""
Leave Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

from utils.database import get_db
from services.leave_service import LeaveService
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
class LeaveApplicationRequest(BaseModel):
    """Leave application request"""
    leave_type: str = Field(..., description="Type of leave (Annual, Sick, Casual, etc.)")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    reason: Optional[str] = Field(None, description="Reason for leave")


class LeaveRequestResponse(BaseModel):
    """Leave request response"""
    id: str
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    days_count: int
    reason: Optional[str]
    status: str
    approved_by: Optional[str]
    approval_date: Optional[str]
    rejection_reason: Optional[str]
    created_at: str
    updated_at: str


class LeaveBalance(BaseModel):
    """Leave balance response"""
    id: str
    employee_id: str
    leave_type: str
    total_days: int
    used_days: int
    available_days: int
    year: int


class LeaveBalanceResponse(BaseModel):
    """Leave balance response"""
    employee_id: str
    year: int
    balances: List[LeaveBalance]


class ApproveRejectRequest(BaseModel):
    """Approve/Reject leave request"""
    reason: Optional[str] = Field(None, description="Reason for rejection (if rejecting)")


# NOTE: Static routes must come BEFORE parametrized routes in FastAPI

@router.get("/types")
async def get_leave_types():
    """Get available leave types"""
    return {
        "leave_types": [
            {"code": "annual", "name": "Annual Leave", "description": "Paid annual leave"},
            {"code": "sick", "name": "Sick Leave", "description": "Medical leave"},
            {"code": "casual", "name": "Casual Leave", "description": "Short unplanned leave"},
            {"code": "maternity", "name": "Maternity Leave", "description": "Maternity leave"},
            {"code": "paternity", "name": "Paternity Leave", "description": "Paternity leave"},
            {"code": "unpaid", "name": "Unpaid Leave", "description": "Leave without pay"}
        ]
    }


@router.get("/history", response_model=List[LeaveRequestResponse])
async def get_leave_history(
    year: Optional[int] = Query(None, description="Filter by year"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Get leave history (past approved leaves)"""
    try:
        requests = await LeaveService.get_leave_requests(
            db,
            current_user["user_id"],
            "approved",
            year
        )
        return requests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/calendar")
async def get_leave_calendar(
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Get team leave calendar"""
    # Mock team calendar
    return {
        "team_leaves": [
            {
                "employee_name": "John Doe",
                "leave_type": "Annual Leave",
                "start_date": "2025-12-20",
                "end_date": "2025-12-24",
                "days_count": 5
            },
            {
                "employee_name": "Jane Smith",
                "leave_type": "Sick Leave",
                "start_date": "2025-12-15",
                "end_date": "2025-12-16",
                "days_count": 2
            }
        ]
    }


@router.get("/balance/types", response_model=List[LeaveBalance])
async def get_leave_balance_by_type(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Get balance by leave type"""
    try:
        balances = await LeaveService.get_leave_balance(
            db,
            current_user["user_id"],
            None
        )
        return balances
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/balance", response_model=LeaveBalanceResponse)
async def get_leave_balance(
    year: Optional[int] = Query(None, description="Year (defaults to current year)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get leave balance for current employee

    Returns all leave types with their balances for the specified year
    or current year if not specified.
    """
    try:
        user_id = current_user["user_id"]
        year = year or date.today().year

        balances = await LeaveService.get_leave_balance(db, user_id, year)
        return {
            "employee_id": user_id,
            "year": year,
            "balances": balances
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def apply_leave(
    request: LeaveApplicationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Apply for leave

    Creates a new leave request with status "Pending"
    """
    try:
        leave_request = await LeaveService.apply_leave(
            db,
            current_user["user_id"],
            request.leave_type,
            request.start_date,
            request.end_date,
            request.reason
        )
        return leave_request
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


@router.get("/requests", response_model=List[LeaveRequestResponse])
async def get_leave_requests(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get all leave requests for current employee

    Can be filtered by status and year
    """
    try:
        requests = await LeaveService.get_leave_requests(
            db,
            current_user["user_id"],
            status_filter,
            year
        )
        return requests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/requests/{request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Get a specific leave request"""
    try:
        leave_request = await LeaveService.get_leave_request_by_id(db, request_id)

        if not leave_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )

        # Verify ownership
        if leave_request["employee_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this leave request"
            )

        return leave_request
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/requests/{request_id}/cancel", response_model=LeaveRequestResponse)
async def cancel_leave_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Cancel a leave request

    Only pending or approved (not started) requests can be cancelled
    """
    try:
        leave_request = await LeaveService.cancel_leave_request(
            db,
            request_id,
            current_user["user_id"]
        )
        return leave_request
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


@router.put("/requests/{request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Approve a leave request (Manager action)

    Updates leave balance when approved
    """
    try:
        leave_request = await LeaveService.approve_leave_request(
            db,
            request_id,
            current_user["user_id"]
        )
        return leave_request
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


@router.put("/requests/{request_id}/reject", response_model=LeaveRequestResponse)
async def reject_leave_request(
    request_id: str,
    request: ApproveRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Reject a leave request (Manager action)

    Optionally provide a rejection reason
    """
    try:
        leave_request = await LeaveService.reject_leave_request(
            db,
            request_id,
            current_user["user_id"],
            request.reason
        )
        return leave_request
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
