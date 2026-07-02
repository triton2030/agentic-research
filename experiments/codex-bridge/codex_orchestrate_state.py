"""Git snapshot, run-ledger and heartbeat helpers shared by every bridge
entrypoint (codex_review, codex_investigate, codex_orchestrate)."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex_orchestrate_contract import UsageError, path_allowed

BACKEND_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class GitSnapshot:
    available: bool
    worktree_root: str | None
    git_head: str | None
    dirty_files: tuple[str, ...]
    fingerprints: dict[str, str]
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "worktree_root": self.worktree_root,
            "git_head": self.git_head,
            "dirty_files": list(self.dirty_files),
            "error": self.error,
        }


@dataclass(frozen=True)
class ScopeCheck:
    changed_files: tuple[str, ...]
    out_of_scope_files: tuple[str, ...]
    head_changed: bool

    @property
    def passed(self) -> bool:
        return not self.out_of_scope_files and not self.head_changed


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git_text(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _git_bytes(cwd: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _nul_paths(data: bytes) -> list[str]:
    return [part.decode("utf-8", "surrogateescape") for part in data.split(b"\0") if part]


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _worktree_root(project: Path, *, required: bool) -> tuple[Path | None, str | None]:
    result = _git_text(project, "rev-parse", "--show-toplevel")
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve(), None
    error = result.stderr.strip() or result.stdout.strip() or "git worktree unavailable"
    if required:
        raise UsageError(f"Git worktree is required for write-fleet safety: {error}")
    return None, error


def _head(root: Path) -> str | None:
    result = _git_text(root, "rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else None


def _dirty_repo_paths(root: Path) -> set[str]:
    paths: set[str] = set()
    commands = [
        ("diff", "--name-only", "-z", "--"),
        ("diff", "--cached", "--name-only", "-z", "--"),
        ("ls-files", "--others", "--exclude-standard", "-z", "--"),
    ]
    for command in commands:
        result = _git_bytes(root, *command)
        if result.returncode != 0:
            error = result.stderr.decode("utf-8", "replace").strip()
            raise UsageError(f"Git dirty snapshot failed: {error or ' '.join(command)}")
        paths.update(_nul_paths(result.stdout))
    return paths


def _repo_to_project_path(root: Path, project: Path, repo_path: str) -> str | None:
    full = (root / repo_path).resolve()
    try:
        return full.relative_to(project).as_posix()
    except ValueError:
        return None


def _project_to_repo_path(root: Path, project: Path, project_path: str) -> str:
    return (project / project_path).resolve().relative_to(root).as_posix()


def _git_blob_hash(root: Path, *args: str) -> str:
    result = _git_bytes(root, *args)
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", "replace").strip()
        raise UsageError(f"Git fingerprint failed: {error or ' '.join(args)}")
    return _sha_bytes(result.stdout)


def _filesystem_fingerprint(path: Path) -> str:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return "missing"
    if stat.S_ISLNK(info.st_mode):
        return "symlink:" + os.readlink(path)
    if stat.S_ISREG(info.st_mode):
        return f"file:{info.st_mode:o}:{_sha_file(path)}"
    if stat.S_ISDIR(info.st_mode):
        return f"dir:{info.st_mode:o}"
    return f"other:{info.st_mode:o}:{info.st_size}:{info.st_mtime_ns}"


def _dirty_fingerprint(root: Path, project: Path, path: str) -> str:
    repo_path = _project_to_repo_path(root, project, path)
    filesystem = _filesystem_fingerprint(project / path)
    unstaged = _git_blob_hash(root, "diff", "--binary", "--", repo_path)
    staged = _git_blob_hash(root, "diff", "--cached", "--binary", "--", repo_path)
    return json.dumps(
        {"filesystem": filesystem, "unstaged": unstaged, "staged": staged},
        sort_keys=True,
        ensure_ascii=False,
    )


def capture_git_snapshot(project: Path, *, required: bool) -> GitSnapshot:
    project = project.resolve()
    root, error = _worktree_root(project, required=required)
    if root is None:
        return GitSnapshot(
            available=False,
            worktree_root=None,
            git_head=None,
            dirty_files=(),
            fingerprints={},
            error=error,
        )

    dirty_files: set[str] = set()
    for repo_path in _dirty_repo_paths(root):
        project_path = _repo_to_project_path(root, project, repo_path)
        if project_path:
            dirty_files.add(project_path)

    fingerprints = {
        path: _dirty_fingerprint(root, project, path)
        for path in sorted(dirty_files)
    }
    return GitSnapshot(
        available=True,
        worktree_root=str(root),
        git_head=_head(root),
        dirty_files=tuple(sorted(dirty_files)),
        fingerprints=fingerprints,
    )


def compare_scope(initial: GitSnapshot, after: GitSnapshot, allowlist: set[str]) -> ScopeCheck:
    if not initial.available or not after.available:
        raise UsageError("Git snapshots are required for postflight scope check.")

    all_paths = set(initial.fingerprints) | set(after.fingerprints)
    changed = sorted(
        path
        for path in all_paths
        if initial.fingerprints.get(path) != after.fingerprints.get(path)
    )
    out_of_scope = sorted(path for path in changed if not path_allowed(path, allowlist))
    return ScopeCheck(
        changed_files=tuple(changed),
        out_of_scope_files=tuple(out_of_scope),
        head_changed=initial.git_head != after.git_head,
    )


def make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]


def prepare_run_dir(raw_run_dir: str | None) -> tuple[str, Path]:
    run_id = make_run_id()
    run_dir = Path(raw_run_dir).expanduser().resolve() if raw_run_dir else BACKEND_DIR / "runs" / run_id
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise UsageError(f"Run dir already exists; choose a fresh --run-dir: {run_dir}") from exc
    return run_id, run_dir


def write_json(path: Path, data: Any) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, data: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def append_event(run_dir: Path, event: str, **data: Any) -> None:
    append_jsonl(run_dir / "events.jsonl", {"ts": utc_now(), "event": event, **data})


def append_heartbeat(
    run_dir: Path,
    started_monotonic: float,
    **data: Any,
) -> None:
    append_event(
        run_dir,
        "heartbeat",
        elapsed_sec=int(time.monotonic() - started_monotonic),
        **data,
    )


def start_heartbeat(
    run_dir: Path | None,
    heartbeat_sec: int,
    started_monotonic: float,
    *,
    thread_name: str = "codex-heartbeat",
    **fields: Any,
) -> tuple[threading.Event, threading.Thread | None]:
    """Background ledger heartbeat shared by every bridge entrypoint.

    Returns (stop_event, thread). No-op (thread is None) when there is no run_dir
    or heartbeat is disabled, so callers can always .set()/.join() the pair.
    """
    stop = threading.Event()
    if run_dir is None or heartbeat_sec <= 0:
        return stop, None

    def loop() -> None:
        while not stop.wait(heartbeat_sec):
            append_heartbeat(run_dir, started_monotonic, **fields)

    thread = threading.Thread(target=loop, name=thread_name, daemon=True)
    thread.start()
    return stop, thread
