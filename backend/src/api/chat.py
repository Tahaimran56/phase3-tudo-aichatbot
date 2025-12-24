"""Chat API endpoints for AI-powered task management."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..api.errors import bad_request_exception
from ..schemas.chat import ChatRequest, ChatResponse, ToolCall
from ..services.chat_service import process_chat_message
from .deps import CurrentUser, DbSession

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit("60/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ChatResponse:
    """Process a chat message and return AI response.

    This endpoint:
    - Accepts user messages in natural language
    - Routes them to OpenAI with MCP tools
    - Executes tool calls (task operations)
    - Returns natural language responses
    - Persists conversation history

    Rate limit: 60 requests per minute per user

    Args:
        request: FastAPI request object (for rate limiting)
        chat_request: Chat request with message and optional conversation_id
        db: Database session
        current_user: Authenticated user

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls

    Raises:
        HTTPException 400: Invalid request (empty message, etc.)
        HTTPException 429: Rate limit exceeded
        HTTPException 500: OpenAI API error or internal error
    """
    # Validate message
    if not chat_request.message.strip():
        raise bad_request_exception("Message cannot be empty")

    try:
        logger.info(
            f"Chat request from user {current_user.id}: {chat_request.message[:50]}..."
        )

        # Process the chat message
        result = await process_chat_message(
            db=db,
            user_id=current_user.id,
            message=chat_request.message,
            conversation_id=chat_request.conversation_id,
        )

        # Format tool calls for response
        tool_calls = [
            ToolCall(
                id=tc["id"],
                name=tc["name"],
                arguments=tc["arguments"],
                result=None,  # Don't expose internal results to frontend
            )
            for tc in result.get("tool_calls", [])
        ]

        response = ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=tool_calls,
        )

        logger.info(
            f"Chat response for user {current_user.id}: {response.conversation_id}"
        )

        return response

    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # OpenAI API errors or other failures
        logger.error(f"Chat processing error: {str(e)}")

        # Check if it's an AI service error
        if "AI service error" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service temporarily unavailable. Please try again.",
            )

        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message. Please try again.",
        )
