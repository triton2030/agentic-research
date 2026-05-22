from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable

from .result import ToolResult
from .transactions import (
    INTENT_KEYS,
    compute_fingerprint,
    create_transaction,
    verify_fingerprint,
    verify_and_consume_transaction,
)


def requires_transaction(
    *,
    tool_name: str,
    affected_files: Callable[[Any, dict[str, Any]], Iterable[str | Path]],
    intent_keys: Iterable[str] = INTENT_KEYS,
) -> Callable[[Callable[[Any], ToolResult]], Callable[[Any], ToolResult]]:
    def decorate(run_preview_or_execute: Callable[[Any], ToolResult]) -> Callable[[Any], ToolResult]:
        @wraps(run_preview_or_execute)
        def wrapper(args: Any) -> ToolResult:
            if getattr(args, "dry_run", False):
                result = run_preview_or_execute(args)
                payload = dict(result.payload or {})
                fingerprint, files = compute_fingerprint(affected_files(args, payload))
                txn = create_transaction(tool_name, vars(args), fingerprint, files)
                payload.update(
                    {
                        "dry_run": True,
                        "transaction_id": txn["id"],
                        "transaction_expires_at": txn["expires_at"],
                        "fingerprint": fingerprint,
                        "files": files,
                    }
                )
                return ToolResult(payload, result.exit_code)
            if getattr(args, "confirm", False):
                transaction_id = getattr(args, "transaction_id", None)
                if transaction_id:
                    verified = verify_and_consume_transaction(
                        transaction_id,
                        tool_name,
                        vars(args),
                        intent_keys=intent_keys,
                    )
                    if not verified["ok"]:
                        return ToolResult({"error": verified["reason"], **verified}, 1)
                    return run_preview_or_execute(args)
                fingerprint = getattr(args, "fingerprint", None)
                if fingerprint:
                    preview = run_preview_or_execute(args)
                    checked = verify_fingerprint(affected_files(args, preview.payload or {}), fingerprint)
                    if not checked["ok"]:
                        return ToolResult({"error": checked["reason"], **checked}, 1)
                    return preview
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

        return wrapper

    return decorate
