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

from core.orchestrator import orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Chat message model"""
    # session_id: Optional[str] = None
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    sources: List[dict] = []
    agent_used: Optional[str] = None
    timestamp: str


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatMessage):
    """
    Send a message to the chatbot

    This endpoint:
    Routes the query through the Orchestrator agent with memory

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


        # Process the message through orchestrator with memory context
        result = await orchestrator.process(
            query=request.message,
            context={
                "user_id": user_id,
            }
        )


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

        # Build response
        return ChatResponse(
            # session_id=session_id,
            response=response_text,
            sources=sources,
            agent_used=agent_used,
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing message: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing your request:  {str(e)}"
        ) from e


@router.post("/message/stream")
async def send_message_stream(request: ChatMessage):
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
    session_id = "streaming-session"

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            # For streaming, we need to collect the full response first
            # (Current agents don't support streaming yet)
            result = await orchestrator.process(
                query=request.message,
                context={
                    "session_id": session_id,
                    "user_id": user_id,
                    # "memory": memory,
                    # "conversation_history": memory_service.get_conversation_context(session_id, as_string=True)
                }
            )

            # Get response details
            response_text = result.get("response", "I apologize, but I couldn't process your request.")
            agent_used = result.get("agent_used", "unknown")
            sources = result.get("metadata", {}).get("sources", [])
            
            # Ensure sources is a list of dicts
            if not isinstance(sources, list):
                sources = []
            else:
                sources = [s for s in sources if isinstance(s, dict)]

            # Stream the response word by word while preserving all whitespace
            import asyncio
            import re
            
            # Split by whitespace but capture the whitespace as separate tokens
            # This regex splits on whitespace while keeping the whitespace characters
            tokens = re.split(r'(\s+)', response_text)
            
            for token in tokens:
                if token:  # Skip empty tokens
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                    # Add small delay only for words, not for whitespace
                    if not token.isspace():
                        await asyncio.sleep(0.03)

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'agent_used': agent_used})}\n\n"

        except Exception as e:
            logger.error("Error in streaming: %s ", str(e), exc_info=True)
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
