"""API dependencies for authentication and database sessions."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..services.auth_service import AuthService


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    session_token: Annotated[str | None, Cookie(alias="session")] = None,
) -> User:
    """Get current authenticated user from session cookie.

    Raises HTTPException 401 if not authenticated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if session_token is None:
        raise credentials_exception

    user_id = AuthService.decode_token(session_token)
    if user_id is None:
        raise credentials_exception

    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
