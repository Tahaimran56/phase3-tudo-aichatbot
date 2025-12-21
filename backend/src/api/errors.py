"""Error handling and HTTP exceptions."""

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str
    message: str
    status_code: int


def not_found_exception(resource: str = "Resource") -> HTTPException:
    """Create a 404 Not Found exception."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
    )


def unauthorized_exception(message: str = "Not authenticated") -> HTTPException:
    """Create a 401 Unauthorized exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
    )


def forbidden_exception(message: str = "Access denied") -> HTTPException:
    """Create a 403 Forbidden exception."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


def bad_request_exception(message: str) -> HTTPException:
    """Create a 400 Bad Request exception."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


def conflict_exception(message: str) -> HTTPException:
    """Create a 409 Conflict exception."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )
