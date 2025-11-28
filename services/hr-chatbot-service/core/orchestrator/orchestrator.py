"""
Orchestrator Agent - LangChain Supervisor Pattern
Supervisor agent that routes queries to specialized sub-agents following the supervisor pattern
"""
import logging
from typing import Dict, Any, Optional
from langchain.agents import create_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from core.agents.base_agent import BaseTimeAgent
from core.agents.leave_agent import LeaveAgent
from core.agents.attendance_agent import AttendanceAgent
from core.agents.payroll_agent import PayrollAgent
from core.tools.hr_rag_tool import search_hr_policies
from core.llm_processor import LLMProcessor
from core.config import settings


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
    LangChain Supervisor Agent

    Top layer in the supervisor pattern architecture that routes queries to specialized sub-agents.

    Architecture layers:
    - Bottom layer: Low-level API tools (HRMS API calls, RAG search)
    - Middle layer: Specialized sub-agents (LeaveAgent, AttendanceAgent, PayrollAgent)
    - Top layer: Supervisor agent (THIS LAYER) - routes to appropriate sub-agents

    The supervisor:
    1. Analyzes incoming user queries
    2. Routes to the appropriate specialized sub-agent
    3. Returns the sub-agent's response to the user

    Benefits of this pattern:
    - Clear domain boundaries between agents
    - Each agent has specialized tools and prompts
    - Centralized workflow control
    - Easy to test layers independently
    """

    def __init__(self, hrms_token: Optional[str] = None):
        """
        Initialize Supervisor with specialized sub-agents

        Args:
            hrms_token: JWT token for HRMS API authentication
        """
        self.hrms_token = hrms_token
        self.llm = LLMProcessor().get_llm()

        # Initialize specialized sub-agents (middle layer)
        self.leave_agent = LeaveAgent()
        self.attendance_agent = AttendanceAgent()
        self.payroll_agent = PayrollAgent()

        # Create supervisor tools (wrapped sub-agents)
        self.tools = self._create_tools()

        # Create the supervisor agent
        self.supervisor_agent = self._create_supervisor_agent()

    def _create_tools(self):
        """
        Wrap specialized sub-agents as tools for the supervisor

        Following the supervisor pattern, each sub-agent is wrapped as a tool that:
        1. Accepts natural language queries
        2. Returns complete results (not just confirmations)
        3. Has clear descriptions for routing decisions

        This abstraction hides the complexity of low-level tools from the supervisor.
        """

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
                logger.info(f"Routing to LeaveAgent: {query[:50]}...")
                response = await self.leave_agent.process(query, context)
                return response
            except Exception as e:
                logger.error(f"Error in LeaveAgent: {str(e)}", exc_info=True)
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
                logger.info(f"Routing to AttendanceAgent: {query[:50]}...")
                response = await self.attendance_agent.process(query, context)
                return response
            except Exception as e:
                logger.error(f"Error in AttendanceAgent: {str(e)}", exc_info=True)
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
                logger.info(f"Routing to PayrollAgent: {query[:50]}...")
                response = await self.payroll_agent.process(query, context)
                return response
            except Exception as e:
                logger.error(f"Error in PayrollAgent: {str(e)}", exc_info=True)
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
                logger.info(f"Routing to PolicySearch: {query[:50]}...")
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

    def _create_supervisor_agent(self):
        """
        Create the supervisor agent using create_agent()

        The supervisor uses the LangChain agent pattern with wrapped sub-agents as tools.
        This provides intelligent routing based on query analysis.
        """

        # Store base system prompt (will be enhanced with current date/time at runtime)
        self.base_system_prompt = """You are an HR assistant supervisor that intelligently routes employee queries to specialized sub-agents.

Your role is to:
1. Analyze the user's query to understand their intent
2. Select the most appropriate sub-agent tool to handle the query
3. Ensure the sub-agent's complete response is returned to the user

Available sub-agents:
- handle_leave_query: Leave management (balance, applications, history, cancellations)
- handle_attendance_query: Attendance tracking (records, check-in/out, summaries)
- handle_payroll_query: Payroll and compensation (payslips, salary, deductions, YTD)
- search_hr_policy: HR policy search (company rules, procedures, guidelines)

Important:
- Each sub-agent returns a complete response with all relevant details
- Your job is routing, not answering - always delegate to the appropriate sub-agent
- When in doubt between agents, choose based on the primary intent
- Pass the user's query to the selected sub-agent as-is
- When users mention relative dates (today, tomorrow, this week, last month), the sub-agents will handle the conversion

Examples:
- "What's my leave balance?" → handle_leave_query
- "Show attendance for November" → handle_attendance_query
- "What's my latest payslip?" → handle_payroll_query
- "What is the annual leave policy?" → search_hr_policy"""

        # Create supervisor agent with sub-agent tools
        supervisor = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.base_system_prompt,
            debug=settings.debug,
        )

        return supervisor

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user query using the supervisor agent with datetime awareness

        Following the supervisor pattern, this method:
        1. Injects current date/time context for datetime awareness
        2. Invokes the supervisor agent with the datetime-aware query
        3. The supervisor analyzes the query and routes to the appropriate sub-agent
        4. The sub-agent executes its tools and returns a complete response
        5. Returns the response to the user

        Args:
            query: User query text
            context: Optional context (user_id, session_id, history, etc.)

        Returns:
            Dict containing:
                - response: Final response text from the sub-agent
                - agent_used: Which sub-agent was selected
                - metadata: Additional information about routing and execution
        """
        try:
            logger.info(f"Supervisor processing query: {query[:50]}...")

            # Inject current date/time context for datetime awareness
            datetime_context = self.get_current_date_time()
            datetime_aware_query = f"{datetime_context}\n\nUser query: {query}"

            # Invoke the supervisor agent with datetime-aware query
            result = await self.supervisor_agent.ainvoke(
                {"messages": [{"role": "user", "content": datetime_aware_query}]},
                context=context
            )

            logger.debug(f"Supervisor result: {result}")

            # Extract the final response
            if "messages" in result and len(result["messages"]) > 0:
                # Get the last message which contains the final response
                final_message = result["messages"][-1]
                response_text = final_message.content if hasattr(final_message, 'content') else str(final_message)

                # Determine which agent was used by checking tool calls in the message history
                agent_used = "direct_supervisor"
                tool_calls_info = []

                for msg in result["messages"]:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            agent_used = tool_call.get('name', 'unknown')
                            tool_calls_info.append({
                                'tool': tool_call.get('name'),
                                'args': tool_call.get('args', {})
                            })

                return {
                    "response": response_text,
                    "agent_used": agent_used,
                    "metadata": {
                        "routing_method": "supervisor_agent",
                        "tool_calls": tool_calls_info,
                        "datetime_context": datetime_context
                    }
                }
            else:
                # Fallback if structure is unexpected
                logger.warning("Unexpected result structure from supervisor")
                return {
                    "response": str(result),
                    "agent_used": "supervisor",
                    "metadata": {"routing_method": "supervisor_fallback"}
                }

        except Exception as e:
            logger.error(f"Error in Supervisor: {str(e)}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "agent_used": "error",
                "metadata": {"error": str(e)}
            }

    async def close(self):
        """Clean up resources"""
        pass


