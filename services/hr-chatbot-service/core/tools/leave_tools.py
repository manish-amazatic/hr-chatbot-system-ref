"""
Leave Agent
Specialized LangChain agent for leave management tasks
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


from langchain.tools import tool
# from langchain_classic.tools import tool
# from langchain_core.tools import tool

from core.services.hrms_api import hrms_client


logger = logging.getLogger(__name__)


class CheckLeaveBalanceInput(BaseModel):
    """Input for checking leave balance."""
    year: Optional[int] = Field(default=None, description="Year to check leave balance for")


@tool
async def check_leave_balance(year: Optional[int] = None) -> str:
    """
    Check the employee's leave balance.

    Args:
        year: Optional year to check balance for (defaults to current year)

    Returns:
        A formatted string showing leave balance by type
    """
    try:
        logger.info("Checking leave balance for year*********************: %s", year if year else 'current year')

        year_int = int(year) if year else None
        balance_data = await hrms_client.get_leave_balance(year=year_int)

        # Format the response
        balances = balance_data.get("balances", [])
        if not balances:
            return "No leave balance information available."

        result = f"Leave Balance for {balance_data['year']}:\n\n"
        for balance in balances:
            result += f"• {balance['leave_type']}: {balance['available_days']} days available "
            result += f"(Used: {balance['used_days']}, Total: {balance['total_days']})\n"

        return result
    except Exception as e:
        logger.error("Error checking leave balance: %s", str(e), exc_info=True)
        return f"Error checking leave balance: {str(e)}"


@tool
async def apply_for_leave(
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str = "Personal"
) -> str:
    """
    Apply for leave.

    Args:
        leave_type: Type of leave (Annual, Sick, Casual, Maternity, Paternity)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        reason: Reason for leave (Default : Personal)

    Returns:
        Confirmation message with request details
    """
    try:
        result = await hrms_client.apply_leave(
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

        return (
            f"Leave request submitted successfully!\n\n"
            f"Request ID: {result['id']}\n"
            f"Type: {result['leave_type']}\n"
            f"Duration: {result['start_date']} to {result['end_date']}\n"
            f"Days: {result['days_count']}\n"
            f"Status: {result['status']}\n"
            f"\nYour request is pending approval."
        )
    except Exception as e:
        logger.error("Error applying for leave: %s", str(e), exc_info=True)
        error_msg = str(e)
        if "insufficient balance" in error_msg.lower():
            return f"Cannot apply for leave: {error_msg}. Please check your leave balance first."
        return f"Error applying for leave: {error_msg}"


@tool
async def view_leave_history(status: Optional[str] = None) -> str:
    """
    View leave request history.

    Args:
        status: Optional filter by status (Pending, Approved, Rejected, Cancelled).
                If not provided, shows all requests.

    Returns:
        List of leave requests with details
    """
    try:
        requests = await hrms_client.get_leave_requests(status=status)

        if not requests:
            status_msg = f" with status '{status}'" if status else ""
            return f"No leave requests found{status_msg}."

        result = f"Leave Request History{' - ' + status if status else ''}:\n\n"
        for req in requests:
            result += f"• ID: {req['id']}\n"
            result += f"  Type: {req['leave_type']}\n"
            result += f"  Duration: {req['start_date']} to {req['end_date']} ({req['days_count']} days)\n"
            result += f"  Status: {req['status']}\n"
            if req.get('reason'):
                result += f"  Reason: {req['reason']}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error("Error viewing leave history: %s", str(e), exc_info=True)
        return f"Error viewing leave history: {str(e)}"


@tool
async def cancel_leave_request(request_id: str) -> str:
    """
    Cancel a pending or approved leave request.

    Args:
        request_id: The ID of the leave request to cancel

    Returns:
        Confirmation message
    """
    try:
        result = await hrms_client.cancel_leave_request(request_id)

        return (
            f"Leave request cancelled successfully!\n\n"
            f"Request ID: {result['id']}\n"
            f"Type: {result['leave_type']}\n"
            f"Duration: {result['start_date']} to {result['end_date']}\n"
            f"Status: {result['status']}"
        )
    except Exception as e:
        logger.error("Error cancelling leave request: %s", str(e), exc_info=True)
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return f"Leave request '{request_id}' not found."
        if "cannot be cancelled" in error_msg.lower():
            return "This leave request cannot be cancelled (it may already be rejected or cancelled)."
        return f"Error cancelling leave request: {error_msg}"
