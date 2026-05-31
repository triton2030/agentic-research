from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .cost_ledger import get_cost_snapshot
from .next_steps import LARGE_REPLY_BYTES, derive_next_step


ENVELOPE_VERSION = 1
COUNTABLE_LIST_FIELDS = (
    "results",
    "files",
    "items",
    "blocks",
    "pairs",
    "proposals",
    "sections",
    "concepts",
    "headings",
    "cycles",
    "orphans",
    "hubs",
    "anchors",
    "issues",
    "corpora",
    "unindexed_with_md",
    "must_read",
    "must_update",
    "cascade_breaks",
    "reference_breaks",
    "body_wikilink_refs",
    "body_markdown_refs",
    "modified",
    "changes",
    "topics",
    "candidates",
    "folder_breakdown",
    "scopes",
    "folders",
    "start_here",
)

# --- Agent-view projection -------------------------------------------------
# Internal/engine fields no agent consumes; dropped from every payload before
# it reaches the wire. NOT applied to `_envelope` (it is attached after wrap).
INTERNAL_FIELDS = frozenset({"rowid", "content_hash"})
# Path-valued keys to relativize against corpus_root for compactness.
PATH_STRING_FIELDS = frozenset({"path", "centroid_path"})
PATH_LIST_FIELDS = frozenset({"affected_files", "files_to_modify"})
# Anchor paths stay absolute (skills resolve other paths against them).
ANCHOR_PATH_FIELDS = frozenset({"root", "corpus_root", "corpus", "index_path", "scan", "repo_root"})


def _relativize(value: str, corpus_root: str) -> str:
    try:
        p = Path(value)
        if p.is_absolute():
            return str(p.relative_to(corpus_root))
    except (ValueError, TypeError, OSError):
        pass
    return value


def _project_node(node: Any, corpus_root: str | None) -> Any:
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key, val in node.items():
            if key in INTERNAL_FIELDS:
                continue
            if corpus_root and key in PATH_STRING_FIELDS and isinstance(val, str) and val:
                out[key] = _relativize(val, corpus_root)
            elif corpus_root and key in PATH_LIST_FIELDS and isinstance(val, list):
                out[key] = [
                    _relativize(v, corpus_root) if isinstance(v, str) else _project_node(v, corpus_root)
                    for v in val
                ]
            else:
                out[key] = _project_node(val, corpus_root)
        return out
    if isinstance(node, list):
        return [_project_node(item, corpus_root) for item in node]
    return node


def project_payload(result: Any, *, tool_name: str | None = None, corpus_root: str | None = None) -> Any:
    """Agent-view projection: drop internal fields, relativize non-anchor paths,
    collapse the legacy view-flag trio (map_only/content_included/expanded) into a
    single `expanded` bool + derived `view`. Pure dict->dict; runs inside wrap()
    before the size estimate, so size reflects the projected payload. Never sees
    `_envelope` (attached after wrap), so `recommended_action` is untouched."""
    if not isinstance(result, dict):
        return result
    projected = _project_node(result, corpus_root)
    if "map_only" in projected or "content_included" in projected or "expanded" in projected:
        expanded = bool(projected.get("expanded"))
        projected.pop("map_only", None)
        projected.pop("content_included", None)
        projected["expanded"] = expanded
        projected.setdefault("view", "expanded" if expanded else "map")
    return projected


def _as_args_dict(args: dict[str, Any] | Any | None) -> dict[str, Any]:
    if args is None:
        return {}
    if isinstance(args, dict):
        raw = dict(args)
    else:
        raw = vars(args)
    skip = {"subcommand", "json"}
    return {
        key: _jsonable(value)
        for key, value in raw.items()
        if not key.startswith("_") and key not in skip and value not in (None, False)
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return str(value)


def resolve_corpus_root(args: dict[str, Any] | Any | None) -> str | None:
    args_dict = _as_args_dict(args)
    candidate = args_dict.get("corpus") or args_dict.get("scan")
    if not isinstance(candidate, str) or not candidate:
        return None
    return str(Path(candidate).expanduser().resolve())


def compute_size_estimate(result: Any) -> dict[str, Any] | None:
    if not isinstance(result, dict):
        return None
    try:
        byte_count = len(json.dumps(result, ensure_ascii=False))
    except (TypeError, ValueError):
        byte_count = None
    items_returned = 0
    counted_fields = []
    for field in COUNTABLE_LIST_FIELDS:
        value = result.get(field)
        if isinstance(value, list) and value:
            items_returned += len(value)
            counted_fields.append({"field": field, "count": len(value)})
    estimate: dict[str, Any] = {
        "bytes": byte_count,
        "items_returned": items_returned,
    }
    if counted_fields:
        estimate["counted_fields"] = counted_fields
    if byte_count is not None and byte_count > LARGE_REPLY_BYTES:
        estimate["large_reply"] = True
    return estimate


def wrap(
    result: Any,
    *,
    tool_name: str | None,
    args: dict[str, Any] | Any | None,
    corpus_state: dict[str, Any] | None = None,
    lock: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if isinstance(result, dict) and "_envelope" in result:
        return result
    args_dict = _as_args_dict(args)
    corpus_root = resolve_corpus_root(args_dict)
    result = project_payload(result, tool_name=tool_name, corpus_root=corpus_root)
    size_estimate = compute_size_estimate(result)
    envelope = {
        "version": ENVELOPE_VERSION,
        "tool": tool_name,
        "corpus_root": corpus_root,
        "corpus_state": corpus_state,
        "lock": lock,
        "cost": get_cost_snapshot(),
        "size_estimate": size_estimate,
        "next_step": derive_next_step(
            result,
            tool_name=tool_name,
            args_dict=args_dict,
            corpus_root=corpus_root,
            corpus_state=corpus_state,
            lock=lock,
            size_estimate=size_estimate,
        ),
    }
    if result is None:
        return {"_envelope": envelope}
    if not isinstance(result, dict):
        return {"value": result, "_envelope": envelope}
    return {**result, "_envelope": envelope}
