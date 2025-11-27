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
    Specialized agent for leave management

    This agent handles:
    - Checking leave balance
    - Applying for leave
    - Viewing leave history
    - Cancelling leave requests

    Uses LangChain's ReAct pattern for tool use
    """

    agent_name = "LeaveAgent"
    tools = [
        check_leave_balance,
        apply_for_leave,
        view_leave_history,
        cancel_leave_request,
    ]
    template = """
        You are a helpful HR assistant specialized in leave management.

        {current_date_time}

        You have access to the following tools to help employees with their leave requests:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action (parameters)
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Important guidelines:
        - Always be polite and professional
        - When dates are mentioned like "tomorrow", "next week", convert them to YYYY-MM-DD format based on the current date
        - For leave type, use proper capitalization: Annual, Sick, Casual, Maternity, Paternity
        - Check leave balance before applying for leave
        - Provide clear confirmation messages

        Begin!

        Question: {input}
        Thought: {agent_scratchpad}
    """
