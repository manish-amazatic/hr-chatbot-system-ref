"""
HRMS API Client
Async HTTP client for communicating with HRMS Mock API
"""
import httpx
import logging
from typing import Optional, List, Dict, Any
from datetime import date

from utils.config import settings

logger = logging.getLogger(__name__)


class HRMSClient:
    """
    Async HTTP client for HRMS Mock API

    Handles all communication with the HRMS system including:
    - Leave management
    - Attendance tracking (when available)
    - Payroll queries (when available)

    Usage:
        client = HRMSClient(token="Bearer xyz...")
        balance = await client.get_leave_balance()
    """

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize HRMS client

        Args:
            token: JWT token for authentication (format: "Bearer <token>")
            base_url: HRMS API base URL (defaults to settings)
        """
        self.base_url = base_url or settings.hrms_api_url
        self.token = token
        self.client = httpx.AsyncClient(timeout=30.0)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = self.token
        return headers

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    # ==================== Leave Management ====================

    async def get_leave_balance(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get leave balance for the authenticated user

        Args:
            year: Year to get balance for (defaults to current year)

        Returns:
            Leave balance data with types and days available

        Example:
            >>> balance = await client.get_leave_balance()
            >>> print(balance)
            {
                "employee_id": "EMP001",
                "year": 2025,
                "balances": [
                    {"leave_type": "Annual", "total_days": 20, "used_days": 5, "available_days": 15},
                    {"leave_type": "Sick", "total_days": 10, "used_days": 2, "available_days": 8}
                ]
            }
        """
        try:
            params = {"year": year} if year else {}
            response = await self.client.get(
                f"{self.base_url}/api/v1/leave/balance",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting leave balance: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting leave balance: {str(e)}")
            raise

    async def apply_leave(
        self,
        leave_type: str,
        start_date: str,
        end_date: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply for leave

        Args:
            leave_type: Type of leave (Annual, Sick, Casual, etc.)
            start_date: Leave start date (YYYY-MM-DD)
            end_date: Leave end date (YYYY-MM-DD)
            reason: Optional reason for leave

        Returns:
            Created leave request with status

        Example:
            >>> request = await client.apply_leave(
            ...     leave_type="Sick",
            ...     start_date="2025-12-01",
            ...     end_date="2025-12-02",
            ...     reason="Doctor's appointment"
            ... )
        """
        try:
            data = {
                "leave_type": leave_type,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason
            }
            response = await self.client.post(
                f"{self.base_url}/api/v1/leave/requests",
                headers=self._get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error applying for leave: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error applying for leave: {str(e)}")
            raise

    async def get_leave_requests(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get leave requests for authenticated user

        Args:
            status: Filter by status (Pending, Approved, Rejected, Cancelled)
            start_date: Filter from this date
            end_date: Filter to this date

        Returns:
            List of leave requests
        """
        try:
            params = {}
            if status:
                params["status"] = status
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            response = await self.client.get(
                f"{self.base_url}/api/v1/leave/requests",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting leave requests: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting leave requests: {str(e)}")
            raise

    async def get_leave_request(self, request_id: str) -> Dict[str, Any]:
        """
        Get a specific leave request by ID

        Args:
            request_id: Leave request ID

        Returns:
            Leave request details
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/leave/requests/{request_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting leave request: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting leave request: {str(e)}")
            raise

    async def cancel_leave_request(self, request_id: str) -> Dict[str, Any]:
        """
        Cancel a pending or approved leave request

        Args:
            request_id: Leave request ID to cancel

        Returns:
            Updated leave request
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/api/v1/leave/requests/{request_id}/cancel",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error cancelling leave request: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error cancelling leave request: {str(e)}")
            raise

    # ==================== Attendance Management ====================

    async def get_attendance_records(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get attendance records for authenticated user

        Args:
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)
            status: Filter by status (Present, Absent, etc.)

        Returns:
            List of attendance records
        """
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if status:
                params["status"] = status

            response = await self.client.get(
                f"{self.base_url}/api/v1/attendance/records",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting attendance records: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting attendance records: {str(e)}")
            raise

    async def get_attendance_summary(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get attendance summary for a month

        Args:
            month: Month (1-12)
            year: Year

        Returns:
            Attendance summary with statistics
        """
        try:
            params = {}
            if month:
                params["month"] = month
            if year:
                params["year"] = year

            response = await self.client.get(
                f"{self.base_url}/api/v1/attendance/summary",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting attendance summary: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting attendance summary: {str(e)}")
            raise

    async def check_in(self) -> Dict[str, Any]:
        """
        Mark check-in for today

        Returns:
            Attendance record
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/attendance/checkin",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error checking in: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error checking in: {str(e)}")
            raise

    async def check_out(self) -> Dict[str, Any]:
        """
        Mark check-out for today

        Returns:
            Updated attendance record
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/attendance/checkout",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error checking out: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error checking out: {str(e)}")
            raise

    # ==================== Payroll Management ====================

    async def get_current_payslip(self) -> Dict[str, Any]:
        """
        Get current month's payslip

        Returns:
            Payslip details
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/payroll/current",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting current payslip: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting current payslip: {str(e)}")
            raise

    async def get_payslip(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get payslip for a specific month

        Args:
            month: Month (1-12)
            year: Year

        Returns:
            Payslip details
        """
        try:
            params = {}
            if month:
                params["month"] = month
            if year:
                params["year"] = year

            response = await self.client.get(
                f"{self.base_url}/api/v1/payroll/breakdown",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting payslip: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting payslip: {str(e)}")
            raise

    async def get_ytd_summary(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get year-to-date payroll summary

        Args:
            year: Year (defaults to current year)

        Returns:
            YTD summary with earnings and deductions
        """
        try:
            params = {}
            if year:
                params["year"] = year

            response = await self.client.get(
                f"{self.base_url}/api/v1/payroll/ytd",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting YTD summary: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting YTD summary: {str(e)}")
            raise

    async def get_tax_summary(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get tax summary for a year

        Args:
            year: Tax year (defaults to current year)

        Returns:
            Tax summary
        """
        try:
            params = {}
            if year:
                params["year"] = year

            response = await self.client.get(
                f"{self.base_url}/api/v1/payroll/tax-summary",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting tax summary: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting tax summary: {str(e)}")
            raise

    # ==================== Context Manager Support ====================

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
