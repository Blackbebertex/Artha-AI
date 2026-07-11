"""Vercel serverless entrypoint for ARTHA AI FastAPI backend."""
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent / "artha_backend"
sys.path.insert(0, str(_backend))

from main import app  # noqa: E402
