"""
Chat Endpoints
Handles chat messages, sessions, and orchestrates agents
"""
from fastapi import APIRouter, HTTPException, status, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import logging
import json
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.agents.orchestrator import Orchestrator
from services.session_service import SessionService
from services.memory_service import MemoryService
from utils.database import get_db
from models import ChatSession

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Chat message model"""
    session_id: Optional[str] = None
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str
    response: str
    sources: List[dict] = []
    agent_used: Optional[str] = None
    timestamp: str


class Session(BaseModel):
    """Session model"""
    id: str
    user_id: str
    title: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int = 0


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatMessage,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Send a message to the chatbot

    This endpoint:
    1. Creates or retrieves a session
    2. Loads conversation history into memory
    3. Stores user message
    4. Routes the query through the Orchestrator agent with memory
    5. Stores assistant response
    6. Returns the response with sources

    Args:
        request: Chat message with query and session info
        db: Database session (injected)
        authorization: JWT token from HRMS login (format: "Bearer <token>")

    Returns:
        ChatResponse with agent's reply and session context
    """
    logger.info(f"Received message: {request.message[:50]}...")

    # Extract user_id from request or default
    user_id = request.user_id or "GUEST"

    try:
        # Get or create session
        if request.session_id:
            session = SessionService.get_session(db, request.session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session {request.session_id} not found"
                )
            session_id = session.id
        else:
            # Create new session
            session = SessionService.create_session(
                db,
                user_id=user_id,
                title="New Chat"
            )
            session_id = session.id
            logger.info(f"Created new session: {session_id}")

        # Initialize memory service
        memory_service = MemoryService(db)

        # Get or create memory with conversation history
        memory = memory_service.get_or_create_memory(session_id)

        # Store user message in DB and memory
        memory_service.add_user_message(session_id, request.message, memory)

        # Extract token from Authorization header
        hrms_token = None
        if authorization and authorization.startswith("Bearer "):
            hrms_token = authorization
        elif authorization:
            hrms_token = f"Bearer {authorization}"

        # Initialize orchestrator with HRMS token
        orchestrator = Orchestrator(hrms_token=hrms_token)

        # Process the message through orchestrator with memory context
        result = await orchestrator.process(
            query=request.message,
            context={
                "session_id": session_id,
                "user_id": user_id,
                "memory": memory,
                "conversation_history": memory_service.get_conversation_context(session_id, as_string=True)
            }
        )

        # Clean up orchestrator resources
        await orchestrator.close()

        # Get response details
        response_text = result.get("response", "I apologize, but I couldn't process your request.")
        agent_used = result.get("agent_used", "unknown")
        sources = result.get("metadata", {}).get("sources", [])
        
        # Ensure sources is a list of dicts (validate format)
        if not isinstance(sources, list):
            sources = []
        else:
            # Filter out any non-dict items
            sources = [s for s in sources if isinstance(s, dict)]

        # Store assistant message in DB and memory
        memory_service.add_assistant_message(
            session_id,
            response_text,
            memory,
            sources=sources,
            agent_used=agent_used
        )

        # Update session title if it's the first exchange
        if session.title == "New Chat":
            # Generate title from first user message (first 50 chars)
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            SessionService.update_session_title(db, session_id, title)

        # Build response
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            sources=sources,
            agent_used=agent_used,
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing your request: {str(e)}"
        )


