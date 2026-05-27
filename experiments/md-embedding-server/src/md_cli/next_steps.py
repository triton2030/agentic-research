from __future__ import annotations

from typing import Any


LARGE_REPLY_BYTES = 10_000


def _narrow_for_large_reply(
    tool_name: str, args_dict: dict[str, Any], byte_count: int | None
) -> dict[str, Any] | None:
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
    args_dict: dict[str, Any],
    corpus_root: str | None,
    lock: dict[str, Any] | None = None,
    size_estimate: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []
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
        suggested_index = result.get("suggested_index_args")
        if isinstance(suggested_index, dict):
            index_args = dict(suggested_index)
            index_args.pop("confirm", None)
            index_args["dry_run"] = True
            steps.append(
                {
                    "tool": "md_index",
                    "args": index_args,
                    "reason": "Preview embedding cost before warming the parent index for this path scope.",
                }
            )
        elif corpus_root:
            steps.append(
                {
                    "tool": "md_index",
                    "args": {"corpus": corpus_root, "dry_run": True},
                    "reason": "Preview embedding cost before warming the index.",
                }
            )
        if tool_name and args_dict:
            retry_args = dict(args_dict)
            suggested_retry = result.get("suggested_retry_args")
            if isinstance(suggested_retry, dict):
                retry_args.update(suggested_retry)
            steps.append(
                {
                    "tool": tool_name,
                    "args": retry_args,
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
