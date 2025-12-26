"""CORS middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import get_settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the application."""
    settings = get_settings()

    # Parse frontend URLs (comma-separated for multiple origins)
    origins = [url.strip() for url in settings.frontend_url.split(",") if url.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Required for cookies
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
