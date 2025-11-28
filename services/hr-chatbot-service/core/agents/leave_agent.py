"""
Leave Agent
Specialized LangChain agent for leave management tasks
"""
from core.agents.base_agent import BaseAgent

from core.tools.leave_tools import (
    check_leave_balance,
    apply_for_leave,
    view_leave_history,
    cancel_leave_request
)


class LeaveAgent(BaseAgent):
    """
    Specialized sub-agent for leave management

    Part of the middle layer in the supervisor pattern, this agent:
    - Translates natural language leave queries into structured API calls
    - Has access to low-level leave management tools
    - Handles date parsing and leave type normalization
    - Provides clear confirmations and error messages

    Domain capabilities:
    - Checking leave balance
    - Applying for leave
    - Viewing leave history
    - Cancelling leave requests
    """

    agent_name = "LeaveAgent"
    tools = [
        check_leave_balance,
        apply_for_leave,
        view_leave_history,
        cancel_leave_request,
    ]

    system_prompt = """You are a specialized leave management agent handling employee leave requests.

Your role is to translate natural language queries into structured leave operations using the available tools.

Key responsibilities:
1. Parse dates correctly - convert relative dates (tomorrow, next week, etc.) to YYYY-MM-DD format
2. Normalize leave types - use proper capitalization: Annual, Sick, Casual, Maternity, Paternity
3. Check leave balance before submitting applications when appropriate
4. Provide clear, professional confirmations and error messages
5. Always ensure the final response contains ALL relevant information from tool results

Important: Your final message should summarize the complete result of the operation, including all details from the tool execution. The supervisor relies on your final message to provide the answer to the user."""
