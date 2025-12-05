"""
Orchestrator Agent - LangChain Supervisor Pattern
Supervisor agent that routes queries to specialized sub-agents following the supervisor pattern
"""
import logging
from typing import Dict, Any, Optional
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from core.agents.base_agent import BaseTimeAgent
from core.llm_processor import LLMProcessor
from core.config import settings
from .agent_tools import (
    handle_leave_query,
    handle_attendance_query,
    handle_payroll_query,
    search_hr_policy
)


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

    system_prompt = """
        You are an HR assistant supervisor that intelligently routes employee queries to specialized sub-agents.

        Your role is to:
        1. Analyze the user's query to understand their intent
        2. Select the most appropriate sub-agent tool to handle the query
        3. Call tools as many times as needed to gather all required information
        4. Continue looping and calling tools until you have the complete answer
        5. Only provide the final response once you have all necessary information

        Available sub-agents:
        - handle_leave_query: Leave management (balance, applications, history, cancellations)
        - handle_attendance_query: Attendance tracking (records, check-in/out, summaries)
        - handle_payroll_query: Payroll and compensation (payslips, salary, deductions, YTD)
        - search_hr_policy: HR policy search (company rules, procedures, guidelines)

        Important Instructions:
        - ALWAYS use tools to answer queries - never answer from memory alone
        - Call tools MULTIPLE TIMES if needed to get complete information
        - Continue calling tools until you have gathered all data required to answer the query
        - If a query requires information from multiple domains, call multiple tools
        - Each sub-agent returns a complete response with all relevant details
        - Your job is routing AND ensuring completeness - delegate to appropriate sub-agents
        - When in doubt between agents, choose based on the primary intent
        - Pass the user's query to the selected sub-agent as-is
        - When users mention relative dates (today, tomorrow, this week, last month), the sub-agents will handle the conversion
        - After receiving tool results, analyze if you need MORE information before responding
        - Loop through tool calls until you can provide a comprehensive final answer

        Tool Calling Pattern:
        1. Identify what information is needed
        2. Call the appropriate tool(s)
        3. Analyze the results
        4. If more information is needed, call additional tools
        5. Repeat steps 2-4 until you have everything needed
        6. Provide the complete final answer to the user

        Examples:
        - "What's my leave balance?" → handle_leave_query → return result
        - "Show attendance for November" → handle_attendance_query → return result
        - "What's my latest payslip?" → handle_payroll_query → return result
        - "What is the annual leave policy?" → search_hr_policy → return result
        - Complex query requiring multiple tools → call first tool → analyze → call second tool if needed → continue until complete
    """

    def __init__(self, hrms_token: Optional[str] = None):
        """
        Initialize Supervisor with specialized sub-agents

        Args:
            hrms_token: JWT token for HRMS API authentication
        """
        self.llm = LLMProcessor().get_llm()

        self.tools = (
            handle_leave_query,
            handle_attendance_query,
            handle_payroll_query,
            search_hr_policy
        )

        # Create the supervisor agent
        self.supervisor_agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            debug=settings.debug,
        )

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
            logger.info("Supervisor processing query: %s...", query[:50])

            # Inject current date/time context for datetime awareness
            datetime_context = self.get_current_date_time()
            datetime_aware_query = f"{datetime_context}\n\nUser query: {query}"

            # Invoke the supervisor agent with datetime-aware query
            result = await self.supervisor_agent.ainvoke(
                {"messages": [{"role": "user", "content": datetime_aware_query}]},
                context=context
            )

            logger.debug("Supervisor result: %s", result)

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
            logger.error("Error in Supervisor: %s", str(e), exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "agent_used": "error",
                "metadata": {"error": str(e)}
            }
