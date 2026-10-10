"""Pytest configuration: make ``src/`` importable without installing the package.

The project runs as ``PYTHONPATH=src python3 -m aloy.<module>`` (see README), so
tests mirror that by putting ``src`` on ``sys.path`` here.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
