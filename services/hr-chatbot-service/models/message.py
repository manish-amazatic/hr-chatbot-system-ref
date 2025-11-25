"""
Chat Message Model
Stores individual messages within chat sessions
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class ChatMessage(Base):
    """
    Chat Message Model

    Stores individual messages including:
    - Message content
    - Role (user/assistant/system)
    - Sources (for RAG responses)
    - Agent information
    - Timestamps
    """
    __tablename__ = "chat_messages"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to session
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Message details
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)

    # RAG sources (JSON array of source documents)
    sources = Column(JSON, nullable=True, default=list)

    # Agent information
    agent_used = Column(String(50), nullable=True)  # Which agent processed this

    # Confidence/relevance score
    confidence_score = Column(Float, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, session_id={self.session_id})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "sources": self.sources,
            "agent_used": self.agent_used,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
