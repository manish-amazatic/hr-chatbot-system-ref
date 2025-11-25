"""
Payroll Agent
Specialized LangChain agent for payroll and compensation queries
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


class PayrollAgent:
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

    def __init__(self, hrms_client: HRMSClient):
        """
        Initialize Payroll Agent

        Args:
            hrms_client: HRMS API client instance
        """
        self.hrms_client = hrms_client
        self.llm = LLMProcessor().get_llm(LLMProvider.OPENAI)
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self):
        """Create LangChain tools for payroll operations"""

        @tool
        def get_latest_payslip() -> str:
            """
            Get the latest payslip information.

            Returns:
                Details of the most recent payslip
            """
            try:
                # Note: HRMS API payroll endpoints not yet implemented
                # This is a placeholder for when the API is ready
                return (
                    "Payslip retrieval feature is currently being enhanced. "
                    "For now, please access your payslips through:\n\n"
                    "• HRMS Portal: Check 'My Payslips' section\n"
                    "• Email: Payslips are sent monthly to your work email\n"
                    "• HR Department: Contact hr@company.com for assistance\n\n"
                    "Coming soon:\n"
                    "• Direct payslip viewing in chat\n"
                    "• YTD earnings summary\n"
                    "• Tax calculation breakdown\n"
                    "• Historical payslip access"
                )
            except Exception as e:
                logger.error(f"Error getting payslip: {str(e)}")
                return f"Error retrieving payslip: {str(e)}"

        @tool
        def get_ytd_summary(year: Optional[str] = None) -> str:
            """
            Get year-to-date earnings summary.

            Args:
                year: Year for the summary (defaults to current year)

            Returns:
                YTD earnings, deductions, and net pay summary
            """
            try:
                # Placeholder for when API is ready
                return (
                    "Year-to-date summary feature is coming soon. "
                    "For now, you can find this information:\n\n"
                    "• In your monthly payslips (cumulative section)\n"
                    "• HRMS Portal under 'Payroll Summary'\n"
                    "• By contacting the payroll team at payroll@company.com"
                )
            except Exception as e:
                logger.error(f"Error getting YTD summary: {str(e)}")
                return f"Error getting YTD summary: {str(e)}"

        @tool
        def search_payroll_policy(query: str) -> str:
            """
            Search for payroll and compensation policies.

            Use this for questions about:
            - Salary structure
            - Allowances and benefits
            - Tax deductions
            - Bonus policies
            - Increment policies
            - Compensation guidelines

            Args:
                query: Question about payroll policies

            Returns:
                Answer based on company payroll policies
            """
            try:
                # Use RAG tool to search policies
                return search_hr_policies(query)
            except Exception as e:
                logger.error(f"Error searching payroll policy: {str(e)}")
                return f"Error searching payroll policy: {str(e)}"

        @tool
        def explain_payslip_component(component: str) -> str:
            """
            Explain a specific payslip component or deduction.

            Args:
                component: The payslip component to explain (e.g., "HRA", "PF", "TDS")

            Returns:
                Explanation of the component
            """
            try:
                # Common payslip components
                explanations = {
                    "hra": "HRA (House Rent Allowance) is a component of your salary paid by your employer to meet your accommodation expenses. It's partially tax-exempt under certain conditions.",
                    "pf": "PF (Provident Fund) is a retirement savings scheme where both you and your employer contribute a percentage of your basic salary. Your contribution is 12% and employer's contribution is also 12%.",
                    "tds": "TDS (Tax Deducted at Source) is the income tax deducted from your salary by your employer as per Income Tax Act. The amount depends on your tax slab.",
                    "esi": "ESI (Employee State Insurance) is a social security scheme providing medical and cash benefits to employees earning below a certain threshold.",
                    "gratuity": "Gratuity is a lump sum amount paid by the employer to an employee at the time of leaving the organization after completing at least 5 years of continuous service.",
                    "basic": "Basic salary is the fixed component of your salary before any additions or deductions. It typically forms 40-50% of your CTC.",
                    "da": "DA (Dearness Allowance) is a cost of living adjustment allowance paid to employees to offset the impact of inflation.",
                    "bonus": "Bonus is an additional payment made to employees based on company performance, individual performance, or as per statutory requirements.",
                    "professional_tax": "Professional Tax is a state-level tax levied on income earned through employment or profession. The amount varies by state."
                }

                component_lower = component.lower().replace(" ", "_")
                
                # Check if we have a direct explanation
                for key, explanation in explanations.items():
                    if key in component_lower or component_lower in key:
                        return f"{explanation}\n\nFor more specific details about your payslip, please check the HRMS portal or contact payroll@company.com."

                # If not found, search policies
                return search_hr_policies(f"What is {component} in payslip?")

            except Exception as e:
                logger.error(f"Error explaining payslip component: {str(e)}")
                return f"Error explaining component: {str(e)}"

        return [
            get_latest_payslip,
            get_ytd_summary,
            search_payroll_policy,
            explain_payslip_component
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools"""

        template = """You are a helpful HR assistant specialized in payroll and compensation queries.

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
- For policy questions, use the search_payroll_policy tool
- For payslip component questions, use explain_payslip_component
- Inform users that payslip access features are being enhanced
- Suggest checking the HRMS portal or contacting payroll team for specific queries
- Be sensitive about compensation-related topics

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
        Process a payroll-related query

        Args:
            query: User query about payroll
            context: Optional context (user_id, history, etc.)

        Returns:
            Agent's response
        """
        try:
            logger.info(f"PayrollAgent processing query: {query[:100]}...")

            # Invoke the agent
            result = self.agent.invoke({"input": query})

            # Extract the output
            output = result.get("output", "I apologize, but I couldn't process your request.")

            logger.info(f"PayrollAgent response generated successfully")
            return output

        except Exception as e:
            logger.error(f"Error in PayrollAgent: {str(e)}", exc_info=True)
            return (
                f"I apologize, but I encountered an error while processing your payroll request. "
                f"Please try again or contact the payroll team at payroll@company.com.\n\nError: {str(e)}"
            )
