"""
Base Agent
Specialized LangChain agent for leave management tasks
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.prompts import PromptTemplate
from langchain_core.tools.base import BaseTool

from core.llm_processor import LLMProcessor
from core.config import settings

logger = logging.getLogger(__name__)


class BaseTimeAgent():

    def get_current_date_time(self) -> str:
        """Get current date and time string"""
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

    # Define the prompt template for the agent
    # Note: current_date_time will be injected at execution time
    agent_name = "BaseAgent"
    tools: list[BaseTool] = []
    template = """
        Begin!

        Question: {input}
        Thought: {agent_scratchpad}
    """

    def __init__(self):
        """
        Initialize Leave Agent

        Args:
            hrms_client: HRMS API client instance
        """
        self.llm = LLMProcessor().get_llm()
        self.agent = self._create_agent()

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools"""
        prompt = PromptTemplate.from_template(self.template)

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
            logger.info("context***********************************: %s", context)
            logger.info("%s processing query: %s...", self.agent_name, query[:100])

            # Invoke the agent with current date/time context
            result = await self.agent.ainvoke(
                {
                    "input": query,
                    "current_date_time": self.get_current_date_time()
                },
                include_run_info=settings.debug
            )

            # Extract the output
            output = result.get("output", "I apologize, but I couldn't process your request.")

            logger.info("%s response generated successfully")
            return output

        except Exception as e:
            logger.error(f"Error i %s  {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
