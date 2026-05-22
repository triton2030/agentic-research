from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .cost_ledger import get_cost_snapshot


ENVELOPE_VERSION = 1
LARGE_REPLY_BYTES = 10_000
COUNTABLE_LIST_FIELDS = (
    "results",
    "files",
    "items",
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
)


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


def derive_next_step(
    result: Any,
    *,
    tool_name: str | None,
    args: dict[str, Any] | Any | None,
    corpus_root: str | None,
) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []
    args_dict = _as_args_dict(args)
    if result.get("error") == "index_warmup_required":
        steps = []
        if corpus_root:
            steps.append(
                {
                    "tool": "md_index",
                    "args": {"corpus": corpus_root, "dry_run": True},
                    "reason": "Preview embedding cost before warming the index.",
                }
            )
        if tool_name and args_dict:
            steps.append(
                {
                    "tool": tool_name,
                    "args": args_dict,
                    "reason": "Retry the original call once the index is warm.",
                }
            )
        return steps
    if result.get("error") == "confirm_required":
        if not tool_name:
            return []
        dry_args = dict(args_dict)
        dry_args.pop("confirm", None)
        dry_args["dry_run"] = True
        return [
            {
                "tool": tool_name,
                "args": dry_args,
                "reason": "Preview affected files or cost before mutation.",
            }
        ]
    if result.get("empty") is True and tool_name == "md_search":
        broader_args = dict(args_dict)
        broader_args["scope"] = "descriptions"
        return [
            {
                "tool": "md_search",
                "args": broader_args,
                "reason": "Retry with scope='descriptions' for higher-level matching.",
            }
        ]
    return []


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
    envelope = {
        "version": ENVELOPE_VERSION,
        "tool": tool_name,
        "corpus_root": corpus_root,
        "corpus_state": corpus_state,
        "lock": lock,
        "cost": get_cost_snapshot(),
        "size_estimate": compute_size_estimate(result),
        "next_step": derive_next_step(
            result,
            tool_name=tool_name,
            args=args_dict,
            corpus_root=corpus_root,
        ),
    }
    if result is None:
        return {"_envelope": envelope}
    if not isinstance(result, dict):
        return {"value": result, "_envelope": envelope}
    return {**result, "_envelope": envelope}
