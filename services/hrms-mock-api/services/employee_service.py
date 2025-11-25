"""
Employee Service
Handles CRUD operations for employees and related HR data
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
from datetime import datetime, date

from models import Employee, LeaveBalance, LeaveRequest, AttendanceRecord, PayrollRecord


class EmployeeService:
    """
    Service for managing employees and HR data

    Provides CRUD operations for:
    - Employees
    - Leave balances and requests
    - Attendance records
    - Payroll records
    """

    # ==================== Employee Operations ====================

    @staticmethod
    def get_employee(db: Session, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID

        Args:
            db: Database session
            employee_id: Employee ID (e.g., EMP001)

        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
        """
        Get employee by email

        Args:
            db: Database session
            email: Employee email

        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        return db.query(Employee).filter(Employee.email == email).first()

    @staticmethod
    def get_all_employees(
        db: Session,
        department: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Employee]:
        """
        Get all employees with optional filtering

        Args:
            db: Database session
            department: Optional department filter
            is_active: Filter by active status (default: True)
            limit: Maximum number of employees to return
            offset: Offset for pagination

        Returns:
            List[Employee]: List of employees
        """
        query = db.query(Employee).filter(Employee.is_active == is_active)

        if department:
            query = query.filter(Employee.department == department)

        return query.order_by(Employee.id).limit(limit).offset(offset).all()

    # ==================== Leave Balance Operations ====================

    @staticmethod
    def get_leave_balances(
        db: Session,
        employee_id: str,
        year: Optional[int] = None
    ) -> List[LeaveBalance]:
        """
        Get leave balances for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            year: Optional year filter (default: current year)

        Returns:
            List[LeaveBalance]: List of leave balances
        """
        if year is None:
            year = datetime.now().year

        return (
            db.query(LeaveBalance)
            .filter(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.year == year
                )
            )
            .all()
        )

    @staticmethod
    def get_leave_balance_by_type(
        db: Session,
        employee_id: str,
        leave_type: str,
        year: Optional[int] = None
    ) -> Optional[LeaveBalance]:
        """
        Get leave balance for specific type

        Args:
            db: Database session
            employee_id: Employee ID
            leave_type: Leave type (Annual, Sick, Casual, etc.)
            year: Optional year filter (default: current year)

        Returns:
            Optional[LeaveBalance]: The leave balance if found, None otherwise
        """
        if year is None:
            year = datetime.now().year

        return (
            db.query(LeaveBalance)
            .filter(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.leave_type == leave_type,
                    LeaveBalance.year == year
                )
            )
            .first()
        )

    # ==================== Leave Request Operations ====================

    @staticmethod
    def get_leave_requests(
        db: Session,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LeaveRequest]:
        """
        Get leave requests with optional filtering

        Args:
            db: Database session
            employee_id: Optional employee ID filter
            status: Optional status filter (Pending, Approved, Rejected)
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of requests to return
            offset: Offset for pagination

        Returns:
            List[LeaveRequest]: List of leave requests
        """
        query = db.query(LeaveRequest)

        if employee_id:
            query = query.filter(LeaveRequest.employee_id == employee_id)

        if status:
            query = query.filter(LeaveRequest.status == status)

        if start_date:
            query = query.filter(LeaveRequest.start_date >= start_date)

        if end_date:
            query = query.filter(LeaveRequest.end_date <= end_date)

        return (
            query.order_by(desc(LeaveRequest.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_leave_request(db: Session, request_id: str) -> Optional[LeaveRequest]:
        """
        Get leave request by ID

        Args:
            db: Database session
            request_id: Leave request UUID

        Returns:
            Optional[LeaveRequest]: The leave request if found, None otherwise
        """
        return db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()

    @staticmethod
    def create_leave_request(
        db: Session,
        employee_id: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        days_count: int,
        reason: Optional[str] = None
    ) -> LeaveRequest:
        """
        Create a new leave request

        Args:
            db: Database session
            employee_id: Employee ID
            leave_type: Leave type
            start_date: Start date
            end_date: End date
            days_count: Number of days
            reason: Optional reason

        Returns:
            LeaveRequest: The created leave request
        """
        request = LeaveRequest(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days_count=days_count,
            reason=reason,
            status="Pending"
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def update_leave_request_status(
        db: Session,
        request_id: str,
        status: str,
        approved_by: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[LeaveRequest]:
        """
        Update leave request status

        Args:
            db: Database session
            request_id: Leave request UUID
            status: New status (Approved, Rejected, Cancelled)
            approved_by: Employee ID who approved/rejected
            rejection_reason: Optional rejection reason

        Returns:
            Optional[LeaveRequest]: Updated leave request if found, None otherwise
        """
        request = EmployeeService.get_leave_request(db, request_id)
        if request:
            request.status = status
            request.approved_by = approved_by
            request.rejection_reason = rejection_reason
            if status in ["Approved", "Rejected"]:
                request.approval_date = datetime.utcnow()
            request.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(request)
        return request

    # ==================== Attendance Operations ====================

    @staticmethod
    def get_attendance_records(
        db: Session,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AttendanceRecord]:
        """
        Get attendance records for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            List[AttendanceRecord]: List of attendance records
        """
        query = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id
        )

        if start_date:
            query = query.filter(AttendanceRecord.date >= start_date)

        if end_date:
            query = query.filter(AttendanceRecord.date <= end_date)

        return query.order_by(AttendanceRecord.date).limit(limit).offset(offset).all()

    @staticmethod
    def get_attendance_record(
        db: Session,
        employee_id: str,
        date: date
    ) -> Optional[AttendanceRecord]:
        """
        Get attendance record for a specific date

        Args:
            db: Database session
            employee_id: Employee ID
            date: Date

        Returns:
            Optional[AttendanceRecord]: The attendance record if found, None otherwise
        """
        return (
            db.query(AttendanceRecord)
            .filter(
                and_(
                    AttendanceRecord.employee_id == employee_id,
                    AttendanceRecord.date == date
                )
            )
            .first()
        )

    # ==================== Payroll Operations ====================

    @staticmethod
    def get_payroll_records(
        db: Session,
        employee_id: str,
        year: Optional[int] = None,
        limit: int = 12,
        offset: int = 0
    ) -> List[PayrollRecord]:
        """
        Get payroll records for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            year: Optional year filter
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            List[PayrollRecord]: List of payroll records
        """
        query = db.query(PayrollRecord).filter(
            PayrollRecord.employee_id == employee_id
        )

        if year:
            query = query.filter(PayrollRecord.year == year)

        return (
            query.order_by(desc(PayrollRecord.year), desc(PayrollRecord.month))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_payroll_record(
        db: Session,
        employee_id: str,
        month: int,
        year: int
    ) -> Optional[PayrollRecord]:
        """
        Get payroll record for a specific month

        Args:
            db: Database session
            employee_id: Employee ID
            month: Month (1-12)
            year: Year

        Returns:
            Optional[PayrollRecord]: The payroll record if found, None otherwise
        """
        return (
            db.query(PayrollRecord)
            .filter(
                and_(
                    PayrollRecord.employee_id == employee_id,
                    PayrollRecord.month == month,
                    PayrollRecord.year == year
                )
            )
            .first()
        )

    # ==================== Statistics and Aggregations ====================

    @staticmethod
    def get_employee_summary(db: Session, employee_id: str, year: Optional[int] = None):
        """
        Get comprehensive summary for an employee

        Args:
            db: Database session
            employee_id: Employee ID
            year: Optional year filter (default: current year)

        Returns:
            dict: Employee summary including leave balances, attendance, etc.
        """
        if year is None:
            year = datetime.now().year

        employee = EmployeeService.get_employee(db, employee_id)
        if not employee:
            return None

        # Get leave balances
        leave_balances = EmployeeService.get_leave_balances(db, employee_id, year)

        # Get pending leave requests
        pending_requests = EmployeeService.get_leave_requests(
            db, employee_id=employee_id, status="Pending"
        )

        # Get recent payroll
        payroll_records = EmployeeService.get_payroll_records(
            db, employee_id, year=year, limit=3
        )

        return {
            "employee": employee.to_dict(),
            "leave_balances": [lb.to_dict() for lb in leave_balances],
            "pending_leave_requests": [req.to_dict() for req in pending_requests],
            "recent_payroll": [pr.to_dict() for pr in payroll_records]
        }
