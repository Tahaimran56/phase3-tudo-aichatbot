"""Pydantic schemas for user-related requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user signup request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class SigninRequest(BaseModel):
    """Schema for user signin request."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (excludes password)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Schema for token response after authentication."""

    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Schema for simple message response."""

    message: str
