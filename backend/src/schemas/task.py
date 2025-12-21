"""Pydantic schemas for task-related requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str = Field(..., min_length=1, max_length=255)


class TaskResponse(BaseModel):
    """Schema for task response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
