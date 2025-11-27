"""
Leave Agent
Specialized LangChain agent for leave management tasks
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import asyncio

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.tools import tool
from langchain_classic.prompts import PromptTemplate

from core.processors.llm_processor import LLMProcessor
from core.tools.hrms_api_client import HRMSClient

logger = logging.getLogger(__name__)


def run_async_in_sync(coro):
    """
    Helper to run async coroutines from sync context within an async event loop.

    Args:
        coro: Coroutine to run

    Returns:
        Result of the coroutine
    """
    try:
        # Try to get the running loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, use asyncio.run()
        return asyncio.run(coro)

    # There's a running loop, we need to run in a thread pool
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()


class LeaveAgent:
    """
    Specialized agent for leave management

    This agent handles:
    - Checking leave balance
    - Applying for leave
    - Viewing leave history
    - Cancelling leave requests

    Uses LangChain's ReAct pattern for tool use
    """

    def __init__(self, hrms_client: HRMSClient):
        """
        Initialize Leave Agent

        Args:
            hrms_client: HRMS API client instance
        """
        self.hrms_client = hrms_client
        self.llm = LLMProcessor().get_llm()
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self):
        """Create LangChain tools for leave operations"""

        @tool
        def check_leave_balance(year: Optional[str] = None) -> str:
            """
            Check the employee's leave balance.

            Args:
                year: Optional year to check balance for (defaults to current year)

            Returns:
                A formatted string showing leave balance by type
            """
            try:
                year_int = int(year) if year else None
                balance_data = run_async_in_sync(self.hrms_client.get_leave_balance(year=year_int))

                # Format the response
                balances = balance_data.get("balances", [])
                if not balances:
                    return "No leave balance information available."

                result = f"Leave Balance for {balance_data['year']}:\n\n"
                for balance in balances:
                    result += f"• {balance['leave_type']}: {balance['available_days']} days available "
                    result += f"(Used: {balance['used_days']}, Total: {balance['total_days']})\n"

                return result
            except Exception as e:
                logger.error(f"Error checking leave balance: {str(e)}")
                return f"Error checking leave balance: {str(e)}"

        @tool
        def apply_for_leave(
            leave_type: str,
            start_date: str,
            end_date: str,
            reason: str = "Personal"
        ) -> str:
            """
            Apply for leave.

            Args:
                leave_type: Type of leave (Annual, Sick, Casual, Maternity, Paternity)
                start_date: Start date in YYYY-MM-DD format
                end_date: End date in YYYY-MM-DD format
                reason: Reason for leave

            Returns:
                Confirmation message with request details
            """
            try:
                result = run_async_in_sync(self.hrms_client.apply_leave(
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason
                ))

                return (
                    f"Leave request submitted successfully!\n\n"
                    f"Request ID: {result['id']}\n"
                    f"Type: {result['leave_type']}\n"
                    f"Duration: {result['start_date']} to {result['end_date']}\n"
                    f"Days: {result['days_count']}\n"
                    f"Status: {result['status']}\n"
                    f"\nYour request is pending approval."
                )
            except Exception as e:
                logger.error(f"Error applying for leave: {str(e)}")
                error_msg = str(e)
                if "insufficient balance" in error_msg.lower():
                    return f"Cannot apply for leave: {error_msg}. Please check your leave balance first."
                return f"Error applying for leave: {error_msg}"

        @tool
        def view_leave_history(status: Optional[str] = None) -> str:
            """
            View leave request history.

            Args:
                status: Optional filter by status (Pending, Approved, Rejected, Cancelled).
                        If not provided, shows all requests.

            Returns:
                List of leave requests with details
            """
            try:
                requests = run_async_in_sync(self.hrms_client.get_leave_requests(status=status))

                if not requests:
                    status_msg = f" with status '{status}'" if status else ""
                    return f"No leave requests found{status_msg}."

                result = f"Leave Request History{' - ' + status if status else ''}:\n\n"
                for req in requests:
                    result += f"• ID: {req['id']}\n"
                    result += f"  Type: {req['leave_type']}\n"
                    result += f"  Duration: {req['start_date']} to {req['end_date']} ({req['days_count']} days)\n"
                    result += f"  Status: {req['status']}\n"
                    if req.get('reason'):
                        result += f"  Reason: {req['reason']}\n"
                    result += "\n"

                return result
            except Exception as e:
                logger.error(f"Error viewing leave history: {str(e)}")
                return f"Error viewing leave history: {str(e)}"

        @tool
        def cancel_leave_request(request_id: str) -> str:
            """
            Cancel a pending or approved leave request.

            Args:
                request_id: The ID of the leave request to cancel

            Returns:
                Confirmation message
            """
            try:
                result = run_async_in_sync(self.hrms_client.cancel_leave_request(request_id))

                return (
                    f"Leave request cancelled successfully!\n\n"
                    f"Request ID: {result['id']}\n"
                    f"Type: {result['leave_type']}\n"
                    f"Duration: {result['start_date']} to {result['end_date']}\n"
                    f"Status: {result['status']}"
                )
            except Exception as e:
                logger.error(f"Error cancelling leave request: {str(e)}")
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    return f"Leave request '{request_id}' not found."
                if "cannot be cancelled" in error_msg.lower():
                    return f"This leave request cannot be cancelled (it may already be rejected or cancelled)."
                return f"Error cancelling leave request: {error_msg}"

        return [
            check_leave_balance,
            apply_for_leave,
            view_leave_history,
            cancel_leave_request
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools"""

        # Define the prompt template for the agent
        template = """You are a helpful HR assistant specialized in leave management.

You have access to the following tools to help employees with their leave requests:

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
- When dates are mentioned like "tomorrow", "next week", convert them to YYYY-MM-DD format
- For leave type, use proper capitalization: Annual, Sick, Casual, Maternity, Paternity
- Check leave balance before applying for leave
- Provide clear confirmation messages

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        # Create the ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=False
        )

        return agent_executor

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a leave-related query

        Args:
            query: User query about leave
            context: Optional context (user_id, history, etc.)

        Returns:
            Agent's response
        """
        try:
            logger.info(f"LeaveAgent processing query: {query[:100]}...")

            # Invoke the agent
            result = self.agent.invoke({"input": query})

            # Extract the output
            output = result.get("output", "I apologize, but I couldn't process your request.")

            logger.info(f"LeaveAgent response generated successfully")
            return output

        except Exception as e:
            logger.error(f"Error in LeaveAgent: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
