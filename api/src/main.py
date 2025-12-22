"""FastAPI application entry point."""

from fastapi import FastAPI

from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
from .config import get_settings
from .middleware.cors import setup_cors

settings = get_settings()

app = FastAPI(
    title="Todo Web App API",
    description="RESTful API for the Phase 2 Todo Web Application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS middleware
setup_cors(app)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint - health check."""
    return {"status": "healthy", "message": "Todo API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
