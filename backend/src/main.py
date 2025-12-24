"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .api.auth import router as auth_router
from .api.chat import router as chat_router
from .api.tasks import router as tasks_router
from .config import get_settings
from .middleware.cors import setup_cors

settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Todo Web App API",
    description="RESTful API for Phase 3 Todo Web Application with AI Chat",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup CORS middleware
setup_cors(app)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint - health check."""
    return {"status": "healthy", "message": "Todo API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
