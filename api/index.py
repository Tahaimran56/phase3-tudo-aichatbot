"""Vercel entry point for FastAPI backend.

This file is required by Vercel to deploy FastAPI applications.
It imports and exposes the FastAPI app instance from the backend.
"""

import sys
from pathlib import Path

# Add backend/src to Python path so we can import the app
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Import the FastAPI app instance
from main import app

# Vercel will use this 'app' instance
__all__ = ["app"]
