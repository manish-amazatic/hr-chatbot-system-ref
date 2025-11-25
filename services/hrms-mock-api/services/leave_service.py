"""
Leave Service

Handles all leave-related business logic including:
- Leave balance management
- Leave request creation and management
- Leave approval/rejection workflow
"""
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import List, Optional, Dict
import uuid

from models.leave_balance import LeaveBalance
from models.leave_request import LeaveRequest
from models.employee import Employee


class LeaveService:
    """Service for managing leave operations"""

    @staticmethod
    async def get_leave_balance(db: AsyncSession, employee_id: str, year: Optional[int] = None) -> List[Dict]:
        """
        Get leave balance for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            year: Year (defaults to current year)

        Returns:
            List of leave balances
        """
        if year is None:
            year = datetime.now().year

        query = select(LeaveBalance).where(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.year == year
            )
        )
        result = await db.execute(query)
        balances = result.scalars().all()

        return [balance.to_dict() for balance in balances]

    @staticmethod
    async def get_leave_balance_by_type(
        db: AsyncSession,
        employee_id: str,
        leave_type: str,
        year: Optional[int] = None
    ) -> Optional[Dict]:
        """Get leave balance for a specific leave type"""
        if year is None:
            year = datetime.now().year

        query = select(LeaveBalance).where(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type == leave_type,
                LeaveBalance.year == year
            )
        )
        result = await db.execute(query)
        balance = result.scalar_one_or_none()

        return balance.to_dict() if balance else None

    @staticmethod
    async def apply_leave(
        db: AsyncSession,
        employee_id: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Apply for leave

        Args:
            db: Database session
            employee_id: Employee ID
            leave_type: Type of leave
            start_date: Start date
            end_date: End date
            reason: Reason for leave

        Returns:
            Created leave request

        Raises:
            ValueError: If validation fails
        """
        # Validate dates
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")

        if start_date < date.today():
            raise ValueError("Cannot apply for leave in the past")

        # Calculate days
        days_count = (end_date - start_date).days + 1

        # Check leave balance
        year = start_date.year
        balance = await LeaveService.get_leave_balance_by_type(db, employee_id, leave_type, year)

        if balance and balance["available_days"] < days_count:
            raise ValueError(f"Insufficient leave balance. Available: {balance['available_days']}, Requested: {days_count}")

        # Create leave request
        leave_request = LeaveRequest(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days_count=days_count,
            reason=reason,
            status="Pending"
        )

        db.add(leave_request)
        await db.commit()
        await db.refresh(leave_request)

        return leave_request.to_dict()

    @staticmethod
    async def get_leave_requests(
        db: AsyncSession,
        employee_id: str,
        status: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict]:
        """Get leave requests for an employee"""
        conditions = [LeaveRequest.employee_id == employee_id]

        if status:
            conditions.append(LeaveRequest.status == status)

        if year:
            conditions.append(extract('year', LeaveRequest.start_date) == year)

        query = select(LeaveRequest).where(and_(*conditions)).order_by(LeaveRequest.created_at.desc())
        result = await db.execute(query)
        requests = result.scalars().all()

        return [req.to_dict() for req in requests]

    @staticmethod
    async def get_leave_request_by_id(db: AsyncSession, request_id: str) -> Optional[Dict]:
        """Get a specific leave request"""
        query = select(LeaveRequest).where(LeaveRequest.id == request_id)
        result = await db.execute(query)
        leave_request = result.scalar_one_or_none()

        return leave_request.to_dict() if leave_request else None

    @staticmethod
    async def cancel_leave_request(db: AsyncSession, request_id: str, employee_id: str) -> Dict:
        """Cancel a leave request"""
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.id == request_id,
                LeaveRequest.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        leave_request = result.scalar_one_or_none()

        if not leave_request:
            raise ValueError("Leave request not found")

        if leave_request.status == "Cancelled":
            raise ValueError("Leave request is already cancelled")

        if leave_request.status == "Approved" and leave_request.start_date < date.today():
            raise ValueError("Cannot cancel approved leave that has already started")

        leave_request.status = "Cancelled"
        leave_request.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(leave_request)

        return leave_request.to_dict()

    @staticmethod
    async def approve_leave_request(
        db: AsyncSession,
        request_id: str,
        approved_by: str
    ) -> Dict:
        """Approve a leave request (manager action)"""
        query = select(LeaveRequest).where(LeaveRequest.id == request_id)
        result = await db.execute(query)
        leave_request = result.scalar_one_or_none()

        if not leave_request:
            raise ValueError("Leave request not found")

        if leave_request.status != "Pending":
            raise ValueError(f"Cannot approve leave request with status: {leave_request.status}")

        # Update leave balance
        balance_query = select(LeaveBalance).where(
            and_(
                LeaveBalance.employee_id == leave_request.employee_id,
                LeaveBalance.leave_type == leave_request.leave_type,
                LeaveBalance.year == leave_request.start_date.year
            )
        )
        balance_result = await db.execute(balance_query)
        balance = balance_result.scalar_one_or_none()

        if balance:
            if balance.available_days < leave_request.days_count:
                raise ValueError("Insufficient leave balance")

            balance.used_days += leave_request.days_count
            balance.available_days -= leave_request.days_count
            balance.updated_at = datetime.utcnow()

        # Approve request
        leave_request.status = "Approved"
        leave_request.approved_by = approved_by
        leave_request.approval_date = datetime.utcnow()
        leave_request.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(leave_request)

        return leave_request.to_dict()

    @staticmethod
    async def reject_leave_request(
        db: AsyncSession,
        request_id: str,
        rejected_by: str,
        rejection_reason: Optional[str] = None
    ) -> Dict:
        """Reject a leave request (manager action)"""
        query = select(LeaveRequest).where(LeaveRequest.id == request_id)
        result = await db.execute(query)
        leave_request = result.scalar_one_or_none()

        if not leave_request:
            raise ValueError("Leave request not found")

        if leave_request.status != "Pending":
            raise ValueError(f"Cannot reject leave request with status: {leave_request.status}")

        leave_request.status = "Rejected"
        leave_request.approved_by = rejected_by  # Store who rejected it
        leave_request.rejection_reason = rejection_reason
        leave_request.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(leave_request)

        return leave_request.to_dict()
