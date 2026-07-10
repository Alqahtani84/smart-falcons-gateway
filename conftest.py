"""Ensure the repo root is importable so `ml` / `scripts` resolve during tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
