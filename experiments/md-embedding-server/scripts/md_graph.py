#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6",
# ]
# ///
"""Entry script for the repository-owned Markdown graph backend.

LEGACY FALLBACK since 2026-05-22 — kept while skill fallback path exists.
Documented intent: docs/skills-semantic-equivalence.md ("legacy debug fallback").
Used for: skill-level cluster fallback (no `md cluster` yet), error-recipe
suggestions in navigator/cli.py, debug invocations.
Remove when: (1) `md cluster` subcommand exists, AND (2) skills doc no longer
references md_navigator.py/md_graph.py as fallback.
Prefer `md <subcommand>` (md-tools CLI installed globally) for everything else.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from navigator.graph import main

if __name__ == "__main__":
    raise SystemExit(main())
