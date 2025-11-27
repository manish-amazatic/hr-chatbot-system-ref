"""
Attendance management tools for HRMS integration.
"""
import logging

from typing import Optional

from langchain_classic.tools import tool

from core.tools.hr_rag_tool import search_hr_policies

logger = logging.getLogger(__name__)



@tool
async def view_attendance_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    View attendance records for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (optional, defaults to last 30 days)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)

    Returns:
        List of attendance records with check-in/check-out times
    """
    try:
        records = await self.hrms_client.get_attendance_records(
            start_date=start_date,
            end_date=end_date
        )

        if not records:
            return "No attendance records found for the specified period."

        result = "Attendance Records:\n\n"
        for record in records:
            result += f"• Date: {record.get('date')}\n"
            result += f"  Status: {record.get('status')}\n"
            if record.get('check_in_time'):
                result += f"  Check-in: {record['check_in_time']}\n"
            if record.get('check_out_time'):
                result += f"  Check-out: {record['check_out_time']}\n"
            if record.get('work_hours'):
                result += f"  Work hours: {record['work_hours']} hours\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error viewing attendance history: {str(e)}")
        return f"Error viewing attendance history: {str(e)}"


@tool
async def get_monthly_summary(month: Optional[str] = None, year: Optional[str] = None) -> str:
    """
    Get monthly attendance summary.

    Args:
        month: Month number (1-12, defaults to current month)
        year: Year (defaults to current year)

    Returns:
        Summary of attendance for the month
    """
    try:
        month_int = int(month) if month else None
        year_int = int(year) if year else None

        summary = await self.hrms_client.get_attendance_summary(
            month=month_int,
            year=year_int
        )

        result = f"Attendance Summary for {summary.get('month')}/{summary.get('year')}:\n\n"
        result += f"• Total Working Days: {summary.get('total_working_days', 0)}\n"
        result += f"• Present Days: {summary.get('present_days', 0)}\n"
        result += f"• Absent Days: {summary.get('absent_days', 0)}\n"
        result += f"• Leave Days: {summary.get('leave_days', 0)}\n"
        result += f"• Half Days: {summary.get('half_days', 0)}\n"
        result += f"• Total Work Hours: {summary.get('total_work_hours', 0)} hours\n"
        result += f"• Attendance Percentage: {summary.get('attendance_percentage', 0):.1f}%\n"

        return result
    except Exception as e:
        logger.error(f"Error getting monthly summary: {str(e)}")
        return f"Error getting monthly summary: {str(e)}"


@tool
async def search_attendance_policy(query: str) -> str:
    """
    Search for attendance-related policies and guidelines.

    Args:
        query: Question about attendance policies

    Returns:
        Answer based on company attendance policies
    """
    try:
        # Use RAG tool to search policies
        return await search_hr_policies.invoke({"query": query})
    except Exception as e:
        logger.error(f"Error searching attendance policy: {str(e)}")
        return f"Error searching attendance policy: {str(e)}"
