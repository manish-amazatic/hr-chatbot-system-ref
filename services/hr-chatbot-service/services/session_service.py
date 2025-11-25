"""
Session Service
Handles CRUD operations for chat sessions and messages
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from models import ChatSession, ChatMessage, User


class SessionService:
    """
    Service for managing chat sessions and messages

    Provides CRUD operations for:
    - Creating and managing chat sessions
    - Adding and retrieving messages
    - Managing user cache
    """

    @staticmethod
    def create_session(db: Session, user_id: str, title: Optional[str] = None) -> ChatSession:
        """
        Create a new chat session

        Args:
            db: Database session
            user_id: Employee ID (e.g., EMP001)
            title: Optional session title

        Returns:
            ChatSession: The created session
        """
        session = ChatSession(
            user_id=user_id,
            title=title or "New Chat Session"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[ChatSession]:
        """
        Get a chat session by ID

        Args:
            db: Database session
            session_id: Session UUID

        Returns:
            Optional[ChatSession]: The session if found, None otherwise
        """
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSession]:
        """
        Get all sessions for a user

        Args:
            db: Database session
            user_id: Employee ID
            limit: Maximum number of sessions to return
            offset: Offset for pagination

        Returns:
            List[ChatSession]: List of sessions ordered by updated_at (newest first)
        """
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def update_session_title(
        db: Session,
        session_id: str,
        title: str
    ) -> Optional[ChatSession]:
        """
        Update session title

        Args:
            db: Database session
            session_id: Session UUID
            title: New title

        Returns:
            Optional[ChatSession]: Updated session if found, None otherwise
        """
        session = SessionService.get_session(db, session_id)
        if session:
            session.title = title
            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """
        Delete a chat session and all its messages

        Args:
            db: Database session
            session_id: Session UUID

        Returns:
            bool: True if deleted, False if not found
        """
        session = SessionService.get_session(db, session_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def add_message(
        db: Session,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[dict]] = None,
        agent_used: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> ChatMessage:
        """
        Add a message to a chat session

        Args:
            db: Database session
            session_id: Session UUID
            role: Message role ('user' or 'assistant')
            content: Message content
            sources: Optional list of RAG source documents
            agent_used: Optional agent name that processed this message
            confidence_score: Optional confidence/relevance score

        Returns:
            ChatMessage: The created message
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources or [],
            agent_used=agent_used,
            confidence_score=confidence_score
        )
        db.add(message)

        # Update session's updated_at timestamp
        session = SessionService.get_session(db, session_id)
        if session:
            session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_session_messages(
        db: Session,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        Get all messages for a session

        Args:
            db: Database session
            session_id: Session UUID
            limit: Optional maximum number of messages
            offset: Offset for pagination

        Returns:
            List[ChatMessage]: List of messages ordered by timestamp (oldest first)
        """
        query = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp)
            .offset(offset)
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_message(db: Session, message_id: str) -> Optional[ChatMessage]:
        """
        Get a message by ID

        Args:
            db: Database session
            message_id: Message UUID

        Returns:
            Optional[ChatMessage]: The message if found, None otherwise
        """
        return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    @staticmethod
    def cache_user(
        db: Session,
        user_id: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        department: Optional[str] = None,
        designation: Optional[str] = None
    ) -> User:
        """
        Cache or update user information from HRMS

        Args:
            db: Database session
            user_id: Employee ID
            email: User email
            first_name: First name
            last_name: Last name
            department: Department
            designation: Designation

        Returns:
            User: The cached user
        """
        user = db.query(User).filter(User.id == user_id).first()

        if user:
            # Update existing user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.department = department
            user.designation = designation
            user.updated_at = datetime.utcnow()
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                department=department,
                designation=designation,
                last_login=datetime.utcnow()
            )
            db.add(user)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """
        Get cached user by ID

        Args:
            db: Database session
            user_id: Employee ID

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get cached user by email

        Args:
            db: Database session
            email: User email

        Returns:
            Optional[User]: The user if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
