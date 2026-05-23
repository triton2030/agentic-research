from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

from md_cli.catalog import get_tool
from md_cli.result import ToolResult
from md_cli.transactions import (
    claim_transaction,
    compute_fingerprint,
    create_transaction,
    finish_transaction_claim,
    restore_transaction_claim,
    verify_fingerprint,
)


MUTATING_TOOLS = {"md_init", "md_strip", "md_index", "md_profile_sections"}


TRANSACTION_HINTS = {
    "transaction_not_found": "Transaction id not recognized. Run --dry-run to get a fresh id.",
    "expired": "Transaction expired (TTL 5 min). Re-run --dry-run.",
    "args_mismatch": "Args differ between dry-run and confirm. Re-run --dry-run with the final args.",
    "drift_detected": "Affected files changed since dry-run; re-run --dry-run.",
    "affected_files_mismatch": "Affected file set changed; re-run --dry-run.",
    "tool_mismatch": "Transaction was created for a different tool.",
    "cwd_mismatch": "Transaction was created from a different cwd.",
    "internal_error": "Internal failure during consume; retry or check logs.",
}


def run_tool(tool_id: str, args: Any) -> ToolResult:
    spec = get_tool(tool_id)
    if spec is None:
        return ToolResult({"error": "unknown_tool", "tool": tool_id}, 2)
    target = spec.workflow_function or spec.library_function
    if target is None:
        return ToolResult({"error": "missing_target", "tool": tool_id}, 3)
    func = _load_target(target)
    kwargs = _kwargs(args)
    if _requires_transaction(tool_id, kwargs):
        return _run_mutating(tool_id, func, args, kwargs)
    return _call(func, kwargs)


def _load_target(target: str) -> Callable[..., dict[str, Any]]:
    module_name, attr = target.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def _kwargs(args: Any) -> dict[str, Any]:
    return {
        key: value
        for key, value in vars(args).items()
        if not key.startswith("_") and key not in {"subcommand", "json"}
    }


def _call(func: Callable[..., dict[str, Any]], kwargs: dict[str, Any]) -> ToolResult:
    try:
        payload = func(**kwargs)
    except FileNotFoundError as exc:
        return ToolResult({"error": "path_not_found", "detail": str(exc)}, 2)
    except PermissionError as exc:
        return ToolResult({"error": "permission_denied", "detail": str(exc)}, 2)
    except TypeError as exc:
        return ToolResult({"error": "usage_error", "detail": str(exc)}, 2)
    except Exception as exc:
        # Catch-all fence: any unhandled exception (URLError, socket.timeout,
        # nx.NetworkXError, etc.) becomes an envelope error instead of a raw
        # traceback. KeyboardInterrupt and SystemExit inherit from BaseException
        # and propagate normally.
        return ToolResult(
            {
                "error": "internal_error",
                "exception": type(exc).__name__,
                "detail": str(exc),
            },
            3,
        )
    if payload is None:
        payload = {}
    payload = dict(payload)
    code = int(payload.pop("_exit_code", 0))
    return ToolResult(payload, code)


def _requires_transaction(tool_id: str, kwargs: dict[str, Any]) -> bool:
    if tool_id not in MUTATING_TOOLS:
        return False
    if tool_id == "md_profile_sections":
        mode = kwargs.get("mode") or "heuristic"
        return bool(kwargs.get("dry_run") or kwargs.get("confirm") or mode in {"llm", "auto"})
    return True


def _run_mutating(
    tool_id: str,
    func: Callable[..., dict[str, Any]],
    args: Any,
    kwargs: dict[str, Any],
) -> ToolResult:
    if kwargs.get("dry_run"):
        result = _call(func, {**kwargs, "dry_run": True, "confirm": False})
        if result.exit_code != 0:
            return result
        payload = dict(result.payload or {})
        fingerprint, files = compute_fingerprint(_affected_files(payload))
        txn = create_transaction(tool_id, vars(args), fingerprint, files)
        # `files` stays in payload — it's the dry-run preview data (which files
        # will be touched). transaction_id / expires_at / fingerprint move to
        # `_envelope.lock` so agents read one canonical location for the
        # session-bound mutation handle.
        payload["files"] = files
        lock = {
            "transaction_id": txn["id"],
            "expires_at": txn["expires_at"],
            "fingerprint": fingerprint,
        }
        return ToolResult(payload, result.exit_code, lock=lock)

    if kwargs.get("confirm"):
        transaction_id = kwargs.get("transaction_id")
        if transaction_id:
            preview = _call(func, {**kwargs, "dry_run": True, "confirm": False})
            if preview.exit_code != 0:
                return preview
            verified = claim_transaction(
                transaction_id,
                tool_id,
                vars(args),
                confirm_files=_affected_files(preview.payload or {}),
            )
            if not verified["ok"]:
                return ToolResult(_transaction_error_payload(verified), 1)
            result = _call(func, {**kwargs, "dry_run": False, "confirm": True})
            if result.exit_code == 0:
                finish_transaction_claim(verified["claim_path"])
            else:
                restore_transaction_claim(verified["claim_path"])
            return result
        fingerprint = kwargs.get("fingerprint")
        if fingerprint:
            preview = _call(func, {**kwargs, "dry_run": True, "confirm": False})
            checked = verify_fingerprint(_affected_files(preview.payload or {}), fingerprint)
            if not checked["ok"]:
                return ToolResult(_transaction_error_payload(checked), 1)
            return _call(func, {**kwargs, "dry_run": False, "confirm": True})
        return ToolResult(
            {
                "error": "transaction_required",
                "reason": "Confirm requires --transaction-id or --fingerprint.",
            },
            1,
        )

    return ToolResult(
        {
            "error": "confirm_required",
            "reason": "Run with --dry-run first to obtain transaction_id.",
        },
        1,
    )


def _transaction_error_payload(verified: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": verified["reason"], **verified}
    hint = TRANSACTION_HINTS.get(verified["reason"])
    if hint and "hint" not in payload:
        payload["hint"] = hint
    return payload


def _affected_files(payload: dict[str, Any]) -> list[str]:
    candidates = (
        payload.get("affected_files")
        or payload.get("files_to_modify")
        or payload.get("modified")
        or payload.get("files")
        or []
    )
    files: list[str] = []
    for item in candidates:
        if isinstance(item, dict) and "path" in item:
            files.append(str(item["path"]))
        elif isinstance(item, (str, Path)):
            files.append(str(item))
    return files
