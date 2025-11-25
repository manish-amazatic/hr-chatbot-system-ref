"""
Payroll Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List, Any
from decimal import Decimal

from utils.database import get_db
from services.payroll_service import PayrollService
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
class CreatePayrollRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    """Create payroll record request (admin function)"""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., description="Year")
    base_salary: float = Field(..., gt=0, description="Base salary")
    allowances: Optional[Any] = Field(default=None, description="Allowances", json_schema_extra={"type": "object"})
    deductions: Optional[Any] = Field(default=None, description="Deductions", json_schema_extra={"type": "object"})
    payment_date: Optional[date] = Field(None, description="Payment date")
    payment_method: Optional[str] = Field(None, description="Payment method")


class UpdatePaymentStatusRequest(BaseModel):
    """Update payment status request"""
    payment_status: str = Field(..., description="Payment status (Pending, Processed, Paid)")
    payment_date: Optional[date] = Field(None, description="Payment date")
    payment_method: Optional[str] = Field(None, description="Payment method")


class PayrollResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    """Payroll record response"""
    id: str
    employee_id: str
    month: int
    year: int
    base_salary: float
    allowances: Optional[Any] = Field(None, json_schema_extra={"type": "object"})
    gross_salary: float
    deductions: Optional[Any] = Field(None, json_schema_extra={"type": "object"})
    total_deductions: float
    net_salary: float
    payment_date: Optional[str]
    payment_status: str
    payment_method: Optional[str]
    created_at: str
    updated_at: str


class YTDSummaryResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    """Year-to-date summary response"""
    employee_id: str
    year: int
    months_processed: int
    ytd_gross_salary: float
    ytd_deductions: float
    ytd_net_salary: float
    average_monthly_gross: float
    average_monthly_net: float
    months_detail: List[Any] = Field(default_factory=list, json_schema_extra={"type": "array", "items": {"type": "object"}})


@router.get("/records", response_model=List[PayrollResponse])
async def get_payroll_records(
    year: Optional[int] = Query(None, description="Filter by year"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get all payroll records for current employee

    Can be filtered by year and payment status
    """
    try:
        records = await PayrollService.get_payroll_records(
            db,
            current_user["user_id"],
            year,
            status
        )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/payslip/{month}/{year}", response_model=PayrollResponse)
async def get_payslip(
    month: int,
    year: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get payslip for a specific month

    Returns detailed salary breakdown including allowances and deductions
    """
    if not 1 <= month <= 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12"
        )

    try:
        payslip = await PayrollService.get_payslip(
            db,
            current_user["user_id"],
            month,
            year
        )

        if not payslip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payslip not found for {month}/{year}"
            )

        return payslip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/records/{record_id}", response_model=PayrollResponse)
async def get_payslip_by_id(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """Get a specific payslip by record ID"""
    try:
        payslip = await PayrollService.get_payslip_by_id(
            db,
            record_id,
            current_user["user_id"]
        )

        if not payslip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payslip not found"
            )

        return payslip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/records", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll_record(
    request: CreatePayrollRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Create a new payroll record (Admin/Manager function)

    Generates payslip with salary breakdown
    """
    try:
        payroll = await PayrollService.create_payroll_record(
            db,
            current_user["user_id"],
            request.month,
            request.year,
            Decimal(str(request.base_salary)),
            request.allowances,
            request.deductions,
            request.payment_date,
            request.payment_method
        )
        return payroll
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


@router.put("/records/{record_id}/status", response_model=PayrollResponse)
async def update_payment_status(
    record_id: str,
    request: UpdatePaymentStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Update payment status of a payroll record

    Changes status and optionally updates payment date and method
    """
    try:
        payroll = await PayrollService.update_payment_status(
            db,
            record_id,
            current_user["user_id"],
            request.payment_status,
            request.payment_date,
            request.payment_method
        )
        return payroll
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


@router.get("/ytd-summary", response_model=YTDSummaryResponse)
async def get_ytd_summary(
    year: Optional[int] = Query(None, description="Year (defaults to current year)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Get Year-To-Date (YTD) salary summary

    Returns total gross salary, deductions, net salary, and monthly averages
    """
    try:
        summary = await PayrollService.get_ytd_summary(
            db,
            current_user["user_id"],
            year
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payroll_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_employee)
):
    """
    Delete a payroll record (Admin function)

    Cannot delete paid records
    """
    try:
        await PayrollService.delete_payroll_record(
            db,
            record_id,
            current_user["user_id"]
        )
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
