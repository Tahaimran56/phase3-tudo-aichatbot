"""Authentication service with password hashing and JWT token management."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models.user import User
from ..schemas.user import UserCreate

settings = get_settings()


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def create_access_token(user_id: UUID) -> str:
        """Create JWT access token for user."""
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
        }
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def decode_token(token: str) -> UUID | None:
        """Decode JWT token and return user_id if valid."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id_str: str | None = payload.get("sub")
            if user_id_str is None:
                return None
            return UUID(user_id_str)
        except JWTError:
            return None

    @classmethod
    def create_user(cls, db: Session, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        password_hash = cls.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not cls.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Get user by email address."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User | None:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