@router.post("/message/stream")
async def send_message_stream(
    request: ChatMessage,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Send a message to the chatbot with streaming response

    This endpoint streams the response back to the client in real-time
    using Server-Sent Events (SSE) format.

    Response format:
        data: {"type": "token", "content": "Hello"}
        data: {"type": "token", "content": " world"}
        data: {"type": "done", "session_id": "..."}

    Args:
        request: Chat message with query and session info
        db: Database session (injected)
        authorization: JWT token from HRMS login

    Returns:
        StreamingResponse with SSE events
    """
    logger.info(f"Received streaming message: {request.message[:50]}...")

    # Extract user_id from request or default
    user_id = request.user_id or "GUEST"

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            # Get or create session
            if request.session_id:
                session = SessionService.get_session(db, request.session_id)
                if not session:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Session not found'})}\n\n"
                    return
                session_id = session.id
            else:
                # Create new session
                session = SessionService.create_session(
                    db,
                    user_id=user_id,
                    title="New Chat"
                )
                session_id = session.id
                logger.info(f"Created new session: {session_id}")

                # Send session info
                yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

            # Initialize memory service
            memory_service = MemoryService(db)
            memory = memory_service.get_or_create_memory(session_id)

            # Store user message
            memory_service.add_user_message(session_id, request.message, memory)

            # Extract token
            hrms_token = None
            if authorization and authorization.startswith("Bearer "):
                hrms_token = authorization
            elif authorization:
                hrms_token = f"Bearer {authorization}"

            # Initialize orchestrator
            orchestrator = Orchestrator(hrms_token=hrms_token)

            # For streaming, we need to collect the full response first
            # (Current agents don't support streaming yet)
            result = await orchestrator.process(
                query=request.message,
                context={
                    "session_id": session_id,
                    "user_id": user_id,
                    "memory": memory,
                    "conversation_history": memory_service.get_conversation_context(session_id, as_string=True)
                }
            )

            # Clean up orchestrator
            await orchestrator.close()

            # Get response details
            response_text = result.get("response", "I apologize, but I couldn't process your request.")
            agent_used = result.get("agent_used", "unknown")
            sources = result.get("metadata", {}).get("sources", [])
            
            # Ensure sources is a list of dicts
            if not isinstance(sources, list):
                sources = []
            else:
                sources = [s for s in sources if isinstance(s, dict)]

            # Stream the response word by word to simulate streaming
            words = response_text.split()
            for i, word in enumerate(words):
                content = word if i == 0 else f" {word}"
                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

            # Store assistant message
            memory_service.add_assistant_message(
                session_id,
                response_text,
                memory,
                sources=sources,
                agent_used=agent_used
            )

            # Update session title if needed
            if session.title == "New Chat":
                title = request.message[:50] + "..." if len(request.message) > 50 else request.message
                SessionService.update_session_title(db, session_id, title)

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'agent_used': agent_used})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/sessions", response_model=List[Session])
async def list_sessions(
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all chat sessions for a user

    Args:
        user_id: Optional user ID to filter sessions
        db: Database session (injected)

    Returns:
        List of sessions for the user
    """
    logger.info(f"Listing sessions for user: {user_id or 'all users'}")

    # Get sessions from database
    if user_id:
        sessions = SessionService.get_user_sessions(db, user_id)
    else:
        # If no user_id provided, return empty list or all sessions
        # For now, return all sessions by querying without filter
        sessions = db.query(ChatSession).order_by(desc(ChatSession.updated_at)).limit(50).all()

    return [
        Session(
            id=s.id,
            user_id=s.user_id,
            title=s.title,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
            message_count=len(s.messages) if hasattr(s, 'messages') and s.messages else 0
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific session

    Args:
        session_id: ID of the session to retrieve
        db: Database session (injected)

    Returns:
        Session object with details
    """
    logger.info(f"Getting session: {session_id}")

    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    return Session(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        message_count=len(session.messages) if hasattr(session, 'messages') and session.messages else 0
    )


class CreateSessionRequest(BaseModel):
    """Create session request model"""
    user_id: Optional[str] = None
    title: Optional[str] = None


@router.post("/sessions", response_model=Session)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new chat session

    Args:
        request: Session creation request with optional user_id and title
        db: Database session (injected)

    Returns:
        Session object with generated ID
    """
    user_id = request.user_id or "GUEST"
    title = request.title or "New Chat"

    logger.info(f"Creating session for user: {user_id}")

    # Create session in database
    session = SessionService.create_session(
        db,
        user_id=user_id,
        title=title
    )

    return Session(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        message_count=0
    )


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all messages for a specific session

    Args:
        session_id: ID of the session
        db: Database session (injected)

    Returns:
        List of messages in the session
    """
    logger.info(f"Getting messages for session: {session_id}")

    # Check if session exists
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Get messages from memory service
    memory_service = MemoryService(db)
    messages = memory_service.get_conversation_context(session_id)

    return messages


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all its messages

    Args:
        session_id: ID of the session to delete
        db: Database session (injected)

    Returns:
        Success message
    """
    logger.info(f"Deleting session: {session_id}")

    # Check if session exists
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Delete session (this should also delete associated messages via cascade)
    SessionService.delete_session(db, session_id)

    return {"message": "Session deleted successfully", "session_id": session_id}
