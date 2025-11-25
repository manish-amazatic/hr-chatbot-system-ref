"""
Chat Session Model
Stores chat sessions for users
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base


class ChatSession(Base):
    """
    Chat Session Model

    Stores information about chat sessions including:
    - Session ID
    - User ID (from HRMS)
    - Session title
    - Metadata
    - Timestamps
    """
    __tablename__ = "chat_sessions"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User information
    user_id = Column(String(10), nullable=False, index=True)  # EMP001, EMP002, etc.

    # Session details
    title = Column(String(200), nullable=True)

    # Session metadata (JSON field for flexibility)
    session_metadata = Column(JSON, nullable=True, default=dict)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title={self.title})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "metadata": self.session_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": len(self.messages) if self.messages else 0
        }
