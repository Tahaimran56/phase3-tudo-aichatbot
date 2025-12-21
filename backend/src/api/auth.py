"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, Response, status

from ..schemas.user import MessageResponse, SigninRequest, UserCreate, UserResponse
from ..services.auth_service import AuthService
from .deps import CurrentUser, DbSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: DbSession, response: Response) -> UserResponse:
    """Create a new user account.

    Returns the created user and sets session cookie.
    """
    # Check if email already exists
    existing_user = AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = AuthService.create_user(db, user_data)

    # Create session token and set cookie
    token = AuthService.create_access_token(user.id)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return UserResponse.model_validate(user)


@router.post("/signin", response_model=UserResponse)
def signin(credentials: SigninRequest, db: DbSession, response: Response) -> UserResponse:
    """Authenticate user with email and password.

    Returns user info and sets session cookie.
    """
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create session token and set cookie
    token = AuthService.create_access_token(user.id)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return UserResponse.model_validate(user)


@router.post("/signout", response_model=MessageResponse)
def signout(response: Response, current_user: CurrentUser) -> MessageResponse:
    """Sign out and invalidate session."""
    response.delete_cookie(key="session")
    return MessageResponse(message="Successfully signed out")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)
