from __future__ import annotations

from typing import Any, TypedDict


LARGE_REPLY_BYTES = 10_000


class NextStep(TypedDict):
    tool: str
    args: dict[str, Any]
    reason: str


def _narrow_for_large_reply(
    tool_name: str, args_dict: dict[str, Any], byte_count: int | None
) -> NextStep | None:
    size_note = f"Reply {byte_count} bytes > {LARGE_REPLY_BYTES}" if byte_count else "Reply large"

    if tool_name in {"md_search", "md_search_read"}:
        narrowed = {key: value for key, value in args_dict.items() if key != "top"}
        if tool_name == "md_search":
            narrowed["limit"] = min(int(args_dict.get("limit") or 10), 5)
            extra = "Also: --scope descriptions for higher-level summary."
        else:
            if args_dict.get("expanded"):
                narrowed.pop("expanded", None)
                extra = "Return the normal map first, then expand only chosen read_next targets."
            else:
                narrowed["limit"] = min(int(args_dict.get("limit") or 3), 1)
                extra = "Use read_next for one chosen section instead of widening the map."
        limit_note = f"Try --limit {narrowed['limit']}. " if "limit" in narrowed else ""
        return {
            "tool": tool_name,
            "args": narrowed,
            "reason": f"{size_note}. {limit_note}{extra}",
        }
    if tool_name == "md_repeated_concepts":
        narrowed_top = min(int(args_dict.get("top") or 30), 10)
        return {
            "tool": tool_name,
            "args": {**args_dict, "top": narrowed_top},
            "reason": (
                f"{size_note}. Try --top {narrowed_top} or add --path-include "
                "for the folder you actually need."
            ),
        }
    if tool_name == "md_overlaps":
        narrowed_top = min(int(args_dict.get("top") or 10), 10)
        return {
            "tool": tool_name,
            "args": {**args_dict, "top": narrowed_top},
            "reason": f"{size_note}. Try --top {narrowed_top}, raise --threshold, or add --path-include.",
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
    corpus_state: dict[str, Any] | None = None,
    lock: dict[str, Any] | None = None,
    size_estimate: dict[str, Any] | None = None,
) -> list[NextStep]:
    if not isinstance(result, dict):
        return []
    handlers = (
        _handle_dry_run_lock,
        _handle_index_warmup,
        _handle_nested_corpus,
        _handle_transaction_required,
        _handle_transaction_retry,
        _handle_empty_search,
        _handle_large_reply,
    )
    for handler in handlers:
        steps = handler(
            result,
            tool_name=tool_name,
            args_dict=args_dict,
            corpus_root=corpus_root,
            corpus_state=corpus_state,
            lock=lock,
            size_estimate=size_estimate,
        )
        if steps:
            return steps
    return []


def _handle_dry_run_lock(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
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
    return []


def _handle_index_warmup(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
    if result.get("error") == "index_warmup_required":
        steps: list[NextStep] = []
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
    return []


def _handle_nested_corpus(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
    if result.get("error") == "nested_corpus_refused":
        suggested_index = result.get("suggested_index_args")
        if isinstance(suggested_index, dict):
            index_args = dict(suggested_index)
            index_args.pop("confirm", None)
            index_args["dry_run"] = True
            return [
                {
                    "tool": "md_index",
                    "args": index_args,
                    "reason": "Use the existing parent corpus with this path scope, or pass --allow-nested-corpus deliberately.",
                }
            ]
        return []
    return []


def _handle_transaction_required(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
    if result.get("error") in {"confirm_required", "transaction_required"}:
        if not tool_name:
            return []
        recommended = _recommended_action_for(tool_name, corpus_state)
        if recommended is not None:
            return [recommended]
        dry_args = dict(args_dict)
        dry_args.pop("confirm", None)
        dry_args.pop("transaction_id", None)
        dry_args.pop("fingerprint", None)
        dry_args["dry_run"] = True
        return [
            {
                "tool": tool_name,
                "args": dry_args,
                "reason": "Run a dry-run first; confirm requires the returned transaction_id or fingerprint.",
            }
        ]
    return []


def _handle_transaction_retry(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
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
    return []


def _handle_empty_search(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
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


def _handle_large_reply(
    result: dict[str, Any],
    *,
    tool_name: str | None,
    args_dict: dict[str, Any],
    corpus_root: str | None,
    corpus_state: dict[str, Any] | None,
    lock: dict[str, Any] | None,
    size_estimate: dict[str, Any] | None,
) -> list[NextStep]:
    if (
        tool_name
        and isinstance(size_estimate, dict)
        and size_estimate.get("large_reply")
        and not result.get("error")
    ):
        byte_count = size_estimate.get("bytes")
        hint = _narrow_for_large_reply(
            tool_name,
            args_dict,
            byte_count if isinstance(byte_count, int) else None,
        )
        if hint is not None:
            return [hint]
    return []


def _recommended_action_for(
    tool_name: str,
    corpus_state: dict[str, Any] | None,
) -> NextStep | None:
    if not isinstance(corpus_state, dict):
        return None
    action = corpus_state.get("recommended_action")
    if not isinstance(action, dict) or action.get("tool") != tool_name:
        return None
    args = action.get("args")
    if not isinstance(args, dict):
        return None
    clean_args = dict(args)
    clean_args.pop("confirm", None)
    clean_args["dry_run"] = True
    return {
        "tool": tool_name,
        "args": clean_args,
        "reason": f"{action.get('reason') or 'Run the recommended dry-run first.'} Confirm only after the dry-run returns a transaction_id or fingerprint.",
    }
