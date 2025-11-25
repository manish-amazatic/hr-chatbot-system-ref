"""
Memory Service
Integrates LangChain ConversationBufferMemory with database storage
"""
import logging
from typing import Optional, Dict, Any, List
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from models import ChatSession, ChatMessage
from services.session_service import SessionService

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing conversation memory

    Bridges LangChain's ConversationBufferMemory with database persistence.
    Enables agents to maintain context across conversation turns while
    storing all messages in the database for history and analytics.
    """

    def __init__(self, db_session):
        """
        Initialize Memory Service

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.session_service = SessionService()
        self._memory_cache: Dict[str, ConversationBufferMemory] = {}

    def get_or_create_memory(
        self,
        session_id: str,
        max_token_limit: int = 2000
    ) -> ConversationBufferMemory:
        """
        Get or create conversation memory for a session

        Args:
            session_id: Chat session ID
            max_token_limit: Maximum tokens to keep in memory

        Returns:
            ConversationBufferMemory instance loaded with session history
        """
        # Check cache first
        if session_id in self._memory_cache:
            logger.debug(f"Using cached memory for session {session_id}")
            return self._memory_cache[session_id]

        # Create new memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=max_token_limit
        )

        # Load historical messages from database
        messages = self.session_service.get_session_messages(
            self.db,
            session_id,
            limit=20  # Last 20 messages for context
        )

        # Add messages to memory
        for msg in messages:
            if msg.role == "user":
                memory.chat_memory.add_user_message(msg.content)
            elif msg.role == "assistant":
                memory.chat_memory.add_ai_message(msg.content)

        # Cache the memory
        self._memory_cache[session_id] = memory

        logger.info(f"Created memory for session {session_id} with {len(messages)} historical messages")
        return memory

    def add_user_message(
        self,
        session_id: str,
        message: str,
        memory: Optional[ConversationBufferMemory] = None
    ) -> ChatMessage:
        """
        Add user message to both memory and database

        Args:
            session_id: Chat session ID
            message: User message content
            memory: Optional memory instance (will create if not provided)

        Returns:
            ChatMessage: The saved message
        """
        # Get or create memory
        if memory is None:
            memory = self.get_or_create_memory(session_id)

        # Add to memory
        memory.chat_memory.add_user_message(message)

        # Save to database
        db_message = self.session_service.add_message(
            self.db,
            session_id=session_id,
            role="user",
            content=message
        )

        logger.debug(f"Added user message to session {session_id}")
        return db_message

    def add_assistant_message(
        self,
        session_id: str,
        message: str,
        memory: Optional[ConversationBufferMemory] = None,
        sources: Optional[List[dict]] = None,
        agent_used: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> ChatMessage:
        """
        Add assistant message to both memory and database

        Args:
            session_id: Chat session ID
            message: Assistant message content
            memory: Optional memory instance
            sources: Optional RAG sources
            agent_used: Agent that generated this response
            confidence_score: Optional confidence score

        Returns:
            ChatMessage: The saved message
        """
        # Get or create memory
        if memory is None:
            memory = self.get_or_create_memory(session_id)

        # Add to memory
        memory.chat_memory.add_ai_message(message)

        # Save to database
        db_message = self.session_service.add_message(
            self.db,
            session_id=session_id,
            role="assistant",
            content=message,
            sources=sources,
            agent_used=agent_used,
            confidence_score=confidence_score
        )

        logger.debug(f"Added assistant message to session {session_id}")
        return db_message

    def get_conversation_context(
        self,
        session_id: str,
        as_string: bool = False
    ) -> Any:
        """
        Get conversation context for a session

        Args:
            session_id: Chat session ID
            as_string: If True, return as formatted string; otherwise return messages

        Returns:
            Conversation history as string or list of messages
        """
        memory = self.get_or_create_memory(session_id)

        if as_string:
            # Format messages as a string
            messages = memory.chat_memory.messages
            context = ""
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    context += f"User: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    context += f"Assistant: {msg.content}\n"
            return context
        else:
            return memory.chat_memory.messages

    def clear_memory(self, session_id: str) -> None:
        """
        Clear memory for a session (does NOT delete from database)

        Args:
            session_id: Chat session ID
        """
        if session_id in self._memory_cache:
            self._memory_cache[session_id].clear()
            del self._memory_cache[session_id]
            logger.info(f"Cleared memory cache for session {session_id}")

    def get_recent_messages(
        self,
        session_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages from a session

        Args:
            session_id: Chat session ID
            limit: Number of recent messages to retrieve

        Returns:
            List of message dictionaries
        """
        messages = self.session_service.get_session_messages(
            self.db,
            session_id,
            limit=limit * 2  # Get both user and assistant messages
        )

        # Get the last N messages
        recent = messages[-limit*2:] if len(messages) > limit*2 else messages

        return [msg.to_dict() for msg in recent]

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary of a chat session

        Args:
            session_id: Chat session ID

        Returns:
            Dictionary with session summary
        """
        session = self.session_service.get_session(self.db, session_id)
        if not session:
            return {}

        messages = self.session_service.get_session_messages(self.db, session_id)

        # Count user and assistant messages
        user_msgs = sum(1 for msg in messages if msg.role == "user")
        assistant_msgs = sum(1 for msg in messages if msg.role == "assistant")

        # Get agents used
        agents_used = set(msg.agent_used for msg in messages if msg.agent_used)

        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "total_messages": len(messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "agents_used": list(agents_used)
        }
