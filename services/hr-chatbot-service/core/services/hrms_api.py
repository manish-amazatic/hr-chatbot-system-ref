"""
HRMS API Client - Mock Implementation
Mock client with local data storage (no actual API calls)
"""
import logging
from contextlib import AbstractContextManager, AbstractAsyncContextManager
from contextvars import ContextVar
from typing import Optional, List, Dict, Any
from copy import deepcopy

from core.config import settings

logger = logging.getLogger(__name__)


# Mock HTTPStatusError for compatibility
class HTTPStatusError(Exception):
    """Mock HTTP Status Error"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        self.response = type('obj', (object,), {
            'status_code': status_code,
            'text': message,
            'json': lambda: {"detail": message}
        })
        super().__init__(message)


class HRMSClient:
    """
    Mock HRMS Client with local data storage (no actual API calls)

    Handles all HRMS operations with in-memory data:
    - Leave management (balance, requests, applications)
    - Attendance tracking (records, check-in/out)
    - Payroll queries (payslips, YTD summaries)

    Usage:
        client = HRMSClient()
        balance = await client.get_leave_balance()
    """
    
    # Class-level storage for mock data (shared across instances)
    _leave_requests = []
    _leave_request_counter = 1
    _attendance_records = []
    _attendance_counter = 1
    _payroll_records = []
    _checked_in_today = False
    
    # Initial mock data
    _initial_leave_balance = {
        "employee_id": "EMP001",
        "year": 2025,
        "balances": [
            {"leave_type": "Annual", "total_days": 20, "used_days": 5, "available_days": 15},
            {"leave_type": "Sick", "total_days": 10, "used_days": 2, "available_days": 8},
            {"leave_type": "Casual", "total_days": 7, "used_days": 1, "available_days": 6}
        ]
    }

    def __init__(self):
        """
        Initialize HRMS mock client

        """

        # Initialize mock data on first instantiation
        if not HRMSClient._leave_requests:
            self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock data for testing"""
        # Add some initial leave requests
        HRMSClient._leave_requests = [
            {
                "id": "LR001",
                "employee_id": "EMP001",
                "leave_type": "Annual",
                "start_date": "2025-11-15",
                "end_date": "2025-11-17",
                "days": 3,
                "reason": "Family vacation",
                "status": "Approved",
                "applied_date": "2025-11-01",
                "approved_date": "2025-11-02"
            },
            {
                "id": "LR002",
                "employee_id": "EMP001",
                "leave_type": "Sick",
                "start_date": "2025-10-20",
                "end_date": "2025-10-21",
                "days": 2,
                "reason": "Medical appointment",
                "status": "Approved",
                "applied_date": "2025-10-18",
                "approved_date": "2025-10-19"
            }
        ]
        HRMSClient._leave_request_counter = 3
        
        # Add some attendance records
        HRMSClient._attendance_records = [
            {
                "id": "ATT001",
                "employee_id": "EMP001",
                "date": "2025-11-28",
                "status": "Present",
                "check_in_time": "09:00:00",
                "check_out_time": "18:00:00",
                "work_hours": 9.0
            },
            {
                "id": "ATT002",
                "employee_id": "EMP001",
                "date": "2025-11-27",
                "status": "Present",
                "check_in_time": "09:15:00",
                "check_out_time": "17:45:00",
                "work_hours": 8.5
            },
            {
                "id": "ATT003",
                "employee_id": "EMP001",
                "date": "2025-11-26",
                "status": "Present",
                "check_in_time": "08:55:00",
                "check_out_time": "18:10:00",
                "work_hours": 9.25
            }
        ]
        HRMSClient._attendance_counter = 4
        
        # Add payroll records
        HRMSClient._payroll_records = [
            {
                "id": "PAY001",
                "employee_id": "EMP001",
                "month": 11,
                "year": 2025,
                "base_salary": 75000,
                "allowances": {
                    "HRA": 15000,
                    "Transport": 2000,
                    "Special": 5000
                },
                "deductions": {
                    "Tax": 12000,
                    "PF": 9000,
                    "Insurance": 1500
                },
                "gross_salary": 97000,
                "net_salary": 74500,
                "payment_date": "2025-11-30",
                "payment_status": "Paid"
            },
            {
                "id": "PAY002",
                "employee_id": "EMP001",
                "month": 10,
                "year": 2025,
                "base_salary": 75000,
                "allowances": {
                    "HRA": 15000,
                    "Transport": 2000,
                    "Special": 5000
                },
                "deductions": {
                    "Tax": 12000,
                    "PF": 9000,
                    "Insurance": 1500
                },
                "gross_salary": 97000,
                "net_salary": 74500,
                "payment_date": "2025-10-31",
                "payment_status": "Paid"
            }
        ]

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token"""
        # Try to get token from: 1) context variable, 2) instance token
        token = _auth_token_context.get() or self._instance_token
        token = token.strip()
        if token:
            if not token.startswith("Bearer "):
                token = f"Bearer {token}"

            if token.startswith("bearer "):
                if token := token[7:].strip():
                    token = "Bearer " + token

            if token.startswith("Bearer "):
                return token

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}

        # Try to get token from: 1) context variable, 2) instance token
        token = _auth_token_context.get() or self._instance_token

        if token := self.token:
            headers["Authorization"] = token
        return headers

    async def close(self):
        """Close the HTTP client (no-op in mock)"""
        logger.debug("Mock client close called (no-op)")

    # ==================== Leave Management ====================

    async def get_leave_balance(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get leave balance for the authenticated user (mock data)

        Args:
            year: Year to get balance for (defaults to current year)

        Returns:
            Mock leave balance data
        """
        logger.info("Mock: Getting leave balance for year %s", year or 2025)
        balance = deepcopy(self._initial_leave_balance)
        if year:
            balance["year"] = year
        return balance

    async def apply_leave(
        self,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply for leave (mock implementation)

        Args:
            leave_type: Type of leave (Annual, Sick, Casual, etc.)
            start_date: Leave start date (YYYY-MM-DD)
            end_date: Leave end date (YYYY-MM-DD)
            reason: Optional reason for leave

        Returns:
            Created leave request with status
        """
        logger.info("Mock: Applying for %s leave from %s to %s", leave_type, start_date, end_date)
        
        # Calculate days
        from datetime import datetime as dt
        start = dt.strptime(start_date, "%Y-%m-%d")
        end = dt.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        # Create new leave request
        request_id = f"LR{HRMSClient._leave_request_counter:03d}"
        HRMSClient._leave_request_counter += 1
        
        new_request = {
            "id": request_id,
            "employee_id": "EMP001",
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "days": days,
            "reason": reason or "No reason provided",
            "status": "Pending",
            "applied_date": dt.now().strftime("%Y-%m-%d"),
            "approved_date": None
        }
        
        HRMSClient._leave_requests.append(new_request)
        return new_request

    async def get_leave_requests(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get leave requests for authenticated user (mock data)

        Args:
            status: Filter by status (Pending, Approved, Rejected, Cancelled)
            start_date: Filter from this date
            end_date: Filter to this date

        Returns:
            List of leave requests
        """
        logger.info("Mock: Getting leave requests (status=%s)", status)
        
        requests = deepcopy(HRMSClient._leave_requests)
        
        # Filter by status
        if status:
            requests = [r for r in requests if r["status"] == status]
        
        # Filter by date range
        if start_date:
            requests = [r for r in requests if r["start_date"] >= start_date]
        if end_date:
            requests = [r for r in requests if r["end_date"] <= end_date]
        
        return requests

    async def get_leave_request(self, request_id: str) -> Dict[str, Any]:
        """
        Get a specific leave request by ID (mock data)

        Args:
            request_id: Leave request ID

        Returns:
            Leave request details
        """
        logger.info("Mock: Getting leave request %s", request_id)
        
        for request in HRMSClient._leave_requests:
            if request["id"] == request_id:
                return deepcopy(request)
        
        raise HTTPStatusError("Leave request not found", 404)

    async def cancel_leave_request(self, request_id: str) -> Dict[str, Any]:
        """
        Cancel a pending or approved leave request (mock implementation)

        Args:
            request_id: Leave request ID to cancel

        Returns:
            Updated leave request
        """
        logger.info("Mock: Cancelling leave request %s", request_id)
        
        for request in HRMSClient._leave_requests:
            if request["id"] == request_id:
                if request["status"] in ["Pending", "Approved"]:
                    request["status"] = "Cancelled"
                    return deepcopy(request)
                else:
                    raise HTTPStatusError(f"Cannot cancel request with status {request['status']}", 400)
        
        raise HTTPStatusError("Leave request not found", 404)

    # ==================== Attendance Management ====================

    async def get_attendance_records(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get attendance records for authenticated user (mock data)

        Args:
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)
            status: Filter by status (Present, Absent, etc.)

        Returns:
            List of attendance records
        """
        logger.info("Mock: Getting attendance records (start=%s, end=%s, status=%s)", start_date, end_date, status)
        
        records = deepcopy(HRMSClient._attendance_records)
        
        # Filter by date range
        if start_date:
            records = [r for r in records if r["date"] >= start_date]
        if end_date:
            records = [r for r in records if r["date"] <= end_date]
        
        # Filter by status
        if status:
            records = [r for r in records if r["status"] == status]
        
        return records

    async def get_attendance_summary(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get attendance summary for a month (mock data)

        Args:
            month: Month (1-12)
            year: Year

        Returns:
            Attendance summary with statistics
        """
        logger.info("Mock: Getting attendance summary for %s/%s", month or 11, year or 2025)
        
        # Count records for the month
        present_days = len([r for r in HRMSClient._attendance_records if r["status"] == "Present"])
        total_work_hours = sum(r.get("work_hours", 0) for r in HRMSClient._attendance_records)
        
        return {
            "month": month or 11,
            "year": year or 2025,
            "total_days": 30,
            "present_days": present_days,
            "absent_days": 0,
            "leave_days": 2,
            "total_work_hours": total_work_hours,
            "average_work_hours": total_work_hours / present_days if present_days > 0 else 0
        }

    async def check_in(self) -> Dict[str, Any]:
        """
        Mark check-in for today (mock implementation)

        Returns:
            Attendance record
        """
        logger.info("Mock: Checking in")
        
        if HRMSClient._checked_in_today:
            raise HTTPStatusError("Already checked in today", 400)
        
        from datetime import datetime as dt
        today = dt.now().strftime("%Y-%m-%d")
        check_in_time = dt.now().strftime("%H:%M:%S")
        
        record = {
            "id": f"ATT{HRMSClient._attendance_counter:03d}",
            "employee_id": "EMP001",
            "date": today,
            "status": "Present",
            "check_in_time": check_in_time,
            "check_out_time": None,
            "work_hours": 0
        }
        
        HRMSClient._attendance_counter += 1
        HRMSClient._attendance_records.append(record)
        HRMSClient._checked_in_today = True
        
        return deepcopy(record)

    async def check_out(self) -> Dict[str, Any]:
        """
        Mark check-out for today (mock implementation)

        Returns:
            Updated attendance record
        """
        logger.info("Mock: Checking out")
        
        if not HRMSClient._checked_in_today:
            raise HTTPStatusError("Not checked in today", 400)
        
        from datetime import datetime as dt
        today = dt.now().strftime("%Y-%m-%d")
        check_out_time = dt.now().strftime("%H:%M:%S")
        
        # Find today's record
        for record in HRMSClient._attendance_records:
            if record["date"] == today and record["check_out_time"] is None:
                # Calculate work hours (simplified)
                record["check_out_time"] = check_out_time
                record["work_hours"] = 9.0  # Simplified calculation
                HRMSClient._checked_in_today = False
                return deepcopy(record)
        
        raise HTTPStatusError("No check-in record found for today", 404)

    # ==================== Payroll Management ====================

    async def get_current_payslip(self) -> Dict[str, Any]:
        """
        Get current month's payslip (mock data)

        Returns:
            Payslip details
        """
        logger.info("Mock: Getting current payslip")
        
        # Return November 2025 payslip
        if HRMSClient._payroll_records:
            return deepcopy(HRMSClient._payroll_records[0])
        
        raise HTTPStatusError("No payslip found", 404)

    async def get_payslip(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get payslip for a specific month (mock data)

        Args:
            month: Month (1-12)
            year: Year

        Returns:
            Payslip details
        """
        logger.info("Mock: Getting payslip for %s/%s", month or 11, year or 2025)
        
        # Find matching payslip
        for record in HRMSClient._payroll_records:
            if (not month or record["month"] == month) and (not year or record["year"] == year):
                return deepcopy(record)
        
        raise HTTPStatusError("Payslip not found", 404)

    async def get_ytd_summary(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get year-to-date payroll summary (mock data)

        Args:
            year: Year (defaults to current year)

        Returns:
            YTD summary with earnings and deductions
        """
        logger.info("Mock: Getting YTD summary for %s", year or 2025)
        
        # Calculate from all payroll records for the year
        year_records = [r for r in HRMSClient._payroll_records if r["year"] == (year or 2025)]
        
        total_gross = sum(r["gross_salary"] for r in year_records)
        total_net = sum(r["net_salary"] for r in year_records)
        total_tax = sum(r["deductions"].get("Tax", 0) for r in year_records)
        
        return {
            "year": year or 2025,
            "total_gross_salary": total_gross,
            "total_deductions": total_gross - total_net,
            "total_net_salary": total_net,
            "total_tax_deducted": total_tax,
            "months_paid": len(year_records),
            "average_monthly_gross": total_gross / len(year_records) if year_records else 0,
            "average_monthly_net": total_net / len(year_records) if year_records else 0
        }

    async def get_tax_summary(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get tax summary for a year (mock data)

        Args:
            year: Tax year (defaults to current year)

        Returns:
            Tax summary
        """
        logger.info("Mock: Getting tax summary for %s", year or 2025)
        
        # Calculate from all payroll records for the year
        year_records = [r for r in HRMSClient._payroll_records if r["year"] == (year or 2025)]
        
        total_tax = sum(r["deductions"].get("Tax", 0) for r in year_records)
        total_pf = sum(r["deductions"].get("PF", 0) for r in year_records)
        total_gross = sum(r["gross_salary"] for r in year_records)
        
        return {
            "year": year or 2025,
            "total_taxable_income": total_gross,
            "total_tax_deducted": total_tax,
            "total_pf_contribution": total_pf,
            "tax_rate_percentage": (total_tax / total_gross * 100) if total_gross > 0 else 0,
            "months_processed": len(year_records)
        }

    @staticmethod
    def format_http_error(e: HTTPStatusError) -> str:
        """
        Turn HTTPStatusError into concise user-friendly messages.
        """
        status = e.response.status_code if e.response else None
        detail = None
        try:
            data = e.response.json()
            detail = data.get("detail") or data.get("message") or data.get("error") or data
        except (ValueError, AttributeError, TypeError):
            detail = e.response.text if e.response else str(e)

        if status == 400:
            return f"Invalid request. {detail}"
        if status == 401:
            return "Authentication failed. Please sign in again."
        if status == 403:
            return "You don’t have permission to perform this action."
        if status == 404:
            return "Resource not found."
        if status == 409:
            return "Request conflicts with existing records."
        if status == 422:
            return f"Validation error. {detail}"
        if status and status >= 500:
            return "Service is currently unavailable. Please try again later."
        return f"Request failed. {detail}"

    # ==================== Context Manager Support ====================

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


hrms_client = HRMSClient()

__all__ = ["HRMSClient", "hrms_client", "AuthToken", "HTTPStatusError"]
