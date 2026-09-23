#!/usr/bin/env python3
"""Run bounded, durable Luna Max review jobs through ``codex exec``."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Any

from packets import PacketError, check as check_packets, prepare as prepare_packets


MODEL = "gpt-6-luna"
EFFORT = "max"
DOCTOR_TIMEOUT_SECONDS = 10
STATE_FILE = "run.json"
LOCK_FILE = ".lock"
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SCRUB_ENV = {
    "CODEX_API_KEY",
    "OPENAI_API_KEY",
    "CODEX_THREAD_ID",
    "CODEX_SESSION_ID",
    "CODEX_APP_TOOLS_PIPE_PATH",
    "CODEX_PERMISSION_PROFILE",
}


class CliError(Exception):
    """A user-facing command error."""


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(message)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_utf8(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CliError(f"cannot read {label} {path}: {exc}") from exc


def _atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _load_state(run_dir: Path) -> dict[str, Any]:
    path = run_dir / STATE_FILE
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot read run state {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("tasks"), dict):
        raise CliError(f"invalid run state in {path}")
    return value


def _clean_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in SCRUB_ENV}


def _codex_path() -> str:
    path = shutil.which("codex")
    if not path:
        raise CliError("codex executable was not found on PATH")
    return path


def _doctor_payload() -> tuple[dict[str, Any], bool]:
    try:
        executable = _codex_path()
    except CliError:
        return {
            "status": "unavailable",
            "codex_found": False,
            "chatgpt_login": False,
            "model_requested": MODEL,
        }, False
    environment = _clean_env()
    try:
        version = subprocess.run(
            [executable, "--version"],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
            timeout=DOCTOR_TIMEOUT_SECONDS,
        )
        login = subprocess.run(
            [executable, "login", "status"],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
            timeout=DOCTOR_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "status": "unavailable",
            "codex_found": True,
            "codex_path": executable,
            "chatgpt_login": False,
            "auth_source": "other_or_missing",
            "model_requested": MODEL,
        }, False
    login_text = "\n".join((login.stdout, login.stderr)).strip()
    chatgpt_login = login.returncode == 0 and "chatgpt" in login_text.lower()
    healthy = version.returncode == 0 and chatgpt_login
    return {
        "status": "ready" if healthy else "unavailable",
        "codex_found": True,
        "codex_path": executable,
        "codex_version": (version.stdout or version.stderr).strip(),
        "chatgpt_login": chatgpt_login,
        "auth_source": "chatgpt" if chatgpt_login else "other_or_missing",
        "model_requested": MODEL,
        "reasoning_effort": EFFORT,
        "sandbox": "read-only",
        "approval_policy": "never",
    }, healthy


def _require_ready() -> str:
    payload, healthy = _doctor_payload()
    if not healthy:
        raise CliError("codex with ChatGPT login is required; run `codex login`")
    return str(payload["codex_path"])


class RunLock:
    def __init__(self, run_dir: Path) -> None:
        self.path = run_dir / LOCK_FILE
        self.stream: Any = None

    def __enter__(self) -> "RunLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.stream.close()
            raise CliError(f"another writer is active for {self.path.parent}") from exc
        self.stream.seek(0)
        self.stream.truncate()
        self.stream.write(f"pid={os.getpid()}\n")
        self.stream.flush()
        return self

    def __exit__(self, *_: object) -> None:
        if self.stream is not None:
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()


def _validate_positive(value: str) -> int:
    integer = int(value)
    if integer < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return integer


def _absolute_existing(path_text: Any, label: str, *, directory: bool) -> Path:
    if not isinstance(path_text, str):
        raise CliError(f"{label} must be a string")
    path = Path(path_text)
    if not path.is_absolute():
        raise CliError(f"{label} must be an absolute path: {path}")
    if directory and not path.is_dir():
        raise CliError(f"{label} is not an existing directory: {path}")
    if not directory and not path.is_file():
        raise CliError(f"{label} is not an existing file: {path}")
    return path


def _load_tasks(path: Path) -> list[dict[str, Any]]:
    text = _read_utf8(path, "task file")
    tasks: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CliError(f"invalid JSON on task line {line_number}: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise CliError(f"task line {line_number} must be a JSON object")
        identifier = value.get("id")
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            raise CliError(f"task line {line_number} has an unsafe id")
        if identifier in identifiers:
            raise CliError(f"duplicate task id {identifier!r}")
        identifiers.add(identifier)
        cwd = _absolute_existing(value.get("cwd"), f"task {identifier} cwd", directory=True)
        prompt_path = _absolute_existing(
            value.get("prompt_file"), f"task {identifier} prompt_file", directory=False
        )
        prompt = _read_utf8(prompt_path, f"prompt for task {identifier}")
        if not prompt.strip():
            raise CliError(f"prompt for task {identifier} is empty")
        tasks.append(
            {
                "id": identifier,
                "cwd": str(cwd),
                "prompt_source": str(prompt_path),
                "prompt": prompt,
                "prompt_sha256": _sha256(prompt.encode("utf-8")),
            }
        )
    if not tasks:
        raise CliError("task file contains no tasks")
    return tasks


def _copy_schema(schema_path: Path | None, inputs_dir: Path) -> dict[str, str] | None:
    if schema_path is None:
        return None
    source = _absolute_existing(str(schema_path), "output schema", directory=False)
    text = _read_utf8(source, "output schema")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CliError(f"output schema is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CliError("output schema must be a JSON object")
    destination = inputs_dir / "output-schema.json"
    destination.write_text(text, encoding="utf-8")
    return {
        "source": str(source),
        "copy": str(destination.relative_to(inputs_dir.parent)),
        "sha256": _sha256(text.encode("utf-8")),
    }


class Runner:
    def __init__(
        self, run_dir: Path, state: dict[str, Any], codex: str, prompts: dict[str, str]
    ) -> None:
        self.run_dir = run_dir
        self.state = state
        self.codex = codex
        self.prompts = prompts
        self.state_lock = threading.Lock()
        self.process_lock = threading.Lock()
        self.processes: dict[str, subprocess.Popen[str]] = {}
        self.cancelled = threading.Event()

    def save(self) -> None:
        self.state["updated_at"] = _now()
        _atomic_json(self.run_dir / STATE_FILE, self.state)

    def _update(self, identifier: str, status: str, attempt: dict[str, Any]) -> None:
        with self.state_lock:
            task = self.state["tasks"][identifier]
            task["status"] = status
            if not task["attempts"] or task["attempts"][-1]["number"] != attempt["number"]:
                task["attempts"].append(attempt)
            else:
                task["attempts"][-1] = attempt
            self.save()

    def cancel_all(self) -> None:
        self.cancelled.set()
        with self.process_lock:
            processes = list(self.processes.values())
        for process in processes:
            _terminate_group(process)

    def run_task(self, identifier: str, timeout: int) -> dict[str, Any]:
        task = self.state["tasks"][identifier]
        if self.cancelled.is_set():
            return {"id": identifier, "status": "queued", "attempt": None}
        attempt_number = len(task["attempts"]) + 1
        relative_dir = Path("attempts") / identifier / f"{attempt_number:04d}"
        attempt_dir = self.run_dir / relative_dir
        attempt_dir.mkdir(parents=True, exist_ok=False)
        report = attempt_dir / "report.txt"
        events = attempt_dir / "events.jsonl"
        stderr = attempt_dir / "stderr.txt"
        attempt: dict[str, Any] = {
            "number": attempt_number,
            "status": "running",
            "started_at": _now(),
            "report": str((relative_dir / "report.txt")),
            "events": str((relative_dir / "events.jsonl")),
            "stderr": str((relative_dir / "stderr.txt")),
            "model_requested": MODEL,
        }
        self._update(identifier, "running", attempt)
        argv = [
            self.codex,
            "exec",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "-m",
            MODEL,
            "-c",
            'model_reasoning_effort="max"',
            "-c",
            'approval_policy="never"',
            "--sandbox",
            "read-only",
            "--json",
            "-o",
            str(report),
            "-C",
            task["cwd"],
        ]
        schema = self.state.get("output_schema")
        if schema:
            argv.extend(["--output-schema", str(self.run_dir / schema["copy"])])
        argv.append("-")
        timed_out = False
        error: str | None = None
        returncode: int | None = None
        try:
            with events.open("w", encoding="utf-8") as event_stream, stderr.open(
                "w", encoding="utf-8"
            ) as error_stream:
                process = subprocess.Popen(
                    argv,
                    stdin=subprocess.PIPE,
                    stdout=event_stream,
                    stderr=error_stream,
                    text=True,
                    env=_clean_env(),
                    start_new_session=True,
                )
                with self.process_lock:
                    self.processes[identifier] = process
                attempt["process_group_id"] = process.pid
                self._update(identifier, "running", attempt)
                if self.cancelled.is_set():
                    _terminate_group(process)
                try:
                    process.communicate(self.prompts[identifier], timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    error = f"timed out after {timeout} seconds"
                    _terminate_group(process)
                    process.wait()
                returncode = process.returncode
        except OSError as exc:
            error = f"cannot start codex exec: {exc}"
        finally:
            with self.process_lock:
                self.processes.pop(identifier, None)
        report_ok = report.is_file() and report.stat().st_size > 0
        if self.cancelled.is_set() and not timed_out:
            error = error or "cancelled"
        observed = _observed_metadata(events)
        model_resolved = observed.get("model_resolved")
        if error is None and model_resolved is not None and model_resolved != MODEL:
            error = f"resolved model {model_resolved!r} does not match requested model {MODEL!r}"
        succeeded = returncode == 0 and report_ok and error is None
        if not succeeded and error is None:
            if returncode != 0:
                error = f"codex exec exited with status {returncode}"
            else:
                error = "codex exec produced no final report"
        attempt.update(
            {
                "status": "succeeded" if succeeded else "failed",
                "finished_at": _now(),
                "exit_code": returncode,
                "timed_out": timed_out,
            }
        )
        if error:
            attempt["error"] = error
        attempt.update(observed)
        self._update(identifier, attempt["status"], attempt)
        return {"id": identifier, "status": attempt["status"], "attempt": attempt_number}

    def run_many(self, identifiers: list[str], parallel: int, timeout: int) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            futures = {pool.submit(self.run_task, identifier, timeout): identifier for identifier in identifiers}
            try:
                for future in as_completed(futures):
                    results.append(future.result())
            except (KeyboardInterrupt, SystemExit):
                self.cancel_all()
                for future in futures:
                    future.cancel()
                raise
        return sorted(results, key=lambda item: item["id"])


def _terminate_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 0.5
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.02)
    try:
        # The group can outlive its leader when a job spawned children.
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        pass


def _process_group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _observed_metadata(events: Path) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    try:
        lines = events.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return observed
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            if value.get("type") == "thread.started" and isinstance(value.get("thread_id"), str):
                observed["thread_id"] = value["thread_id"]
            if value.get("type") == "turn.completed" and isinstance(value.get("usage"), dict):
                observed["usage"] = value["usage"]
            for key in ("model_resolved", "model"):
                model = value.get(key)
                if isinstance(model, str) and model:
                    observed["model_resolved"] = model
    return observed


def _initialize_run(
    tasks_path: Path, run_dir: Path, timeout: int, output_schema: Path | None
) -> dict[str, Any]:
    tasks = _load_tasks(_absolute_existing(str(tasks_path), "task file", directory=False))
    entries = list(run_dir.iterdir())
    unexpected = [entry for entry in entries if entry.name != LOCK_FILE]
    if unexpected:
        raise CliError(f"run directory is not empty: {run_dir}")
    inputs_dir = run_dir / "inputs"
    inputs_dir.mkdir()
    schema = _copy_schema(output_schema, inputs_dir)
    task_state: dict[str, Any] = {}
    for task in tasks:
        prompt_copy = inputs_dir / f"{task['id']}.txt"
        prompt_copy.write_text(task.pop("prompt"), encoding="utf-8")
        task_state[task["id"]] = {
            **task,
            "prompt_copy": str(prompt_copy.relative_to(run_dir)),
            "status": "queued",
            "attempts": [],
        }
    state: dict[str, Any] = {
        "version": 1,
        "created_at": _now(),
        "updated_at": _now(),
        "model_requested": MODEL,
        "reasoning_effort": EFFORT,
        "timeout_seconds": timeout,
        "tasks_source": str(tasks_path),
        "tasks": task_state,
    }
    if schema:
        state["output_schema"] = schema
    _atomic_json(run_dir / STATE_FILE, state)
    return state


def _restore_prompts(
    run_dir: Path, state: dict[str, Any], identifiers: list[str]
) -> dict[str, str]:
    prompts: dict[str, str] = {}
    for identifier in identifiers:
        task = state["tasks"][identifier]
        prompt_path = run_dir / task["prompt_copy"]
        prompt = _read_utf8(prompt_path, f"stored prompt for task {identifier}")
        if _sha256(prompt.encode("utf-8")) != task["prompt_sha256"]:
            raise CliError(f"stored prompt hash changed for task {identifier}")
        prompts[identifier] = prompt
    return prompts


def _summary(state: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    counts = {status: 0 for status in ("queued", "running", "succeeded", "failed")}
    task_ids: dict[str, list[str]] = {status: [] for status in counts}
    for identifier, task in sorted(state["tasks"].items()):
        status = task.get("status", "failed")
        counts[status] = counts.get(status, 0) + 1
        task_ids.setdefault(status, []).append(identifier)
    return {
        "run_dir": str(run_dir),
        "state_path": str(run_dir / STATE_FILE),
        "attempts_dir": str(run_dir / "attempts"),
        "model_requested": state.get("model_requested"),
        "counts": counts,
        "task_ids": task_ids,
    }


def _all_succeeded(payload: dict[str, Any]) -> bool:
    counts = payload["counts"]
    return counts["failed"] == 0 and counts["queued"] == 0 and counts["running"] == 0


def _emit(payload: dict[str, Any], json_output: bool, *, reports: bool = False) -> None:
    if json_output:
        print(json.dumps(payload, sort_keys=True))
        return
    counts = payload.get("counts")
    if counts:
        print(
            " ".join(
                f"{key}={counts.get(key, 0)}"
                for key in ("succeeded", "failed", "running", "queued")
            )
        )
        print(f"run_dir={payload['run_dir']}")
        print(f"state={payload['state_path']}")
    elif "status" in payload:
        print(payload["status"])
    if reports:
        for result in payload.get("results", []):
            detail = result.get("report_path") or result.get("error") or "(no report)"
            print(f"{result['id']} [{result['status']}] {detail}")


def command_doctor(args: argparse.Namespace) -> int:
    payload, healthy = _doctor_payload()
    _emit(payload, args.json)
    return 0 if healthy else 1


def command_prepare(args: argparse.Namespace) -> int:
    base = Path(__file__).resolve().parents[1]
    payload = prepare_packets(
        Path(args.plan),
        Path(args.out),
        base / "assets/packet-reviewer.md",
        base / "assets/report.schema.json",
    )
    _emit(payload, args.json)
    return 0


def command_run(args: argparse.Namespace) -> int:
    codex = _require_ready()
    run_dir = Path(args.run_dir).resolve()
    with RunLock(run_dir):
        state = _initialize_run(Path(args.tasks), run_dir, args.timeout, args.output_schema)
        identifiers = sorted(state["tasks"])
        prompts = _restore_prompts(run_dir, state, identifiers)
        runner = Runner(run_dir, state, codex, prompts)
        try:
            runner.run_many(identifiers, args.parallel, args.timeout)
        except (KeyboardInterrupt, SystemExit):
            runner.cancel_all()
            raise CliError("run cancelled")
        payload = _summary(state, run_dir)
    _emit(payload, args.json)
    return 0 if _all_succeeded(payload) else 1


def command_status(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    payload = _summary(_load_state(run_dir), run_dir)
    _emit(payload, args.json)
    return 0


def command_results(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    state = _load_state(run_dir)
    payload = _summary(state, run_dir)
    results: list[dict[str, Any]] = []
    for identifier, task in sorted(state["tasks"].items()):
        latest = task["attempts"][-1] if task.get("attempts") else None
        item: dict[str, Any] = {"id": identifier, "status": task["status"]}
        if latest:
            item["attempt"] = latest["number"]
            item["report_path"] = str(run_dir / latest["report"])
            if "error" in latest:
                item["error"] = latest["error"]
        results.append(item)
    payload["results"] = results
    _emit(payload, args.json, reports=True)
    return 0 if _all_succeeded(payload) else 1


def command_retry(args: argparse.Namespace) -> int:
    codex = _require_ready()
    run_dir = Path(args.run_dir).resolve()
    with RunLock(run_dir):
        state = _load_state(run_dir)
        runner = Runner(run_dir, state, codex, {})
        for identifier, task in state["tasks"].items():
            if task.get("status") != "running":
                continue
            latest = task["attempts"][-1] if task.get("attempts") else None
            process_group_id = latest.get("process_group_id") if latest else None
            if isinstance(process_group_id, int) and _process_group_exists(process_group_id):
                raise CliError(
                    f"task {identifier} still has a live process group {process_group_id}; "
                    "stop it before retrying"
                )
            if latest:
                latest["status"] = "failed"
                latest["finished_at"] = _now()
                latest["error"] = "previous writer stopped before recording completion"
            task["status"] = "failed"
        runner.save()
        identifiers = sorted(
            identifier
            for identifier, task in state["tasks"].items()
            if task.get("status") in {"failed", "queued"}
        )
        if identifiers:
            prompts = _restore_prompts(run_dir, state, identifiers)
            runner = Runner(run_dir, state, codex, prompts)
            try:
                runner.run_many(identifiers, args.parallel, int(state["timeout_seconds"]))
            except (KeyboardInterrupt, SystemExit):
                runner.cancel_all()
                raise CliError("retry cancelled")
        payload = _summary(state, run_dir)
    _emit(payload, args.json)
    return 0 if _all_succeeded(payload) else 1


def command_check(args: argparse.Namespace) -> int:
    payload, exit_code = check_packets(Path(args.prepared), Path(args.run_dir))
    _emit(payload, args.json)
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = ArgumentParser(
        prog="max-review", description="Run bounded Luna Max reviews through codex exec."
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="check Codex and ChatGPT login")
    doctor.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    doctor.set_defaults(handler=command_doctor)

    prepare = subparsers.add_parser("prepare", help="prepare self-contained review packets")
    prepare.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    prepare.add_argument("--plan", required=True)
    prepare.add_argument("--out", required=True)
    prepare.set_defaults(handler=command_prepare)

    run = subparsers.add_parser("run", help="run all tasks from a JSONL file")
    run.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    run.add_argument("--tasks", required=True, type=Path)
    run.add_argument("--run-dir", required=True)
    run.add_argument("--parallel", required=True, type=_validate_positive)
    run.add_argument("--timeout", required=True, type=_validate_positive)
    run.add_argument("--output-schema", type=Path)
    run.set_defaults(handler=command_run)

    status = subparsers.add_parser("status", help="read current task status")
    status.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    status.add_argument("run_dir")
    status.set_defaults(handler=command_status)

    results = subparsers.add_parser("results", help="read final reports and failures")
    results.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    results.add_argument("run_dir")
    results.set_defaults(handler=command_results)

    retry = subparsers.add_parser("retry", help="retry failed tasks without rerunning successes")
    retry.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    retry.add_argument("run_dir")
    retry.add_argument("--failed", action="store_true", required=True)
    retry.add_argument("--parallel", required=True, type=_validate_positive)
    retry.set_defaults(handler=command_retry)

    check = subparsers.add_parser("check", help="validate current packet reports")
    check.add_argument(
        "--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    check.add_argument("--prepared", required=True)
    check.add_argument("--run-dir", required=True)
    check.set_defaults(handler=command_check)
    return parser


def _interrupt_on_signal(_signum: int, _frame: Any) -> None:
    raise KeyboardInterrupt


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = argparse.Namespace(json="--json" in arguments)
    previous_sigterm: Any = None
    try:
        args = parser.parse_args(arguments)
        if args.command in {"run", "retry"}:
            previous_sigterm = signal.signal(signal.SIGTERM, _interrupt_on_signal)
        return int(args.handler(args))
    except (CliError, PacketError, OSError) as exc:
        payload = {"status": "error", "error": str(exc)}
        if getattr(args, "json", False):
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        if previous_sigterm is not None:
            signal.signal(signal.SIGTERM, previous_sigterm)


if __name__ == "__main__":
    raise SystemExit(main())
