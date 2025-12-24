"""Pydantic schemas for message-related requests and responses."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    conversation_id: UUID
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=10000)


class MessageRead(BaseModel):
    """Schema for message response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    conversation_id: UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
