"""Vercel entry point for FastAPI backend.

This file is required by Vercel to deploy FastAPI applications.
The backend code is in api/src/ directory for simpler deployment.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Also add to PYTHONPATH for safety
os.environ['PYTHONPATH'] = str(src_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')

# Import the FastAPI app instance
try:
    from main import app
except ImportError:
    # Fallback to explicit path import
    from src.main import app

# Vercel will use this 'app' instance
__all__ = ["app"]
