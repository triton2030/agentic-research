"""Probe для finding #18 (2026-05-22): md transaction sentinel marks
consumed before actual apply.

Reproduced path: `_generic._run_mutating` calls `_call(func, confirm=True)`
which is wrapped by the exception fence at `_generic._call` (catches
RuntimeError/URLError/etc. into ToolResult(error, exit_code=3)). The
next line then calls `finish_transaction_claim(...)` UNCONDITIONALLY,
so the .claim file is unlinked even when the mutation never ran.
Result: agent sees an error but the transaction is consumed; retry with
the same transaction_id fails with `transaction_not_found`.

Test asserts the correct post-fix behavior: on `_call` failure, the
claim is restored back to `.json` so the agent can retry without first
running `--dry-run` again.
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import Any

import pytest

from md_cli.handlers._generic import _run_mutating
from md_cli.transactions import transaction_path


@pytest.fixture
def isolated_cache(tmp_path, monkeypatch):
    """Redirect transaction state to a tmp dir so the test is hermetic
    and parallel-safe."""
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path))
    return tmp_path


def _make_args(**overrides) -> Namespace:
    base = {
        "dry_run": False,
        "confirm": False,
        "transaction_id": None,
        "fingerprint": None,
        "json": True,
        "subcommand": "md_init",
        "path": "dummy",
    }
    base.update(overrides)
    return Namespace(**base)


def _kwargs_from(args: Namespace) -> dict[str, Any]:
    return {
        k: v
        for k, v in vars(args).items()
        if not k.startswith("_") and k not in {"subcommand", "json"}
    }


def test_failed_confirm_restores_transaction_for_retry(isolated_cache):
    """Finding #18: on confirm failure, transaction must remain available.

    Failure-mode assertion: after `--confirm` triggers an exception inside
    the mutation function, the transaction file at `<txn>.json` must
    still exist (restored from `<txn>.claim`) so the agent can re-issue
    `--confirm --transaction-id <same id>` without first re-running
    `--dry-run`.
    """
    call_log: list[dict[str, Any]] = []

    def flaky(**kwargs: Any) -> dict[str, Any]:
        call_log.append({k: v for k, v in kwargs.items() if k in {"dry_run", "confirm"}})
        if kwargs.get("dry_run"):
            return {"files": ["dummy.md"], "_exit_code": 0}
        raise RuntimeError("simulated mutation failure after claim")

    dry_args = _make_args(dry_run=True)
    dry_result = _run_mutating("md_init", flaky, dry_args, _kwargs_from(dry_args))

    assert dry_result.lock is not None, "dry-run must emit envelope lock"
    txn_id = dry_result.lock["transaction_id"]
    assert transaction_path(txn_id).exists(), "transaction file missing after dry-run"

    confirm_args = _make_args(confirm=True, transaction_id=txn_id)
    confirm_result = _run_mutating(
        "md_init", flaky, confirm_args, _kwargs_from(confirm_args)
    )

    assert confirm_result.exit_code != 0, (
        "exception in mutation must produce non-zero exit, "
        f"got {confirm_result.exit_code} with payload {confirm_result.payload}"
    )
    payload = confirm_result.payload or {}
    assert payload.get("error") == "internal_error", (
        f"expected internal_error envelope, got {payload!r}"
    )

    txn_path = transaction_path(txn_id)
    assert txn_path.exists(), (
        "Finding #18: transaction was consumed even though mutation failed. "
        "After fix: failed _call must restore .claim back to .json so the "
        "agent can retry with the same transaction_id."
    )


def test_successful_confirm_finishes_transaction(isolated_cache):
    """Counter-test: when mutation succeeds, the transaction file must
    be gone (claim finished). Guards against an overcorrection where the
    fix from the test above also stops finishing successful claims."""
    def happy(**kwargs: Any) -> dict[str, Any]:
        if kwargs.get("dry_run"):
            return {"files": ["dummy.md"], "_exit_code": 0}
        return {"modified": ["dummy.md"], "_exit_code": 0}

    dry_args = _make_args(dry_run=True)
    dry_result = _run_mutating("md_init", happy, dry_args, _kwargs_from(dry_args))
    txn_id = dry_result.lock["transaction_id"]

    confirm_args = _make_args(confirm=True, transaction_id=txn_id)
    confirm_result = _run_mutating(
        "md_init", happy, confirm_args, _kwargs_from(confirm_args)
    )

    assert confirm_result.exit_code == 0, (
        f"happy path must return 0, got {confirm_result.exit_code} "
        f"with {confirm_result.payload}"
    )
    txn_path = transaction_path(txn_id)
    assert not txn_path.exists(), (
        "successful confirm must consume the transaction (no .json file left)"
    )
    claim_path = txn_path.with_suffix(".claim")
    assert not claim_path.exists(), (
        "successful confirm must finish the claim (no .claim file left)"
    )
