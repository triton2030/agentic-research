"""Input preprocessing for `md extract` — stdin reading + search→map adapter.

Kept out of the handler so the handler can stay thin (≤30 lines per
architecture boundary). Reused by tests through `_adapt_stdin_map`.
"""

from __future__ import annotations

import json
import sys
from typing import Any


def process_extract_input(
    kwargs: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Return (kwargs_or_None, error_payload_or_None). Exactly one is None."""
    if kwargs.get("map_stdin") and kwargs.get("map_data"):
        return None, {
            "error": "usage_error",
            "detail": "--map-stdin and --map-data are mutually exclusive",
        }
    if kwargs.pop("map_stdin", False):
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            return None, {
                "error": "usage_error",
                "detail": f"--map-stdin received invalid JSON: {exc}",
            }
        kwargs["map_data"] = _adapt_stdin_map(data)
    elif not kwargs.get("map_data"):
        return None, {
            "error": "usage_error",
            "detail": "md extract requires --map-data or --map-stdin",
        }
    return kwargs, None


def _adapt_stdin_map(data: Any) -> Any:
    """Search payloads use `results`, not `files+headings`. Translate so
    `md search ... --json | md extract --map-stdin --headings ID1,ID2` works.
    Ls/toc/extract outputs are already map-shaped and pass through unchanged.
    """
    if not isinstance(data, dict):
        return data
    payload = dict(data)
    payload.pop("_envelope", None)
    if isinstance(payload.get("files"), list):
        return payload
    results = payload.get("results")
    if not isinstance(results, list):
        return payload
    files_by_id: dict[Any, dict[str, Any]] = {}
    for row in results:
        if not isinstance(row, dict):
            continue
        file_id = row.get("file_id")
        if file_id is None:
            continue
        entry = files_by_id.setdefault(
            file_id,
            {
                "id": file_id,
                "path": row.get("path") or row.get("relative_path", ""),
                "relative_path": row.get("relative_path", ""),
                "description": row.get("file_description", ""),
                "title": row.get("file_title", ""),
                "headings": [],
            },
        )
        section_id = row.get("section_id")
        if section_id is None:
            continue
        entry["headings"].append(
            {
                "id": str(section_id),
                "file_id": file_id,
                "line": row.get("start_line", 0),
                "level": row.get("level", 1),
                "text": row.get("heading_text") or row.get("heading_chain", ""),
                "tokens": row.get("token_count", 0),
            }
        )
    return {
        "root": payload.get("root", ""),
        "files": list(files_by_id.values()),
    }
