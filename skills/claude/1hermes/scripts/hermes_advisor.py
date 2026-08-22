#!/usr/bin/env python3
"""Run one bounded Hermes advisor turn and emit compact runtime evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import _advisor_contract as contract
import _ox_policy as ox
import _run_receipt as receipt_store
import _runtime_evidence as evidence
import _runtime_execution as execution

DEFAULT_MODEL = "moonshotai/kimi-k3"
DEFAULT_PROVIDER = "nous"
DEFAULT_REASONING = "medium"
DEFAULT_TOOLSETS = "file,web"
DEFAULT_MAX_TURNS = 2000
DEFAULT_TIMEOUT_SEC = 10800
SESSION_ID_RE = re.compile(r"^\s*session_id:\s*(\S+)\s*$", re.MULTILINE)
BENIGN_STDERR_PREFIXES = ("↻ Resumed session ",)

# Compatibility aliases for focused pure-function tests.
OX_ALPHA_MODEL = ox.MODEL
UsageKey = evidence.UsageKey
_ox_alpha_pricing_is_free = ox.pricing_is_free
_ox_alpha_catalog_url = ox.catalog_url
_ox_alpha_admission_error = ox.admission_error
_runtime_usage_evidence = evidence.runtime_usage_evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one quiet Hermes turn with session-backed runtime evidence."
    )
    parser.add_argument("--cwd", default=os.getcwd(), help="Project working directory")
    parser.add_argument("--model", help=f"Fresh-run model (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--provider", help=f"Fresh-run provider (default: {DEFAULT_PROVIDER})"
    )
    parser.add_argument(
        "--reasoning",
        choices=("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"),
        help=f"Fresh-run reasoning effort (default: {DEFAULT_REASONING})",
    )
    parser.add_argument("--resume", help="Resume an existing Hermes session")
    parser.add_argument(
        "--toolsets", default=DEFAULT_TOOLSETS, help="Comma-separated Hermes toolsets"
    )
    parser.add_argument(
        "--skill", action="append", default=[], help="Hermes skill to preload"
    )
    parser.add_argument(
        "--isolated",
        action="store_true",
        help="Skip project rules, identity, memory, and preloaded skills",
    )
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument(
        "--allow-write", action="store_true", help="Allow scoped project mutations"
    )
    parser.add_argument("--allow-execution-tools", action="store_true")
    parser.add_argument(
        "--worktree", action="store_true", help="Use a file-only Git worktree"
    )
    parser.add_argument("--allow-fallback", action="store_true")
    parser.add_argument("--hermes-bin", help="Hermes executable override")
    parser.add_argument("--expect-exact", help=argparse.SUPPRESS)
    return parser


_RECEIPT: dict[str, Any] | None = None


def _emit(payload: dict[str, Any]) -> None:
    if _RECEIPT:
        payload = {**payload, "run_dir": _RECEIPT["path"]}
        receipt_store.close_receipt(_RECEIPT, payload)
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _fail(message: str, *, exit_code: int = 2) -> int:
    _emit({"ok": False, "exit_code": exit_code, "error": message})
    return exit_code


def _resume_inputs(
    args: argparse.Namespace, hermes_bin: str, cwd: Path
) -> tuple[tuple[str, str, str] | None, dict[UsageKey, int] | None, str | None]:
    metadata, warning = evidence.read_metadata(hermes_bin, args.resume, cwd)
    runtime = evidence.resume_runtime(metadata)
    if warning or runtime is None:
        return (
            None,
            None,
            "--resume requires exact saved model, provider, and reasoning",
        )
    usage, warning = evidence.session_usage_snapshot(args.resume)
    if warning or usage is None:
        return (
            None,
            None,
            "--resume requires per-model usage evidence: " + (warning or "unknown"),
        )
    return runtime, usage, None


def _terminal_failure(
    *,
    exit_code: int,
    error: str,
    worktree: dict[str, Any] | None = None,
) -> int:
    _emit(
        {
            "ok": False,
            "exit_code": exit_code,
            "error": error,
            "worktree": worktree,
        }
    )
    return exit_code


def _run(
    args: argparse.Namespace,
    prompt: str,
    source_cwd: Path,
    toolsets: list[str],
    hermes_bin: str,
) -> int:
    resume_lock = None
    if args.resume:
        resume_lock, error = execution.acquire_resume_lock(args.resume)
        if error or resume_lock is None:
            return _fail(error or "session resume lock is unavailable")
    try:
        resumed = None
        usage_before: dict[UsageKey, int] = {}
        if args.resume:
            resumed, snapshot, error = _resume_inputs(args, hermes_bin, source_cwd)
            if error or snapshot is None:
                return _fail(error or "resume evidence is unavailable")
            usage_before = snapshot
        runtime = contract.requested_runtime(
            args,
            resumed,
            default_model=DEFAULT_MODEL,
            default_provider=DEFAULT_PROVIDER,
            default_reasoning=DEFAULT_REASONING,
        )
        error = contract.ox_gate(args, runtime)
        if error:
            return _fail(error)

        worktree = None
        run_cwd = source_cwd
        if args.worktree:
            worktree, error = execution.create_worktree(source_cwd)
            if error or worktree is None:
                return _fail(error or "worktree creation failed")
            run_cwd = Path(worktree["path"])

        command = contract.command(args, hermes_bin, prompt, toolsets, runtime)
        requested = {
            "model": runtime[0],
            "provider": runtime[1],
            "reasoning": runtime[2],
            "toolsets": ",".join(toolsets),
            "skills": args.skill,
            "isolated": args.isolated,
            "max_turns": args.max_turns,
            "resume": args.resume,
            "allow_write": args.allow_write,
            "allow_execution_tools": args.allow_execution_tools,
            "worktree": args.worktree,
            "allow_fallback": args.allow_fallback,
            "cwd": str(source_cwd),
            "run_cwd": str(run_cwd),
        }
        global _RECEIPT
        _RECEIPT = receipt_store.open_receipt(requested, prompt)

        run_env = os.environ.copy()
        read_only_root: tempfile.TemporaryDirectory[str] | None = None
        if args.allow_write:
            run_env["HERMES_WRITE_SAFE_ROOT"] = str(run_cwd)
        else:
            read_only_root = tempfile.TemporaryDirectory(prefix="1hermes-readonly-")
            run_env["HERMES_WRITE_SAFE_ROOT"] = read_only_root.name

        try:
            completed = execution.run_process_group(
                command, cwd=run_cwd, env=run_env, timeout=args.timeout_sec
            )
        except subprocess.TimeoutExpired:
            recovery = execution.recover_failed_worktree(worktree)
            return _terminal_failure(
                exit_code=124,
                error=f"Hermes run exceeded {args.timeout_sec}s",
                worktree=recovery,
            )
        except OSError as exc:
            recovery = execution.recover_failed_worktree(worktree)
            return _terminal_failure(
                exit_code=1,
                error=f"Hermes process failed to start: {exc}",
                worktree=recovery,
            )
        finally:
            if read_only_root:
                read_only_root.cleanup()
        response = completed.stdout.strip()
        session_match = SESSION_ID_RE.search(completed.stderr)
        session_id = session_match.group(1) if session_match else None
        stderr_lines = [
            line
            for line in completed.stderr.splitlines()
            if not SESSION_ID_RE.fullmatch(line)
            and not line.startswith(BENIGN_STDERR_PREFIXES)
        ]
        warnings = (
            ["\n".join(line for line in stderr_lines if line.strip())[:4000]]
            if any(line.strip() for line in stderr_lines)
            else []
        )
        if not session_id:
            warnings.append("Hermes did not return a session_id")
        if args.isolated:
            warnings.append(
                "isolated run: project rules, identity, memory and preloaded skills were skipped"
            )

        metadata: dict[str, Any] = {}
        if session_id:
            metadata, warning = evidence.read_metadata(hermes_bin, session_id, run_cwd)
            if warning:
                warnings.append(warning)
        response = evidence.final_assistant_content(metadata) or response
        resolved, session, usage = evidence.compact_metadata(metadata)
        if session_id and not session.get("id"):
            session["id"] = session_id
        runtime_warnings, runtime_mismatch, missing_runtime = contract.runtime_verdict(
            runtime, resolved, args.allow_fallback
        )
        warnings.extend(runtime_warnings)

        route = None
        route_mismatch = False
        ox_requested = runtime[0] == ox.MODEL
        if args.resume or ox_requested:
            usage_session = args.resume or session_id
            after, warning = (
                evidence.session_usage_snapshot(usage_session)
                if usage_session
                else (None, "session id is missing")
            )
            if warning or after is None:
                route_mismatch = True
                warnings.append(
                    "per-call runtime evidence unavailable: " + (warning or "unknown")
                )
            else:
                route, route_mismatch = evidence.runtime_usage_evidence(
                    usage_before,
                    after,
                    model=runtime[0],
                    provider=runtime[1] or "",
                    ox_alpha=ox_requested,
                )
                if route_mismatch:
                    warnings.append(
                        "per-call usage did not prove the exact requested route"
                    )

        cost_mismatch = False
        if ox_requested:
            cost_ok, cost_reason = evidence.ox_cost_verdict(usage)
            if not cost_ok:
                cost_mismatch = True
                warnings.append("Ox Alpha cost evidence rejected: " + cost_reason)

        response_mismatch = (
            args.expect_exact is not None and response != args.expect_exact
        )

        pre_commit_ok = bool(
            completed.returncode == 0
            and response
            and metadata
            and not missing_runtime
            and not runtime_mismatch
            and not route_mismatch
            and not cost_mismatch
            and not response_mismatch
        )
        worktree_evidence = worktree
        worktree_mismatch = False
        if args.worktree and pre_commit_ok:
            worktree_evidence, warning = execution.commit_and_verify_worktree(worktree)
            if warning:
                worktree_mismatch = True
                warnings.append("worktree not preserved: " + warning)
        elif args.worktree:
            worktree_mismatch = True
            worktree_evidence = execution.recover_failed_worktree(worktree)
            if worktree_evidence and worktree_evidence.get("recovery_required"):
                warnings.append(
                    "dirty worktree preserved for recovery after runtime failure"
                )
            else:
                warnings.append("empty failed worktree discarded")

        ok = pre_commit_ok and not worktree_mismatch
        wrapper_exit = 0 if ok else (completed.returncode or 1)
        _emit(
            {
                "ok": ok,
                "exit_code": wrapper_exit,
                "requested": requested,
                "resolved": resolved,
                "session": session,
                "usage": usage,
                "runtime_route": route,
                "resume_runtime": route if args.resume else None,
                "worktree": worktree_evidence,
                "warnings": warnings,
                "response": response,
            }
        )
        return wrapper_exit
    finally:
        execution.release_resume_lock(resume_lock)


def main() -> int:
    args = _parser().parse_args()
    prompt = sys.stdin.read().strip()
    if not prompt:
        return _fail("Hermes brief is empty; pass it on stdin")
    cwd, toolsets, error = contract.validate(args)
    if error or cwd is None:
        return _fail(error or "invalid arguments")
    hermes_bin = args.hermes_bin or shutil.which("hermes")
    if not hermes_bin:
        return _fail("hermes executable not found on PATH")
    try:
        return _run(args, prompt, cwd, toolsets, hermes_bin)
    except Exception as exc:  # noqa: BLE001
        # Вызывающий — агент, читающий stdout как JSON. Traceback для него
        # неотличим от поломки всей системы, а прогон мог быть уже оплачен:
        # любой исход обязан стать терминальным JSON и попасть в квитанцию.
        return _fail(f"{type(exc).__name__}: {exc}", exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main())
