"""Path-pattern filtering helpers shared by search / overlaps /
repeated-concepts.

Same fnmatch-style glob semantics across all callers: `*` matches any
characters including `/`, so `_ops/criteria/*` and `_ops/**` both
match the common include-this-subtree case. Patterns without glob
metachars fall back to substring containment so plain folder names
like `criteria` also work.

Single source of truth — extracted from `search.py` once the same
logic was needed in `overlaps.py` and `repeated_concepts.py`."""

from __future__ import annotations

import fnmatch
from typing import Any


def path_matches_any(rel_path: str, patterns: list[str]) -> bool:
    """fnmatch-style glob match against any of `patterns`. Empty list
    returns False. Patterns without glob metachars fall back to
    substring containment."""
    if not patterns:
        return False
    for pat in patterns:
        if fnmatch.fnmatch(rel_path, pat):
            return True
        if not any(c in pat for c in "*?["):
            if pat in rel_path:
                return True
    return False


def apply_path_filters(
    items: list[dict[str, Any]],
    include_patterns: list[str],
    exclude_patterns: list[str],
    path_key: str = "relative_path",
) -> list[dict[str, Any]]:
    """Filter `items` by `item[path_key]`. Include narrows; exclude
    drops. Both applied: include first, then exclude from matched set.
    Returns a new list. No-op (returns input list unchanged) when
    both pattern lists are empty."""
    if not include_patterns and not exclude_patterns:
        return items
    out: list[dict[str, Any]] = []
    for item in items:
        rel = item.get(path_key, "")
        if include_patterns and not path_matches_any(rel, include_patterns):
            continue
        if exclude_patterns and path_matches_any(rel, exclude_patterns):
            continue
        out.append(item)
    return out


def add_path_filter_args(parser, command_name: str) -> None:
    """Argparse helper: --path-include / --path-exclude with help text
    customised for the command. Repeatable; defaults to empty list."""
    parser.add_argument(
        "--path-include",
        action="append",
        default=[],
        metavar="GLOB",
        help=(
            f"Keep only {command_name} results whose relative path matches "
            f"GLOB (fnmatch syntax; bare names match as substring). "
            f"Repeatable."
        ),
    )
    parser.add_argument(
        "--path-exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help=(
            f"Drop {command_name} results whose relative path matches "
            f"GLOB. Repeatable. Applied after --path-include."
        ),
    )
