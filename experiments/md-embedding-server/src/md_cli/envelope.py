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


def _narrow_for_large_reply(
    tool_name: str, args_dict: dict[str, Any], byte_count: int | None
) -> dict[str, Any] | None:
    """Per-tool narrowing suggestion when reply exceeds LARGE_REPLY_BYTES.

    Returns one `next_step` dict the agent can follow verbatim to cut
    output to a manageable size. Returns None for tools that have no
    natural narrowing axis — they fall back to the generic empty
    `next_step` and the size_estimate alone signals the issue.
    """
    size_note = f"Reply {byte_count} bytes > {LARGE_REPLY_BYTES}" if byte_count else "Reply large"

    if tool_name in {"md_search", "md_search_read"}:
        narrowed = {key: value for key, value in args_dict.items() if key != "top"}
        if tool_name == "md_search":
            narrowed["limit"] = min(int(args_dict.get("limit") or 10), 5)
            extra = "Also: --scope descriptions for higher-level summary."
        else:
            narrowed["limit"] = min(int(args_dict.get("limit") or 3), 1)
            narrowed["token_budget"] = min(int(args_dict.get("token_budget") or 1200), 1200)
            extra = "Also: --token-budget 1200 for a bounded body payload."
        return {
            "tool": tool_name,
            "args": narrowed,
            "reason": f"{size_note}. Try --limit {narrowed['limit']}. {extra}",
        }
    if tool_name == "md_repeated_concepts":
        return {
            "tool": tool_name,
            "args": {**args_dict, "top": 10},
            "reason": (
                f"{size_note}. Try --top 10 or --path-include 'subpath/*' "
                f"to narrow the report scope."
            ),
        }
    if tool_name == "md_overlaps":
        return {
            "tool": tool_name,
            "args": {**args_dict, "top": 20},
            "reason": f"{size_note}. Try --top 20 or raise --threshold.",
        }
    if tool_name == "md_audit":
        return {
            "tool": tool_name,
            "args": dict(args_dict),
            "reason": (
                f"{size_note}. Try --path-include 'subpath/*' to narrow the audit scope."
            ),
        }
    return None


def derive_next_step(
    result: Any,
    *,
    tool_name: str | None,
    args: dict[str, Any] | Any | None,
    corpus_root: str | None,
    lock: dict[str, Any] | None = None,
    size_estimate: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []
    args_dict = _as_args_dict(args)
    if result.get("dry_run") is True and lock and lock.get("transaction_id") and tool_name:
        confirm_args = dict(args_dict)
        confirm_args.pop("dry_run", None)
        confirm_args["confirm"] = True
        confirm_args["transaction_id"] = lock["transaction_id"]
        return [
            {
                "tool": tool_name,
                "args": confirm_args,
                "reason": "Apply the dry-run plan with the matching transaction_id.",
            }
        ]
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
    if result.get("error") in {"transaction_not_found", "expired"}:
        if not tool_name:
            return []
        dry_args = dict(args_dict)
        dry_args.pop("confirm", None)
        dry_args.pop("transaction_id", None)
        dry_args.pop("fingerprint", None)
        dry_args["dry_run"] = True
        return [
            {
                "tool": tool_name,
                "args": dry_args,
                "reason": "Re-run --dry-run to obtain a fresh transaction_id.",
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
    if (
        tool_name
        and isinstance(size_estimate, dict)
        and size_estimate.get("large_reply")
        and not result.get("error")
    ):
        hint = _narrow_for_large_reply(tool_name, args_dict, size_estimate.get("bytes"))
        if hint is not None:
            return [hint]
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
            args=args_dict,
            corpus_root=corpus_root,
            lock=lock,
            size_estimate=size_estimate,
        ),
    }
    if result is None:
        return {"_envelope": envelope}
    if not isinstance(result, dict):
        return {"value": result, "_envelope": envelope}
    return {**result, "_envelope": envelope}
