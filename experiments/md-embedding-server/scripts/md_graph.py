#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6",
# ]
# ///
"""Entry script for the repository-owned Markdown graph backend."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from navigator.graph import main

if __name__ == "__main__":
    raise SystemExit(main())
