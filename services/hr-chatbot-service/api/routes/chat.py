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

from core.agents.orchestrator import Orchestrator
from services.session_service import SessionService
from services.memory_service import MemoryService
from utils.database import get_db

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
async def list_sessions(user_id: Optional[str] = None):
    """
    List all chat sessions for a user
    """
    # TODO: Implement session retrieval from database
    logger.info(f"Listing sessions for user: {user_id}")

    # Placeholder response
    return []


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific session with all messages
    """
    # TODO: Implement session retrieval
    logger.info(f"Getting session: {session_id}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Session not found"
    )


@router.post("/sessions")
async def create_session(user_id: str, title: Optional[str] = None):
    """
    Create a new chat session
    """
    # TODO: Implement session creation
    logger.info(f"Creating session for user: {user_id}")

    session_id = f"session_{datetime.utcnow().timestamp()}"
    return Session(
        id=session_id,
        user_id=user_id,
        title=title or "New Chat",
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        message_count=0
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a chat session
    """
    # TODO: Implement session deletion
    logger.info(f"Deleting session: {session_id}")

    return {"message": "Session deleted successfully"}
