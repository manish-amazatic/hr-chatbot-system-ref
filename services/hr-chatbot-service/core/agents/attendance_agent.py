"""
Attendance Agent
Specialized LangChain agent for attendance management tasks
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate

from core.processors.llm_processor import LLMProcessor, LLMProvider
from core.tools.hrms_api_client import HRMSClient
from core.tools.hr_rag_tool import search_hr_policies

logger = logging.getLogger(__name__)


class AttendanceAgent:
    """
    Specialized agent for attendance management

    This agent handles:
    - Checking attendance records
    - Viewing attendance history
    - Understanding attendance policies
    - Answering attendance-related questions

    Uses LangChain's ReAct pattern for tool use
    """

    def __init__(self, hrms_client: HRMSClient):
        """
        Initialize Attendance Agent

        Args:
            hrms_client: HRMS API client instance
        """
        self.hrms_client = hrms_client
        self.llm = LLMProcessor().get_llm(LLMProvider.OPENAI)
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self):
        """Create LangChain tools for attendance operations"""

        @tool
        def view_attendance_history(
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
        ) -> str:
            """
            View attendance records for a date range.

            Args:
                start_date: Start date in YYYY-MM-DD format (optional, defaults to last 30 days)
                end_date: End date in YYYY-MM-DD format (optional, defaults to today)

            Returns:
                List of attendance records with check-in/check-out times
            """
            try:
                # Note: HRMS API attendance endpoints not yet implemented
                # This is a placeholder for when the API is ready
                return (
                    "Attendance tracking feature is currently being enhanced. "
                    "For now, please check your attendance records in the HRMS portal "
                    "or contact HR for attendance-related queries.\n\n"
                    "Coming soon:\n"
                    "• View daily attendance records\n"
                    "• Check-in/Check-out history\n"
                    "• Monthly attendance summary\n"
                    "• Late arrival tracking"
                )
            except Exception as e:
                logger.error(f"Error viewing attendance history: {str(e)}")
                return f"Error viewing attendance history: {str(e)}"

        @tool
        def get_monthly_summary(month: Optional[str] = None, year: Optional[str] = None) -> str:
            """
            Get monthly attendance summary.

            Args:
                month: Month number (1-12, defaults to current month)
                year: Year (defaults to current year)

            Returns:
                Summary of attendance for the month
            """
            try:
                # Placeholder for when API is ready
                return (
                    "Monthly attendance summary feature is coming soon. "
                    "For now, please refer to the HRMS portal for your attendance reports."
                )
            except Exception as e:
                logger.error(f"Error getting monthly summary: {str(e)}")
                return f"Error getting monthly summary: {str(e)}"

        @tool
        def search_attendance_policy(query: str) -> str:
            """
            Search for attendance-related policies and guidelines.

            Args:
                query: Question about attendance policies

            Returns:
                Answer based on company attendance policies
            """
            try:
                # Use RAG tool to search policies
                return search_hr_policies(query)
            except Exception as e:
                logger.error(f"Error searching attendance policy: {str(e)}")
                return f"Error searching attendance policy: {str(e)}"

        return [
            view_attendance_history,
            get_monthly_summary,
            search_attendance_policy
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools"""

        template = """You are a helpful HR assistant specialized in attendance management.

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
- For policy questions, use the search_attendance_policy tool
- Inform users that attendance tracking features are being enhanced
- Suggest checking the HRMS portal for detailed records
- Provide helpful information about attendance policies

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
        Process an attendance-related query

        Args:
            query: User query about attendance
            context: Optional context (user_id, history, etc.)

        Returns:
            Agent's response
        """
        try:
            logger.info(f"AttendanceAgent processing query: {query[:100]}...")

            # Invoke the agent
            result = self.agent.invoke({"input": query})

            # Extract the output
            output = result.get("output", "I apologize, but I couldn't process your request.")

            logger.info(f"AttendanceAgent response generated successfully")
            return output

        except Exception as e:
            logger.error(f"Error in AttendanceAgent: {str(e)}", exc_info=True)
            return (
                f"I apologize, but I encountered an error while processing your attendance request. "
                f"Please try again or contact HR directly.\n\nError: {str(e)}"
            )
