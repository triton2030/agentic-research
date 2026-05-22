from __future__ import annotations

import json
import re
import shlex
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
    skip = {"subcommand", "json", "brief"}
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
    lock: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []
    args_dict = _as_args_dict(args)
    if (
        result.get("dry_run") is True
        and lock
        and lock.get("transaction_id")
        and tool_name
    ):
        confirm_args = dict(args_dict)
        confirm_args.pop("dry_run", None)
        confirm_args["confirm"] = True
        confirm_args["transaction_id"] = lock["transaction_id"]
        return [
            {
                "tool": tool_name,
                "args": confirm_args,
                "reason": "Apply the dry-run plan with the matching transaction_id.",
                "command": _build_command(tool_name, confirm_args),
            }
        ]
    if (
        tool_name == "md_search"
        and isinstance(result.get("results"), list)
        and result["results"]
    ):
        top_ids = [
            str(row.get("section_id"))
            for row in result["results"][:3]
            if row.get("section_id") is not None
        ]
        if top_ids:
            extract_args = {
                "map_stdin": True,
                "headings": ",".join(top_ids),
                "extract": True,
            }
            search_cmd = _build_command("md_search", args_dict)
            extract_cmd = _build_command("md_extract", extract_args)
            pipe_cmd = (
                f"{search_cmd} | {extract_cmd}"
                if search_cmd and extract_cmd
                else None
            )
            return [
                {
                    "tool": "md_extract",
                    "args": extract_args,
                    "reason": "Read top results in one pipe via md_extract --map-stdin.",
                    "command": pipe_cmd,
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
    if result.get("error") == "transaction_consumed":
        steps: list[dict[str, Any]] = []
        if corpus_root:
            steps.append(
                {
                    "tool": "md_status",
                    "args": {"corpus": corpus_root},
                    "reason": "Verify that the prior --confirm already applied the mutation.",
                }
            )
        return steps
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


_CONTROL_KEYS_FOR_CMD = {"subcommand", "json", "brief"}


def _build_command(tool_name: str, args_dict: dict[str, Any]) -> str | None:
    """Reconstruct a copy-pasteable shell command from a tool name + args dict.

    Used by `next_step[].command` so agents can run the suggested next step
    without rewriting args. Returns None when the tool is unknown.
    """
    # Local import keeps catalog out of envelope's import graph at module load.
    from .catalog import TOOLS_BY_ID

    spec = TOOLS_BY_ID.get(tool_name)
    if spec is None:
        return None
    remaining = dict(args_dict)
    parts: list[str] = ["md", spec.cli_name]
    for key in _positional_keys(spec.cli_signature):
        value = remaining.pop(key, None)
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            parts.extend(shlex.quote(str(item)) for item in value)
        else:
            parts.append(shlex.quote(str(value)))
    for key, value in remaining.items():
        if key in _CONTROL_KEYS_FOR_CMD or key.startswith("_"):
            continue
        if value in (None, False, "", []):
            continue
        flag = "--" + key.replace("_", "-")
        if isinstance(value, bool) and value:
            parts.append(flag)
        elif isinstance(value, list):
            for item in value:
                parts.extend([flag, shlex.quote(str(item))])
        else:
            parts.extend([flag, shlex.quote(str(value))])
    if "--json" not in parts:
        parts.append("--json")
    return " ".join(parts)


def _positional_keys(cli_signature: str) -> list[str]:
    """Extract positional arg names (ALL_CAPS tokens before first --flag)."""
    body = cli_signature.removeprefix("md ").split(maxsplit=1)
    if len(body) < 2:
        return []
    raw_tokens = re.findall(r"\[[^\]]+\]|\S+", body[1])
    result: list[str] = []
    for raw in raw_tokens:
        token = raw[1:-1] if raw.startswith("[") and raw.endswith("]") else raw
        token = token.strip()
        if not token:
            continue
        if token.startswith("--"):
            # Positional tokens always precede flags in our signatures.
            continue
        if token.upper() == token and token.isidentifier():
            result.append(token.lower())
    return result


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
            lock=lock,
        ),
    }
    if result is None:
        return {"_envelope": envelope}
    if not isinstance(result, dict):
        return {"value": result, "_envelope": envelope}
    return {**result, "_envelope": envelope}
