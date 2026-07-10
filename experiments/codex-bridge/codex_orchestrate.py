#!/usr/bin/env python3
"""codex-bridge orchestrator — guarded shared-worktree Codex workers."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cbcommon import scrub_billing_env
from codex_defaults import (
    BRIDGE_THREAD_EPHEMERAL,
    DEFAULT_CODEX_EFFORT,
    DEFAULT_CODEX_MODEL,
    REASONING_EFFORTS,
    WORKER_APPROVAL_MODE,
    WORKER_SANDBOX,
    resolve_codex_bin,
)
from codex_orchestrate_contract import (
    TaskSpec,
    UsageError,
    codex_status_value,
    dirty_overlaps,
    normalize_tasks,
    worker_status_from_codex_status,
)
from codex_orchestrate_state import (
    GitSnapshot,
    append_event,
    append_heartbeat,
    append_jsonl,
    capture_git_snapshot,
    compare_scope,
    is_scope_noise,
    prepare_run_dir,
    utc_now,
    write_json,
)


def _safe_print(message: str, *, stream: Any = None) -> None:
    # Прогресс и финальный дамп — телеметрия поверх канонического результата
    # на диске: закрытый пайп (| head, оборванный терминал) не должен ронять
    # флот и подменять готовые записи воркеров exception-записями.
    try:
        print(message, file=stream if stream is not None else sys.stderr)
    except OSError:
        pass


def _files_constraint(files: tuple[str, ...]) -> str:
    joined = ", ".join(files)
    return (
        f"Тебе разрешено создавать и редактировать ТОЛЬКО эти файлы: {joined}. "
        "Не трогай никакие другие файлы. Если задача требует иного — опиши это "
        "в ответе, но не делай.\n\n"
    )


async def _run_one(codex, sem, task: TaskSpec, defaults: dict[str, Any]) -> dict[str, Any]:
    from openai_codex import ApprovalMode, Sandbox  # импорт после scrub_billing_env
    from openai_codex.generated.v2_all import ReasoningEffort

    prompt = _files_constraint(task.files) + task.prompt
    run_dir: Path = defaults["run_dir"]
    effort = ReasoningEffort(defaults["effort"])

    async with sem:
        t0 = time.monotonic()
        append_event(run_dir, "worker_start", id=task.id)
        try:
            thread = await codex.thread_start(
                cwd=defaults["cwd"],
                sandbox=Sandbox.workspace_write,
                approval_mode=ApprovalMode.auto_review,
                model=defaults["model"],
                ephemeral=BRIDGE_THREAD_EPHEMERAL,
            )
            result = await thread.run(
                prompt,
                approval_mode=ApprovalMode.auto_review,
                effort=effort,
                model=defaults["model"],
                sandbox=Sandbox.workspace_write,
            )
            duration_ms = int((time.monotonic() - t0) * 1000)
            codex_status = codex_status_value(getattr(result, "status", ""))
            worker_status = worker_status_from_codex_status(codex_status, result.error)
            worker_ok = worker_status == "completed"
            _safe_print(
                f"[orch] {'✓' if worker_ok else '✗'} {task.id} ({duration_ms}мс)"
                + ("" if worker_ok else f" — {result.error}")
            )
            record = {
                "id": task.id,
                "worker_status": worker_status,
                "codex_status": codex_status,
                "error": str(result.error) if result.error else None,
                "response": result.final_response,
                "duration_ms": duration_ms,
                "usage": str(getattr(result, "usage", None)),
            }
        except Exception as exc:  # noqa: BLE001 — одна упавшая задача не валит флот
            duration_ms = int((time.monotonic() - t0) * 1000)
            _safe_print(f"[orch] ✗ {task.id} — исключение: {exc}")
            record = {
                "id": task.id,
                "worker_status": "exception",
                "codex_status": "exception",
                "error": str(exc),
                "response": None,
                "duration_ms": duration_ms,
                "usage": None,
            }

        append_event(
            run_dir,
            "worker_done",
            id=task.id,
            worker_status=record["worker_status"],
            duration_ms=record["duration_ms"],
        )
        append_jsonl(run_dir / "results.jsonl", record)
        defaults["progress"]["completed"] += 1
        return record


async def _heartbeat_loop(
    run_dir: Path,
    heartbeat_sec: int,
    started_monotonic: float,
    progress: dict[str, int],
) -> None:
    try:
        while True:
            await asyncio.sleep(heartbeat_sec)
            append_heartbeat(
                run_dir,
                started_monotonic,
                completed=progress["completed"],
                total=progress["total"],
            )
    except asyncio.CancelledError:
        return


async def _run_fleet(
    tasks: list[TaskSpec],
    defaults: dict[str, Any],
    concurrency: int,
    heartbeat_sec: int,
) -> list[dict[str, Any]]:
    from openai_codex import AsyncCodex, CodexConfig

    sem = asyncio.Semaphore(concurrency)
    defaults["progress"] = {"completed": 0, "total": len(tasks)}
    heartbeat_task: asyncio.Task[None] | None = None
    if heartbeat_sec > 0:
        heartbeat_task = asyncio.create_task(
            _heartbeat_loop(defaults["run_dir"], heartbeat_sec, time.monotonic(), defaults["progress"])
        )
    try:
        async with AsyncCodex(
            CodexConfig(cwd=defaults["cwd"], codex_bin=resolve_codex_bin())
        ) as codex:
            return await asyncio.gather(*(_run_one(codex, sem, task, defaults) for task in tasks))
    finally:
        if heartbeat_task is not None:
            heartbeat_task.cancel()
            await asyncio.gather(heartbeat_task, return_exceptions=True)


def run_verification(commands: list[str], project: Path, run_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    if not commands:
        return "not_requested", []

    results: list[dict[str, Any]] = []
    status = "passed"
    for index, command in enumerate(commands, start=1):
        started = time.monotonic()
        append_event(run_dir, "verify_start", index=index, command=command)
        proc = subprocess.run(
            command,
            cwd=project,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        item = {
            "command": command,
            "exit_code": proc.returncode,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        }
        results.append(item)
        append_event(run_dir, "verify_done", index=index, exit_code=proc.returncode)
        if proc.returncode != 0:
            status = "failed"
            break
    return status, results


def build_manifest(
    run_id: str,
    run_dir: Path,
    project: Path,
    tasks: list[TaskSpec],
    allowlist: set[str],
    initial_git: GitSnapshot,
    verify_commands: list[str],
    concurrency: int,
    dry_run: bool,
    codex_runtime: dict[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "created_at": utc_now(),
        "dry_run": dry_run,
        "project": str(project),
        "git": initial_git.to_json(),
        "concurrency": concurrency,
        "codex": codex_runtime,
        "verify": verify_commands,
        "allowlist": sorted(allowlist),
        "tasks": [task.to_json() for task in tasks],
    }


def _orchestrate_paths(run_dir: Path) -> dict[str, str]:
    return {
        "manifest": str(run_dir / "manifest.json"),
        "events": str(run_dir / "events.jsonl"),
        "results": str(run_dir / "results.jsonl"),
        "result": str(run_dir / "result.json"),
    }


def _compact_orchestrate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: payload[key]
        for key in (
            "run_id",
            "run_dir",
            "dry_run",
            "status",
            "ok",
            "fully_verified",
            "worker_status",
            "scope_status",
            "verification_status",
            "codex",
            "paths",
            "task_count",
            "postflight_changed_files",
            "out_of_scope_files",
            "git_head_changed",
        )
        if key in payload
    }


def _load_tasks(args: argparse.Namespace) -> Any:
    raw = Path(args.tasks).read_text() if args.tasks else sys.stdin.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(f"Invalid task JSON: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded fleet of parallel Codex workers under Claude orchestration.")
    parser.add_argument("--tasks", help="JSON task file (otherwise stdin).")
    parser.add_argument("--project", default=None, help="Project root = worker cwd (default: current directory).")
    parser.add_argument("--concurrency", type=int, default=4, help="Concurrent workers. Default: 4.")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL, help=f"Codex model. Default: {DEFAULT_CODEX_MODEL}.")
    parser.add_argument(
        "--effort",
        choices=REASONING_EFFORTS,
        default=DEFAULT_CODEX_EFFORT,
        help=f"Reasoning effort for every Codex turn. Default: {DEFAULT_CODEX_EFFORT}.",
    )
    parser.add_argument("--verify", action="append", default=[], help="Verification command to run after workers and scope check.")
    parser.add_argument("--run-dir", help="Ledger directory override (default: experiments/codex-bridge/runs/<run_id>).")
    parser.add_argument("--allow-dirty-overlap", action="store_true", help="Allow launch when existing dirty files overlap task files.")
    parser.add_argument("--summary-stdout", action="store_true", help="Print compact JSON to stdout; full results stay in result.json/results.jsonl.")
    parser.add_argument("--heartbeat-sec", type=int, default=120, help="Seconds between ledger heartbeat events while Codex workers run; 0 disables.")
    parser.add_argument("--dry-run", action="store_true", help="Validate tasks and write ledger without invoking Codex.")
    args = parser.parse_args()

    project = Path(args.project or os.getcwd()).expanduser().resolve()

    try:
        if args.concurrency < 1:
            raise UsageError("--concurrency must be >= 1.")
        if args.heartbeat_sec < 0:
            raise UsageError("--heartbeat-sec must be >= 0.")
        if not project.is_dir():
            raise UsageError(f"--project must be an existing directory: {project}")

        tasks = normalize_tasks(project, _load_tasks(args))
        allowlist = {path for task in tasks for path in task.files}
        initial_git = capture_git_snapshot(project, required=not args.dry_run)
        dirty_overlap = dirty_overlaps(initial_git.dirty_files, allowlist)
        if dirty_overlap and not args.allow_dirty_overlap:
            raise UsageError(
                "Dirty files overlap task files; commit/stage them or pass --allow-dirty-overlap: "
                + ", ".join(dirty_overlap)
            )

        codex_runtime = {
            "model": args.model,
            "effort": args.effort,
            "worker_sandbox": WORKER_SANDBOX,
            "worker_approval_mode": WORKER_APPROVAL_MODE,
            "thread_ephemeral": BRIDGE_THREAD_EPHEMERAL,
            "heartbeat_sec": args.heartbeat_sec,
        }
        run_id, run_dir = prepare_run_dir(args.run_dir, project=project)
        paths = _orchestrate_paths(run_dir)
        manifest = build_manifest(
            run_id=run_id,
            run_dir=run_dir,
            project=project,
            tasks=tasks,
            allowlist=allowlist,
            initial_git=initial_git,
            verify_commands=args.verify,
            concurrency=args.concurrency,
            dry_run=args.dry_run,
            codex_runtime=codex_runtime,
        )
        manifest["paths"] = paths
        write_json(run_dir / "manifest.json", manifest)
        append_event(run_dir, "validated", task_count=len(tasks), dry_run=args.dry_run)
    except OSError as exc:
        print(f"[orch] filesystem error: {exc}", file=sys.stderr)
        return 1
    except UsageError as exc:
        print(f"[orch] {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        payload = {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "dry_run": True,
            "status": "validated",
            "ok": True,
            "codex": codex_runtime,
            "paths": paths,
            "task_count": len(tasks),
            "git": initial_git.to_json(),
            "tasks": [task.to_json() for task in tasks],
        }
        write_json(run_dir / "result.json", payload)
        print(f"[orch dry-run] {len(tasks)} tasks, concurrency={args.concurrency}, run_dir={run_dir}", file=sys.stderr)
        stdout_payload = _compact_orchestrate_payload(payload) if args.summary_stdout else payload
        print(json.dumps(stdout_payload, ensure_ascii=False, indent=2))
        return 0

    removed = scrub_billing_env()
    print(
        f"[orch] старт: {len(tasks)} задач, лимит {args.concurrency}, project={project}, "
        f"run_dir={run_dir}, model={args.model}, effort={args.effort}, "
        f"sandbox={WORKER_SANDBOX}, approval={WORKER_APPROVAL_MODE}"
        + (f" | вырезано из env: {', '.join(removed)}" if removed else " | env чист"),
        file=sys.stderr,
    )
    append_event(run_dir, "codex_start", task_count=len(tasks))

    defaults = {"cwd": str(project), "model": args.model, "effort": args.effort, "run_dir": run_dir}
    results = asyncio.run(_run_fleet(tasks, defaults, args.concurrency, args.heartbeat_sec))

    worker_status = "completed" if all(r["worker_status"] == "completed" for r in results) else "failed"
    after_git = capture_git_snapshot(project, required=True)
    scope = compare_scope(initial_git, after_git, allowlist)
    # run_dir теперь по умолчанию живёт внутри проекта (_workspace/codex-artifacts):
    # его ledger/файлы — собственная площадка прогона, не правка проекта, иначе
    # каждый прогон ложно валил бы scope об собственный журнал.
    changed_files = [f for f in scope.changed_files if not is_scope_noise(project, run_dir, f)]
    out_of_scope_files = [f for f in scope.out_of_scope_files if not is_scope_noise(project, run_dir, f)]
    scope_status = "passed" if (not out_of_scope_files and not scope.head_changed) else "failed"
    append_event(
        run_dir,
        "scope_done",
        scope_status=scope_status,
        changed_files=changed_files,
        out_of_scope_files=out_of_scope_files,
        git_head_changed=scope.head_changed,
    )

    if worker_status == "completed" and scope_status == "passed":
        verification_status, verification_results = run_verification(args.verify, project, run_dir)
    elif args.verify:
        verification_status, verification_results = "skipped", []
    else:
        verification_status, verification_results = "not_requested", []

    ok = (
        worker_status == "completed"
        and scope_status == "passed"
        and verification_status in {"passed", "not_requested"}
    )
    payload = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "ok": ok,
        "fully_verified": verification_status == "passed",
        "codex": codex_runtime,
        "paths": paths,
        "task_count": len(tasks),
        "worker_status": worker_status,
        "scope_status": scope_status,
        "verification_status": verification_status,
        "postflight_changed_files": changed_files,
        "out_of_scope_files": out_of_scope_files,
        "git_head_changed": scope.head_changed,
        "git": {"initial": initial_git.to_json(), "after": after_git.to_json()},
        "results": results,
        "verification_results": verification_results,
    }
    write_json(run_dir / "result.json", payload)
    append_event(
        run_dir,
        "done",
        ok=ok,
        worker_status=worker_status,
        scope_status=scope_status,
        verification_status=verification_status,
    )

    _safe_print(
        f"[orch] готово: worker={worker_status} scope={scope_status} "
        f"verify={verification_status} ok={ok}"
    )
    stdout_payload = _compact_orchestrate_payload(payload) if args.summary_stdout else payload
    _safe_print(json.dumps(stdout_payload, ensure_ascii=False, indent=2), stream=sys.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
