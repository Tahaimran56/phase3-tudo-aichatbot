"""Pydantic schemas for chat-related requests and responses."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat request."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: UUID | None = None


class ToolCall(BaseModel):
    """Schema for tool call information."""

    id: str
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    """Schema for chat response."""

    conversation_id: UUID
    response: str
    tool_calls: list[ToolCall] = []
