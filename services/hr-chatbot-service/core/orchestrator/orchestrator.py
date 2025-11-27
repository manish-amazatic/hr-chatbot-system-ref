"""
Orchestrator Agent - LangChain Multi-Agent Tool Calling Pattern
Supervisor agent that routes queries to specialized agents using LLM-based tool calling
"""
import logging
from typing import Dict, Any, Optional, Annotated
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from core.agents.base_agent import BaseTimeAgent
from core.agents.leave_agent import LeaveAgent
from core.agents.attendance_agent import AttendanceAgent
from core.agents.payroll_agent import PayrollAgent
from core.tools.hr_rag_tool import search_hr_policies
from core.llm_processor import LLMProcessor


logger = logging.getLogger(__name__)


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


class Orchestrator(BaseTimeAgent):
    """
    LangChain Multi-Agent Orchestrator

    Uses LLM-based tool calling to route queries to specialized agents:
    - LeaveAgent: Handle leave balance, applications, history
    - AttendanceAgent: Handle attendance records and summaries
    - PayrollAgent: Handle payroll and compensation queries
    - PolicySearchTool: Search HR policies using RAG

    The LLM acts as a supervisor, intelligently selecting the right tool
    based on the user's query.
    """

    # System message template for supervisor
    # Note: current date/time will be injected at execution time
    system_message_template = """
        You are an HR assistant supervisor that routes employee queries to specialized tools.

        {current_date_time}

        Available tools:
        - handle_leave_query: For leave balance, applications, cancellations, and leave history
        - handle_attendance_query: For attendance records, check-in/out times, and monthly summaries
        - handle_payroll_query: For payslips, salary information, deductions, and YTD summaries
        - search_hr_policy: For questions about company policies, rules, procedures, and guidelines

        Instructions:
        1. Analyze the user's query to determine their intent
        2. Select the most appropriate tool to handle the query
        3. Call the tool with the query and any relevant context
        4. Return the tool's response to the user
        5. When users mention relative dates (today, tomorrow, next week, last month), understand them in the context of the current date and time

        Examples:
        - "What's my leave balance?" → handle_leave_query
        - "Show my attendance for November" → handle_attendance_query
        - "What's my latest payslip?" → handle_payroll_query
        - "What is the annual leave policy?" → search_hr_policy
    """

    def __init__(self, hrms_token: Optional[str] = None):
        """
        Initialize Orchestrator with LangChain tool calling

        Args:
            hrms_token: JWT token for HRMS API authentication
        """
        self.hrms_token = hrms_token
        self.llm = LLMProcessor().get_llm()

        # Initialize specialized agents
        self.leave_agent = LeaveAgent()
        self.attendance_agent = AttendanceAgent()
        self.payroll_agent = PayrollAgent()

        # Create tools
        self.tools = self._create_tools()

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _create_tools(self):
        """Create LangChain tools from specialized agents"""

        @tool("leave_agent", args_schema=AgentInput)
        async def handle_leave_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
            """
            Handle employee leave-related queries including:
            - Checking leave balance
            - Applying for leave
            - Viewing leave history
            - Cancelling leave requests

            Use this for any questions about vacations, time off, PTO, sick leave, etc.
            """
            try:
                logger.info(f"LeaveAgent processing: {query[:50]}...")
                response = await self.leave_agent.process(query, context)
                return response
            except Exception as e:
                logger.error(f"Error in LeaveAgent: {str(e)}", exc_info=True)
                return f"I encountered an error processing your leave request: {str(e)}"

        @tool("attendance_agent", args_schema=AgentInput)
        async def handle_attendance_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
            """
            Handle employee attendance-related queries including:
            - Viewing attendance history
            - Getting monthly attendance summaries
            - Checking check-in/out times
            - Overtime and working hours

            Use this for any questions about attendance, presence, timesheets, etc.
            """
            try:
                logger.info(f"AttendanceAgent processing: {query[:50]}...")
                response = await self.attendance_agent.process(query, context)
                return response
            except Exception as e:
                logger.error(f"Error in AttendanceAgent: {str(e)}", exc_info=True)
                return f"I encountered an error processing your attendance request: {str(e)}"

        @tool("payroll_agent", args_schema=AgentInput)
        async def handle_payroll_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
            """
            Handle employee payroll and compensation queries including:
            - Viewing payslips
            - Checking salary and deductions
            - Year-to-date (YTD) summaries
            - Tax information and allowances

            Use this for any questions about salary, pay, compensation, earnings, etc.
            """
            try:
                logger.info(f"PayrollAgent processing: {query[:50]}...")
                response = await self.payroll_agent.process(query, context)
                return response
            except Exception as e:
                logger.error(f"Error in PayrollAgent: {str(e)}", exc_info=True)
                return f"I encountered an error processing your payroll request: {str(e)}"

        @tool("hr_policy_rag_tool", args_schema=PolicyInput)
        def search_hr_policy(query: str) -> str:
            """
            Search company HR policies, procedures, and guidelines using RAG.

            Use this for informational questions about:
            - Company policies and rules
            - HR procedures and processes
            - Employee handbook information
            - Compliance and regulations
            - General HR knowledge questions

            This tool searches through the company's HR policy documents to provide
            accurate, policy-based answers.
            """
            try:
                logger.info(f"PolicySearch processing: {query[:50]}...")
                response = search_hr_policies.invoke({"query": query})

                # Check if Milvus was unavailable
                if "currently unavailable" in response.lower():
                    return ("The policy search system is temporarily unavailable. "
                           "Please contact HR at hr@company.com for policy questions.")

                return response
            except Exception as e:
                logger.error(f"Error in policy search: {str(e)}", exc_info=True)
                return (f"I encountered an error searching HR policies: {str(e)}. "
                       "Please contact HR at hr@company.com for assistance.")

        return [handle_leave_query, handle_attendance_query, handle_payroll_query, search_hr_policy]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user query using LLM-based tool calling

        The LLM analyzes the query and automatically selects the appropriate
        tool (agent) to handle it.

        Args:
            query: User query text
            context: Optional context (user_id, session_id, history, etc.)

        Returns:
            Dict containing:
                - response: Agent's response text
                - agent_used: Which tool/agent was called
                - tool_calls: Details about the tool invocation
                - metadata: Additional information
        """
        try:
            # Get current date and time for this execution
            # Create system message with current date/time
            system_message_content = self.system_message_template.format(
                current_date_time=self.get_current_date_time()
            )

            # Create messages for LLM
            messages = [
                SystemMessage(content=system_message_content),
                HumanMessage(content=query)
            ]

            # Invoke LLM with tools
            logger.info(f"Orchestrator processing query: {query[:50]}...")
            response = self.llm_with_tools.invoke(messages)

            # Check if LLM called a tool
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_call = response.tool_calls[0]
                tool_name = tool_call['name']
                tool_args = tool_call['args']

                logger.info(f"LLM selected tool: {tool_name}")

                # Find and execute the tool
                tool_map = {tool.name: tool for tool in self.tools}
                if tool_name in tool_map:
                    selected_tool = tool_map[tool_name]

                    # Add context to tool args if not present
                    if 'context' not in tool_args and context:
                        tool_args['context'] = context

                    # Execute the tool
                    if tool_name == "search_hr_policy":
                        # Sync tool
                        tool_response = selected_tool.invoke(tool_args)
                    else:
                        # Async tools
                        tool_response = await selected_tool.ainvoke(tool_args)

                    return {
                        "response": tool_response,
                        "agent_used": tool_name,
                        "tool_calls": response.tool_calls,
                        "metadata": {
                            "routing_method": "llm_tool_calling",
                            "tool_args": tool_args
                        }
                    }
                else:
                    logger.warning(f"Unknown tool selected: {tool_name}")
                    return {
                        "response": "I'm not sure how to handle that request. Please try rephrasing.",
                        "agent_used": "unknown",
                        "metadata": {"error": f"unknown_tool: {tool_name}"}
                    }
            else:
                # LLM didn't call a tool - return direct response
                logger.info("LLM provided direct response without tool call")
                response_text = response.content if hasattr(response, 'content') else str(response)

                return {
                    "response": response_text,
                    "agent_used": "direct_llm",
                    "metadata": {
                        "routing_method": "direct_response",
                        "no_tool_selected": True
                    }
                }

        except Exception as e:
            logger.error(f"Error in Orchestrator: {str(e)}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "agent_used": "error",
                "metadata": {"error": str(e)}
            }

    async def close(self):
        """Clean up resources"""
        pass


