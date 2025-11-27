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
    Specialized agent for attendance management

    This agent handles:
    - Checking attendance records
    - Viewing attendance history
    - Understanding attendance policies
    - Answering attendance-related questions

    Uses LangChain's ReAct pattern for tool use
    """
    agent_name = "AttendanceAgent"
    tools = [
        view_attendance_history,
        get_monthly_summary,
        search_attendance_policy
    ]
    
    template = """
        You are a helpful HR assistant specialized in attendance management.

        {current_date_time}

        You have access to the following tools to help employees with their attendance queries:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Important guidelines:
        - Always be polite and professional
        - When dates are mentioned like "today", "yesterday", "last week", convert them to YYYY-MM-DD format based on the current date
        - When months are mentioned like "this month", "last month", use the appropriate month/year values
        - For policy questions, use the search_attendance_policy tool
        - Inform users that attendance tracking features are being enhanced
        - Suggest checking the HRMS portal for detailed records
        - Provide helpful information about attendance policies

        Begin!

        Question: {input}
        Thought: {agent_scratchpad}
    """
