"""Vercel entry point for FastAPI backend.

This file is required by Vercel to deploy FastAPI applications.
It imports and exposes the FastAPI app instance from the backend.
"""

import sys
import os
from pathlib import Path

# Get the root directory (where this file's parent is)
root_dir = Path(__file__).parent.parent
backend_src = root_dir / "backend" / "src"

# Add backend/src to Python path
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

# Also add backend to path for relative imports
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Debug: Print paths (will show in Vercel logs)
print(f"Root dir: {root_dir}")
print(f"Backend src: {backend_src}")
print(f"Backend src exists: {backend_src.exists()}")
print(f"Python path: {sys.path[:3]}")

try:
    # Import the FastAPI app instance
    from src.main import app
    print("Successfully imported app from src.main")
except ImportError as e:
    print(f"Failed to import from src.main: {e}")
    # Fallback: try direct import
    try:
        from main import app
        print("Successfully imported app from main")
    except ImportError as e2:
        print(f"Failed to import from main: {e2}")
        raise

# Vercel will use this 'app' instance
__all__ = ["app"]
