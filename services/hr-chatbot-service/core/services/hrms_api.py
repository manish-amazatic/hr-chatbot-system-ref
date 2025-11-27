"""
HRMS API Client
Async HTTP client for communicating with HRMS Mock API
"""
import logging
from contextlib import AbstractContextManager, AbstractAsyncContextManager
from contextvars import ContextVar
from typing import Optional, List, Dict, Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

# Context variable for token (supports both sync and async contexts)
_auth_token_context: ContextVar[str] = ContextVar('auth_token', default='')


class AuthToken(AbstractContextManager, AbstractAsyncContextManager):
    """
    Context manager for token management (supports both sync and async)

    Usage:
        # Synchronous context
        with AuthToken("your_token"):
            client = HRMSClient()
            # token is available
        # token is automatically cleared

        # Asynchronous context
        async with AuthToken("your_token"):
            client = HRMSClient()
            # token is available
        # token is automatically cleared
    """
    
    def __init__(self, token: str):
        """
        Initialize token context manager

        Args:
            token: Authentication token to set
        """
        self.token = token
        self.previous_token = ''

    def __enter__(self):
        """Sync context manager entry"""
        self.previous_token = _auth_token_context.get()
        _auth_token_context.set(self.token)
        return self

    def __exit__(self, *_):
        """Sync context manager exit - restore previous token"""
        _auth_token_context.set(self.previous_token)
        return False

    async def __aenter__(self):
        """Async context manager entry"""
        self.previous_token = _auth_token_context.get()
        _auth_token_context.set(self.token)
        return self

    async def __aexit__(self, *_):
        """Async context manager exit - restore previous token"""
        _auth_token_context.set(self.previous_token)
        return False


class HRMSClient:
    """
    Async HTTP client for HRMS Mock API

    Handles all communication with the HRMS system including:
    - Leave management
    - Attendance tracking (when available)
    - Payroll queries (when available)

    Usage:
        client = HRMSClient()
        balance = await client.get_leave_balance()
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize HRMS client

        Args:
            base_url: HRMS API base URL (defaults to settings)
            token: Optional authentication token (can also be set via set_token method)
        """
        self.base_url = base_url or settings.hrms_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self._instance_token = token

        # If token provided, set it in context
        if token:
            _auth_token_context.set(token)

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
        """Close the HTTP client"""
        try:
            await self.client.aclose()
        except RuntimeError as e:
            # Handle "Event loop is closed" error gracefully
            # This can happen when the client was used in a thread pool
            if "Event loop is closed" in str(e):
                logger.debug("Event loop already closed, skipping client cleanup")
            else:
                raise

    # ==================== Leave Management ====================

    async def get_leave_balance(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get leave balance for the authenticated user (single leave type)

        Args:
            year: Year to get balance for (defaults to current year)

        Returns:
            Single leave balance data

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
            res = response.json()
            return res
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting leave balance: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting leave balance: {str(e)}")
            logger.exception(f"Error getting leave balance: {str(e)}")
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
            logger.error("HTTP error applying for leave: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error applying for leave: %s", str(e))
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
            logger.error("HTTP error getting leave requests: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting leave requests: %s", str(e))
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
            logger.error("HTTP error getting leave request: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting leave request: %s", str(e))
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
            logger.error("HTTP error cancelling leave request: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error cancelling leave request: %s", str(e))
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
            logger.error("HTTP error getting attendance records: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting attendance records: %s", str(e))
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
            logger.error("HTTP error getting attendance summary: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting attendance summary: %s", str(e))
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
            logger.error("HTTP error checking in: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error checking in: %s", str(e))
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
            logger.error("HTTP error checking out: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error checking out: %s", str(e))
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
            logger.error("HTTP error getting current payslip: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting current payslip: %s", str(e))
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
            logger.error("HTTP error getting payslip: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting payslip: %s", str(e))
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
            logger.error("HTTP error getting YTD summary: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting YTD summary: %s", str(e))
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
            logger.error("HTTP error getting tax summary: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Error getting tax summary: %s", str(e))
            raise

    # ==================== Context Manager Support ====================

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


hrms_client = HRMSClient()

__all__ = ["HRMSClient", "hrms_client", "AuthToken"]