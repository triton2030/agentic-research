#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=1.26",
#   "sqlite-vec>=0.1.6",
#   "pyyaml>=6",
# ]
# ///
"""Entry script for the md_navigator package. See `navigator/cli.py`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from navigator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
