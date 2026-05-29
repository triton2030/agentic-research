#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=1.26",
#   "sqlite-vec>=0.1.6",
#   "pyyaml>=6",
#   "pymorphy3>=2.0",
#   "networkx>=3.2",
#   "scipy>=1.11",
# ]
# ///
"""Entry script for the md_navigator package. See `navigator/cli.py`.

LEGACY FALLBACK since 2026-05-22 — kept while skill fallback path exists.
Documented intent: docs/skills-semantic-equivalence.md ("legacy debug fallback").
Used for: legacy direct-script recipes, error-recipe suggestions in
navigator/cli.py, and debug invocations.
Remove when skill docs and diagnostics no longer reference
md_navigator.py/md_graph.py as fallback. Public standalone topology is
`md cluster`.
Prefer `md <subcommand>` (md-tools CLI installed globally) for everything else.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from navigator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
