"""
Attendance Agent
Specialized LangChain agent for attendance management tasks
"""
from core.agents.base_agent import BaseAgent
from core.tools.attendence_tools import (
    view_attendance_history,
    get_monthly_summary,
    search_attendance_policy,
)


class AttendanceAgent(BaseAgent):
    """
    Specialized sub-agent for attendance management

    Part of the middle layer in the supervisor pattern, this agent:
    - Translates natural language attendance queries into structured API calls
    - Has access to low-level attendance tracking tools
    - Handles date parsing for attendance records
    - Provides attendance summaries and policy information

    Domain capabilities:
    - Viewing attendance history and records
    - Getting monthly attendance summaries
    - Checking check-in/check-out times
    - Searching attendance policies
    """
    agent_name = "AttendanceAgent"
    tools = [
        view_attendance_history,
        get_monthly_summary,
        search_attendance_policy
    ]

    system_prompt = """
        You are a specialized attendance management agent handling employee attendance queries.

        Your role is to translate natural language queries into structured attendance operations using the available tools.

        Key responsibilities:
        1. Parse dates correctly - convert relative dates (today, yesterday, last week) to YYYY-MM-DD format
        2. Handle month references - convert "this month", "last month" to appropriate month/year values
        3. Use search_attendance_policy for policy questions
        4. Provide clear summaries of attendance data
        5. Always ensure the final response contains ALL relevant information from tool results

        Important: Your final message should summarize the complete result of the operation, including all details from the tool execution. The supervisor relies on your final message to provide the answer to the user.
    """
