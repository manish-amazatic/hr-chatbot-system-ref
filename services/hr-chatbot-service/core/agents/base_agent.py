"""
Base Agent
Specialized LangChain agent following the supervisor sub-agent pattern
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain.agents.middleware import wrap_tool_call
from langchain_core.tools.base import BaseTool

from core.llm_processor import LLMProcessor
from core.config import settings

logger = logging.getLogger(__name__)


class BaseTimeAgent():
    """Base class providing current date/time functionality"""

    def get_current_date_time(self) -> str:
        """Get current date and time string for agent context"""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day = now.strftime("%A")
        current_time = now.strftime("%H:%M")
        current_month = now.strftime("%B")
        current_year = now.year
        return (
            f"Current date and time: {current_date} ({current_day}) at {current_time}. "
            f"Current month: {current_month} {current_year} [isoformat: {now.isoformat()}]"
        )


class BaseAgent(BaseTimeAgent):
    """
    Base Agent following LangChain supervisor sub-agent pattern

    This serves as the middle layer in the supervisor architecture:
    - Bottom layer: Low-level API tools (HRMS API calls)
    - Middle layer: Sub-agents that translate natural language to API calls (THIS LAYER)
    - Top layer: Supervisor that routes to appropriate sub-agents

    Each sub-agent specializes in a domain (leave, attendance, payroll) and has:
    - Domain-specific tools
    - Specialized system prompt
    - Error handling middleware
    """

    agent_name = "BaseAgent"
    tools: list[BaseTool] = []
    system_prompt = "You are a helpful HR assistant."

    def __init__(self):
        """
        Initialize sub-agent with domain-specific tools and prompts
        """
        self.llm = LLMProcessor().get_llm()
        self.agent = self._create_agent()

    def _create_agent(self):
        """
        Create the LangChain agent with tools and middleware

        Following the supervisor pattern, this creates a sub-agent that:
        1. Has access to domain-specific low-level tools
        2. Uses a specialized prompt for its domain
        3. Handles errors gracefully
        """

        @wrap_tool_call
        async def handle_tool_errors(request, handler):
            """Handle tool execution errors with custom messages."""
            try:
                logger.debug("Tool request: %s", request)
                return await handler(request)
            except Exception as e:
                logger.error(f"Tool error in {self.agent_name}: {str(e)}", exc_info=True)
                # Return a custom error message to the model
                return ToolMessage(
                    content=f"Tool error: {str(e)}. Please verify the input and try again.",
                    tool_call_id=request.tool_call["id"]
                )

        # Create agent with domain-specific configuration
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            middleware=[handle_tool_errors],
            debug=settings.debug,
        )

        return agent

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a domain-specific query with current date/time context

        This is called by the supervisor when routing to this sub-agent.
        The sub-agent translates natural language to structured API calls.

        Args:
            query: User query in natural language
            context: Optional context (user_id, session_id, etc.)

        Returns:
            Agent's response containing results from tool execution
        """
        try:
            logger.info("%s processing query: %s...", self.agent_name, query[:100])

            # Inject current date/time context into the query for datetime awareness
            datetime_aware_query = f"{self.get_current_date_time()}\n\nUser query: {query}"

            # Invoke the agent with the datetime-aware query
            result = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": datetime_aware_query}]},
                context=context
            )

            logger.debug("%s raw response: %s", self.agent_name, result)

            # Extract the final message content
            if "messages" in result and len(result["messages"]) > 0:
                # Get the last message which contains the final response
                final_message = result["messages"][-1]
                output = final_message.content if hasattr(final_message, 'content') else str(final_message)
            else:
                output = result.get("output", "I apologize, but I couldn't process your request.")

            logger.info("%s response generated successfully", self.agent_name)
            return output

        except Exception as e:
            logger.error(f"Error in {self.agent_name}: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
