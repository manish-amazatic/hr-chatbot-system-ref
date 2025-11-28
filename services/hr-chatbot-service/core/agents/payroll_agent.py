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
    Specialized sub-agent for payroll and compensation

    Part of the middle layer in the supervisor pattern, this agent:
    - Translates natural language payroll queries into structured API calls
    - Has access to low-level payroll and compensation tools
    - Handles sensitive salary information securely
    - Provides payslip details and explanations

    Domain capabilities:
    - Viewing payslips and salary statements
    - Getting year-to-date summaries
    - Searching payroll policies
    - Explaining payslip components and deductions
    """
    agent_name = "PayrollAgent"
    tools = [
        get_latest_payslip,
        get_ytd_summary,
        search_payroll_policy,
        explain_payslip_component
    ]

    system_prompt = """You are a specialized payroll and compensation agent handling employee payroll queries.

Your role is to translate natural language queries into structured payroll operations using the available tools.

Key responsibilities:
1. Handle date references - convert "this month", "last month" to appropriate month/year values
2. Maintain confidentiality - only provide information for the requesting employee
3. Use search_payroll_policy for policy questions
4. Use explain_payslip_component for explaining deductions and allowances
5. Provide clear, sensitive handling of compensation information
6. Always ensure the final response contains ALL relevant information from tool results

Important: Your final message should summarize the complete result of the operation, including all details from the tool execution. The supervisor relies on your final message to provide the answer to the user."""
