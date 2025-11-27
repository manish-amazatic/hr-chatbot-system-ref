"""
Orchestrator Agent
Routes user queries to specialized agents based on intent classification
"""
import logging
from typing import Dict, Any, Optional
from enum import Enum

from core.agents.leave_agent import LeaveAgent
from core.agents.attendance_agent import AttendanceAgent
from core.agents.payroll_agent import PayrollAgent
from core.tools.hrms_api_client import HRMSClient
from core.tools.hr_rag_tool import search_hr_policies
from core.processors.llm_processor import LLMProcessor

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """User intent categories"""
    LEAVE = "leave"
    ATTENDANCE = "attendance"
    PAYROLL = "payroll"
    POLICY = "policy"
    GENERAL_HR = "general_hr"
    UNKNOWN = "unknown"


class Orchestrator:
    """
    Main orchestrator for HR Chatbot

    Responsibilities:
    - Classify user intent from query
    - Route to appropriate specialized agent
    - Handle unsupported queries gracefully
    - Coordinate multi-agent workflows (future)

    Currently supports:
    - Leave management (via LeaveAgent)

    Coming soon:
    - Attendance tracking
    - Payroll queries
    - General HR questions (via RAG)
    """

    def __init__(self, hrms_token: Optional[str] = None):
        """
        Initialize Orchestrator

        Args:
            hrms_token: JWT token for HRMS API authentication
        """
        self.hrms_token = hrms_token
        self.llm = LLMProcessor().get_llm()

        # Initialize HRMS client
        self.hrms_client = HRMSClient(token=hrms_token)

        # Initialize specialized agents
        self.leave_agent = LeaveAgent(hrms_client=self.hrms_client)
        self.attendance_agent = AttendanceAgent(hrms_client=self.hrms_client)
        self.payroll_agent = PayrollAgent(hrms_client=self.hrms_client)

        # Intent keywords for heuristic classification
        self.intent_keywords = {
            Intent.LEAVE: [
                "leave", "vacation", "time off", "pto", "holiday",
                "sick leave", "annual leave", "casual leave",
                "maternity", "paternity", "apply", "balance",
                "cancel leave", "leave request", "leave history",
                "days off", "absence", "off work"
            ],
            Intent.ATTENDANCE: [
                "attendance", "check in", "check out", "clock in",
                "clock out", "working hours", "present", "absent",
                "late", "early departure", "overtime", "timesheet",
                "punch in", "punch out", "attendance record"
            ],
            Intent.PAYROLL: [
                "payroll", "salary", "payslip", "pay stub", "wages",
                "compensation", "earnings", "deductions", "tax",
                "allowance", "bonus", "commission", "ytd",
                "year to date", "payment", "gross pay", "net pay"
            ],
            Intent.POLICY: [
                "policy", "policies", "rule", "rules", "regulation",
                "guideline", "guidelines", "procedure", "process",
                "manual", "handbook", "company policy", "hr policy",
                "code of conduct", "compliance", "standard",
                "protocol", "document", "documentation"
            ]
        }

    def classify_intent(self, query: str) -> Intent:
        """
        Classify user intent using keyword matching with policy priority

        Static knowledge questions (policy/informational) → RAG tool
        Transactional actions (apply, cancel, check my) → Agents

        Args:
            query: User query text

        Returns:
            Classified intent
        """
        query_lower = query.lower()

        # STEP 1: Check for explicit policy keywords (highest priority)
        # These indicate static knowledge questions that should use RAG
        explicit_policy_keywords = [
            "policy", "policies", "guideline", "guidelines", "handbook",
            "manual", "rule", "rules", "regulation", "code of conduct",
            "procedure", "protocol", "standard"
        ]
        if any(keyword in query_lower for keyword in explicit_policy_keywords):
            return Intent.POLICY

        # STEP 2: Check for informational question patterns
        # Questions like "what is", "how many", "explain" are usually policy/knowledge queries
        question_patterns = [
            "what is", "what are", "what's", "how many", "how much", "how is",
            "explain", "tell me about", "describe", "can you explain",
            "how does", "how do", "when is", "when do", "who is eligible",
            "eligibility", "criteria", "requirements for"
        ]

        has_question_pattern = any(pattern in query_lower for pattern in question_patterns)

        # STEP 3: Check for transactional action verbs
        # These indicate the user wants to DO something, not just learn about it
        action_verbs = [
            "apply for", "cancel", "book", "request", "submit",
            "check my", "show my", "get my", "view my", "see my",
            "i want to", "i need to", "help me"
        ]

        has_action_verb = any(verb in query_lower for verb in action_verbs)

        # DECISION LOGIC:
        # If it's a question pattern WITHOUT action verbs → POLICY (static knowledge)
        # If it has action verbs → Route to appropriate transactional agent

        if has_question_pattern and not has_action_verb:
            # Informational question → Use RAG for policy lookup
            return Intent.POLICY

        # STEP 4: Count keyword matches for transactional intents
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            if intent == Intent.POLICY:
                continue  # Already handled above
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores[intent] = score

        # Get intent with highest score
        if intent_scores and max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)

        # STEP 5: Fallback to general HR if it's a question
        question_words = ["what", "how", "when", "where", "why", "who", "can", "should", "is", "are", "do"]
        if any(word in query_lower.split() for word in question_words):
            return Intent.GENERAL_HR

        return Intent.UNKNOWN

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user query by routing to appropriate agent

        Args:
            query: User query text
            context: Optional context (user_id, session_id, history, etc.)

        Returns:
            Dict containing:
                - response: Agent's response text
                - intent: Detected intent
                - agent_used: Which agent processed the query
                - metadata: Additional information
        """
        try:
            # Classify intent
            intent = self.classify_intent(query)
            logger.info(f"Classified intent: {intent} for query: {query[:50]}...")

            # Route to appropriate agent
            if intent == Intent.LEAVE:
                return await self._handle_leave_query(query, context)

            elif intent == Intent.POLICY:
                return await self._handle_policy_query(query, context)

            elif intent == Intent.ATTENDANCE:
                return await self._handle_attendance_query(query, context)

            elif intent == Intent.PAYROLL:
                return await self._handle_payroll_query(query, context)

            elif intent == Intent.GENERAL_HR:
                return await self._handle_general_hr_query(query, context)

            else:
                return self._handle_unknown_intent(query)

        except Exception as e:
            logger.error(f"Error in Orchestrator: {str(e)}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "intent": "error",
                "agent_used": "orchestrator",
                "metadata": {"error": str(e)}
            }

    async def _handle_leave_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle leave-related queries via LeaveAgent"""
        logger.info("Routing to LeaveAgent")

        try:
            response = await self.leave_agent.process(query, context)

            return {
                "response": response,
                "intent": Intent.LEAVE,
                "agent_used": "leave_agent",
                "metadata": {
                    "tools_available": ["check_leave_balance", "apply_for_leave",
                                       "view_leave_history", "cancel_leave_request"]
                }
            }
        except Exception as e:
            logger.error(f"Error in LeaveAgent: {str(e)}", exc_info=True)
            return {
                "response": f"I encountered an error processing your leave request: {str(e)}",
                "intent": Intent.LEAVE,
                "agent_used": "leave_agent",
                "metadata": {"error": str(e)}
            }

    async def _handle_attendance_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle attendance-related queries via AttendanceAgent"""
        logger.info("Routing to AttendanceAgent")

        try:
            response = await self.attendance_agent.process(query, context)

            return {
                "response": response,
                "intent": Intent.ATTENDANCE,
                "agent_used": "attendance_agent",
                "metadata": {
                    "tools_available": ["view_attendance_history",
                                       "get_monthly_summary",
                                       "search_attendance_policy"]
                }
            }
        except Exception as e:
            logger.error(f"Error in AttendanceAgent: {str(e)}", exc_info=True)
            return {
                "response": f"I encountered an error processing your attendance request: {str(e)}",
                "intent": Intent.ATTENDANCE,
                "agent_used": "attendance_agent",
                "metadata": {"error": str(e)}
            }

    async def _handle_payroll_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle payroll-related queries via PayrollAgent"""
        logger.info("Routing to PayrollAgent")

        try:
            response = await self.payroll_agent.process(query, context)

            return {
                "response": response,
                "intent": Intent.PAYROLL,
                "agent_used": "payroll_agent",
                "metadata": {
                    "tools_available": ["get_latest_payslip",
                                       "get_ytd_summary",
                                       "search_payroll_policy",
                                       "explain_payslip_component"]
                }
            }
        except Exception as e:
            logger.error(f"Error in PayrollAgent: {str(e)}", exc_info=True)
            return {
                "response": f"I encountered an error processing your payroll request: {str(e)}",
                "intent": Intent.PAYROLL,
                "agent_used": "payroll_agent",
                "metadata": {"error": str(e)}
            }

    async def _handle_policy_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle HR policy queries via RAG tool"""
        logger.info("Routing to RAG tool for policy search")

        try:
            # Use RAG tool to search HR policies
            response = search_hr_policies.invoke({"query": query})

            # Check if Milvus was unavailable
            if "currently unavailable" in response.lower():
                return {
                    "response": response,
                    "intent": Intent.POLICY,
                    "agent_used": "rag_tool",
                    "metadata": {
                        "status": "milvus_unavailable",
                        "fallback": "system_message"
                    }
                }

            return {
                "response": response,
                "intent": Intent.POLICY,
                "agent_used": "rag_tool",
                "metadata": {
                    "type": "policy_search",
                    "rag_enabled": True
                }
            }
        except Exception as e:
            logger.error(f"Error in policy query handler: {str(e)}", exc_info=True)
            return {
                "response": (
                    "I encountered an error while searching for HR policy information. "
                    "Please try rephrasing your question or contact HR directly at hr@company.com."
                ),
                "intent": Intent.POLICY,
                "agent_used": "rag_tool",
                "metadata": {"error": str(e)}
            }

    async def _handle_general_hr_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle general HR questions using LLM"""
        logger.info("Handling general HR query with LLM")

        try:
            # Simple LLM response for general questions
            system_prompt = """You are a helpful HR assistant.

            You can help employees with:
            - Leave management (checking balance, applying for leave, viewing history)

            Features coming soon:
            - Attendance tracking
            - Payroll queries
            - HR policy questions

            For now, focus on helping with leave-related questions or providing general HR guidance.
            Keep responses concise and professional."""

            response = self.llm.invoke(f"{system_prompt}\n\nUser: {query}\n\nAssistant:")

            return {
                "response": response.content if hasattr(response, 'content') else str(response),
                "intent": Intent.GENERAL_HR,
                "agent_used": "llm_fallback",
                "metadata": {"type": "general_question"}
            }
        except Exception as e:
            logger.error(f"Error in general HR query handler: {str(e)}", exc_info=True)
            return {
                "response": "I can help you with leave management queries. Could you please rephrase your question?",
                "intent": Intent.GENERAL_HR,
                "agent_used": "llm_fallback",
                "metadata": {"error": str(e)}
            }

    def _handle_unsupported_intent(self, feature_name: str, message: str) -> Dict[str, Any]:
        """Handle queries for features not yet implemented"""
        logger.info(f"Unsupported intent: {feature_name}")

        return {
            "response": f"{message}\n\nI can currently help you with:\n"
                       "• Checking your leave balance\n"
                       "• Applying for leave\n"
                       "• Viewing your leave history\n"
                       "• Cancelling leave requests\n\n"
                       "How can I assist you with leave management?",
            "intent": feature_name,
            "agent_used": "orchestrator",
            "metadata": {"feature_status": "not_implemented"}
        }

    def _handle_unknown_intent(self, query: str) -> Dict[str, Any]:
        """Handle queries with unknown intent"""
        logger.info(f"Unknown intent for query: {query[:50]}...")

        return {
            "response": "I'm not sure I understand your request. I can help you with:\n\n"
                       "• Leave Management:\n"
                       "  - Check your leave balance\n"
                       "  - Apply for leave\n"
                       "  - View leave history\n"
                       "  - Cancel leave requests\n\n"
                       "Please let me know how I can assist you!",
            "intent": Intent.UNKNOWN,
            "agent_used": "orchestrator",
            "metadata": {"suggestion": "rephrase_query"}
        }

    async def close(self):
        """Clean up resources"""
        await self.hrms_client.close()
