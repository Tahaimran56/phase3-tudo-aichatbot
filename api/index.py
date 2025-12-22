"""Vercel entry point for FastAPI backend.

This file is required by Vercel to deploy FastAPI applications.
The backend code is in api/src/ directory for simpler deployment.
"""

import sys
from pathlib import Path

# Add the src directory to Python path (it's in the same folder as this file)
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import the FastAPI app instance from src.main
from src.main import app

# Vercel will use this 'app' instance
__all__ = ["app"]
