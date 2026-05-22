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
from pathlib import Path
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


def normalize_path_filter_patterns(
    patterns: list[str] | None,
    corpus_root: Path,
) -> list[str]:
    """Convert absolute patterns under `corpus_root` to relative patterns.

    Path filters are evaluated against stored `relative_path` values. MCP
    callers often have absolute paths handy, so accept both forms without
    changing the core matching contract.
    """
    if not patterns:
        return []
    root = str(corpus_root.resolve())
    prefix = root + "/"
    out: list[str] = []
    for pattern in patterns:
        raw = str(pattern).strip()
        if not raw:
            continue
        if raw.startswith(prefix):
            raw = raw[len(prefix) :]
        elif raw.startswith("./"):
            raw = raw[2:]
        out.append(raw)
    return out


def apply_path_filters_to_map(
    map_data: dict[str, Any],
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> dict[str, Any]:
    """Return a shallow map copy with `files` narrowed by path filters."""
    files = apply_path_filters(
        list(map_data.get("files") or []),
        include_patterns,
        exclude_patterns,
    )
    scoped = dict(map_data)
    scoped["files"] = files
    scoped["file_count"] = len(files)
    scoped["description_gap_count"] = sum(1 for f in files if not f.get("description"))
    scoped["heading_count"] = sum(int(f.get("heading_count") or 0) for f in files)
    return scoped


def sqlite_path_filter_sql(
    column: str,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> tuple[str, list[str]]:
    """Build a SQLite WHERE fragment matching `path_matches_any` semantics.

    Glob patterns use SQLite GLOB. Plain patterns use substring matching via
    instr() to mirror the helper's bare-name fallback.
    """

    def _condition(pattern: str) -> tuple[str, str]:
        if any(ch in pattern for ch in "*?["):
            return f"{column} GLOB ?", pattern
        return f"instr({column}, ?) > 0", pattern

    clauses: list[str] = []
    params: list[str] = []
    if include_patterns:
        include_parts = []
        for pattern in include_patterns:
            clause, param = _condition(pattern)
            include_parts.append(clause)
            params.append(param)
        clauses.append("(" + " OR ".join(include_parts) + ")")
    for pattern in exclude_patterns:
        clause, param = _condition(pattern)
        clauses.append(f"NOT ({clause})")
        params.append(param)
    if not clauses:
        return "", []
    return " AND " + " AND ".join(clauses), params


def add_path_filter_args(
    parser,
    command_name: str,
    *,
    with_no_default_excludes: bool = False,
) -> None:
    """Argparse helper: --path-include / --path-exclude with help text
    customised for the command. Repeatable; defaults to empty list.

    `with_no_default_excludes=True` also registers `--no-default-excludes`
    (currently used by graph commands to opt out of the built-in
    hidden/tooling-directory skip).
    """
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
    if with_no_default_excludes:
        parser.add_argument(
            "--no-default-excludes",
            action="store_true",
            help=(
                "Disable built-in hidden / tooling directory skip "
                "(.git, .venv, .md-navigator, node_modules, _archive, "
                "runs, ...). Use only when you really need to walk them."
            ),
        )
