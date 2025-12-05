import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from core.agents.leave_agent import LeaveAgent
from core.agents.attendance_agent import AttendanceAgent
from core.agents.payroll_agent import PayrollAgent
from core.tools.hr_rag_tool import search_hr_policies


logger = logging.getLogger(__name__)


leave_agent = LeaveAgent()
attendance_agent = AttendanceAgent()
payroll_agent = PayrollAgent()


# Tool input schemas
class AgentInput(BaseModel):
    """Input schema for agent tools"""
    query: str = Field(description="The user's query to process")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context including user_id, session_id, etc."
    )


class PolicyInput(BaseModel):
    """Input schema for policy search tool"""
    query: str = Field(description="The policy question to search for")


@tool("leave_agent", args_schema=AgentInput)
async def handle_leave_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Handle employee leave-related queries.

    Use this tool for:
    - Checking leave balance (vacation days, sick days, PTO)
    - Applying for leave/time off
    - Viewing leave history and past applications
    - Cancelling leave requests

    Examples: "What's my leave balance?", "Apply for 3 days leave", "Show my leave history"
    """
    try:
        logger.info("Routing to LeaveAgent: %s", query[:50])
        response = await leave_agent.process(query, context)
        return response
    except Exception as e:
        logger.error("Error in LeaveAgent: %s", str(e), exc_info=True)
        return f"I encountered an error processing your leave request: {str(e)}"



@tool("attendance_agent", args_schema=AgentInput)
async def handle_attendance_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Handle employee attendance-related queries.

    Use this tool for:
    - Viewing attendance history and records
    - Getting monthly attendance summaries
    - Checking check-in/check-out times
    - Overtime and working hours information

    Examples: "Show my attendance for November", "What time did I check in today?"
    """
    try:
        logger.info("Routing to AttendanceAgent: %s", query[:50])
        response = await attendance_agent.process(query, context)
        return response
    except Exception as e:
        logger.error("Error in AttendanceAgent: %s", str(e), exc_info=True)
        return f"I encountered an error processing your attendance request: {str(e)}"


@tool("payroll_agent", args_schema=AgentInput)
async def handle_payroll_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Handle employee payroll and compensation queries.

    Use this tool for:
    - Viewing payslips and salary statements
    - Checking salary, deductions, and allowances
    - Year-to-date (YTD) earnings summaries
    - Tax information and pay components

    Examples: "Show my latest payslip", "What's my YTD salary?", "Explain my deductions"
    """
    try:
        logger.info("Routing to PayrollAgent: %s", query[:50])
        response = await payroll_agent.process(query, context)
        return response
    except Exception as e:
        logger.error("Error in PayrollAgent: %s", str(e), exc_info=True)
        return f"I encountered an error processing your payroll request: {str(e)}"


@tool("hr_policy_search", args_schema=PolicyInput)
def search_hr_policy(query: str) -> str:
    """Search company HR policies and procedures using RAG.

    Use this tool for informational questions about:
    - Company policies, rules, and procedures
    - Employee handbook and guidelines
    - HR processes and compliance
    - Benefits, holidays, and general HR information

    Examples: "What is the annual leave policy?", "Tell me about remote work policy"
    """
    try:
        logger.info("Routing to PolicySearch: %s", query[:50])
        response = search_hr_policies.invoke({"query": query})

        # Check if Milvus was unavailable
        if "currently unavailable" in response.lower():
            return ("The policy search system is temporarily unavailable. "
                    "Please contact HR at hr@company.com for policy questions.")

        return response
    except Exception as e:
        logger.error("Error in policy search: %s", str(e), exc_info=True)
        return (f"I encountered an error searching HR policies: {str(e)}. "
                "Please contact HR at hr@company.com for assistance.")


__all__ = [
    "handle_leave_query",
    "handle_attendance_query",
    "handle_payroll_query",
    "search_hr_policy",
]
