"""Chat service for OpenAI integration and conversation management.

This module handles:
- OpenAI API integration with function calling
- Conversation history management
- Message persistence
- Tool execution routing
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI, OpenAIError
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models.conversation import Conversation
from ..models.message import Message
from ..services.mcp_tools import execute_tool, get_tool_definitions

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
settings = get_settings()
openai_client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    timeout=settings.openai_timeout,
)


async def create_or_get_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID | None = None,
) -> Conversation:
    """Create a new conversation or get an existing one.

    Args:
        db: Database session
        user_id: ID of the user
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation object (new or existing)
    """
    if conversation_id:
        # Try to get existing conversation
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )
        if conversation:
            # Update timestamp
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(conversation)
            return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    logger.info(f"Created new conversation {conversation.id} for user {user_id}")
    return conversation


def get_conversation_history(
    db: Session,
    conversation_id: UUID,
    user_id: UUID,
    limit: int | None = None,
) -> list[dict[str, str]]:
    """Load conversation history from database.

    Args:
        db: Database session
        conversation_id: ID of the conversation
        user_id: ID of the user (for security check)
        limit: Maximum number of messages to load (default from config)

    Returns:
        List of message dicts in OpenAI format [{role, content}, ...]
    """
    if limit is None:
        limit = settings.max_conversation_messages

    # Load messages ordered by creation time (oldest first for context)
    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id,
        )
        .order_by(Message.created_at)
        .limit(limit)
        .all()
    )

    # Convert to OpenAI message format
    history = [{"role": msg.role, "content": msg.content} for msg in messages]

    logger.info(
        f"Loaded {len(history)} messages from conversation {conversation_id}"
    )
    return history


def save_message(
    db: Session,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
) -> Message:
    """Save a message to the database.

    Args:
        db: Database session
        conversation_id: ID of the conversation
        user_id: ID of the user
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Saved Message object
    """
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    logger.info(
        f"Saved {role} message to conversation {conversation_id}: {content[:50]}..."
    )
    return message


async def tool_call_handler(
    tool_calls: list[Any],
    db: Session,
    user_id: UUID,
) -> list[dict[str, Any]]:
    """Execute MCP tool calls and format results for OpenAI.

    Args:
        tool_calls: List of tool call objects from OpenAI response
        db: Database session
        user_id: ID of the user making the request

    Returns:
        List of tool results formatted for OpenAI
    """
    tool_results = []

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        logger.info(
            f"Executing tool {tool_name} with args {tool_args} for user {user_id}"
        )

        # Execute the tool
        result = execute_tool(
            tool_name=tool_name,
            tool_args=tool_args,
            db=db,
            user_id=user_id,
        )

        # Format result for OpenAI
        tool_results.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result),
            }
        )

        logger.info(f"Tool {tool_name} result: {result}")

    return tool_results


async def process_chat_message(
    db: Session,
    user_id: UUID,
    message: str,
    conversation_id: UUID | None = None,
) -> dict[str, Any]:
    """Process a chat message and generate AI response.

    This is the main chat processing function that:
    1. Creates/gets conversation
    2. Loads conversation history
    3. Saves user message
    4. Calls OpenAI with tools
    5. Handles tool calls if needed
    6. Saves assistant response
    7. Returns response to user

    Args:
        db: Database session
        user_id: ID of the user
        message: User's message text
        conversation_id: Optional existing conversation ID

    Returns:
        Dict with conversation_id, response, and tool_calls
    """
    try:
        # Step 1: Create or get conversation
        conversation = await create_or_get_conversation(
            db, user_id, conversation_id
        )

        # Step 2: Load conversation history
        history = get_conversation_history(
            db, conversation.id, user_id
        )

        # Step 3: Save user message
        save_message(
            db,
            conversation.id,
            user_id,
            role="user",
            content=message,
        )

        # Step 4: Prepare messages for OpenAI
        messages = history + [{"role": "user", "content": message}]

        # Add system message if this is a new conversation
        if not history:
            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant. "
                    "You help users manage their todo tasks using natural language. "
                    "When users ask to create, update, complete, delete, or list tasks, "
                    "use the appropriate tools. Be friendly and concise."
                ),
            }
            messages = [system_message] + messages

        logger.info(
            f"Calling OpenAI for conversation {conversation.id} with {len(messages)} messages"
        )

        # Step 5: Call OpenAI with tools
        response = await openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=get_tool_definitions(),
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        tool_calls_info = []

        # Step 6: Handle tool calls if present
        if assistant_message.tool_calls:
            logger.info(
                f"Processing {len(assistant_message.tool_calls)} tool calls"
            )

            # Execute tools
            tool_results = await tool_call_handler(
                assistant_message.tool_calls, db, user_id
            )

            # Store tool call info for response
            for tool_call in assistant_message.tool_calls:
                tool_calls_info.append(
                    {
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments),
                    }
                )

            # Call OpenAI again with tool results to get natural language response
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in assistant_message.tool_calls
                    ],
                }
            )
            messages.extend(tool_results)

            # Get final response
            final_response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
            )

            final_message = final_response.choices[0].message.content or ""
        else:
            # No tool calls, use direct response
            final_message = assistant_message.content or ""

        # Step 7: Save assistant response
        save_message(
            db,
            conversation.id,
            user_id,
            role="assistant",
            content=final_message,
        )

        logger.info(
            f"Completed chat processing for conversation {conversation.id}"
        )

        return {
            "conversation_id": conversation.id,
            "response": final_message,
            "tool_calls": tool_calls_info,
        }

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise Exception(f"AI service error: {str(e)}")
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise
