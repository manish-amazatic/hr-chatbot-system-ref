"""
Payroll Agent
Specialized LangChain agent for payroll and compensation queries
"""
from core.agents.base_agent import BaseAgent

from core.tools.payroll_tools import (
    get_latest_payslip,
    get_ytd_summary,
    search_payroll_policy,
    explain_payslip_component
)


class PayrollAgent(BaseAgent):
    """
    Specialized agent for payroll and compensation

    This agent handles:
    - Payslip queries
    - Salary information
    - Deductions and allowances
    - Tax information
    - Compensation policies

    Uses LangChain's ReAct pattern for tool use
    """
    agent_name = "PayrollAgent"
    tools = [
        get_latest_payslip,
        get_ytd_summary,
        search_payroll_policy,
        explain_payslip_component
    ]
    template = """
        You are a helpful HR assistant specialized in payroll and compensation queries.

        {current_date_time}

        You have access to the following tools to help employees with their payroll questions:

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
        - Never disclose salary information of other employees
        - When users ask about "this month", "last month", or specific months/years, use the appropriate values
        - For policy questions, use the search_payroll_policy tool
        - For payslip component questions, use explain_payslip_component
        - Inform users that payslip access features are being enhanced
        - Suggest checking the HRMS portal or contacting payroll team for specific queries
        - Be sensitive about compensation-related topics

        Begin!

        Question: {input}
        Thought: {agent_scratchpad}
    """
