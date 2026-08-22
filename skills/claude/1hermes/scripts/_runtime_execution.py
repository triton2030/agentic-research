"""Host-side process, resume-lock, and file-only worktree boundaries."""

from __future__ import annotations

import fcntl
import hashlib
import os
import signal
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def acquire_resume_lock(session_id: str) -> tuple[Any | None, str | None]:
    hermes_home = os.environ.get("HERMES_HOME")
    root = Path(hermes_home).expanduser() if hermes_home else Path.home() / ".hermes"
    handle = None
    try:
        lock_dir = root / "locks"
        lock_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:20]
        handle = (lock_dir / f"1hermes-resume-{digest}.lock").open(
            "a+", encoding="utf-8"
        )
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, BlockingIOError) as exc:
        if handle:
            handle.close()
        return None, f"session is already being resumed: {exc}"
    return handle, None


def release_resume_lock(handle: Any | None) -> None:
    if handle is None:
        return
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def run_process_group(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def create_worktree(repo: Path) -> tuple[dict[str, str] | None, str | None]:
    """Create a bounded worktree for a file-only model; no fetch or config edits."""
    remotes = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)", "refs/remotes"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if remotes.returncode != 0 or not remotes.stdout.strip():
        return None, "--worktree requires at least one remote-tracking ref"
    hermes_home = os.environ.get("HERMES_HOME")
    root = Path(hermes_home).expanduser() if hermes_home else Path.home() / ".hermes"
    run_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
    path = root / "worktrees" / f"{repo.name}-{run_id}"
    branch = f"1hermes/{run_id}"
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if base.returncode != 0:
        return None, "--worktree requires a readable git HEAD"
    path.parent.mkdir(parents=True, exist_ok=True)
    created = subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(path), base.stdout.strip()],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if created.returncode != 0:
        return None, "git worktree add failed: " + (
            created.stderr.strip() or "unknown error"
        )
    return {
        "path": str(path.resolve()),
        "branch": branch,
        "base_commit": base.stdout.strip(),
        "repo_root": str(repo),
        "owner": "1hermes file-only adapter",
    }, None


def recover_failed_worktree(worktree: dict[str, str] | None) -> dict[str, Any] | None:
    """Discard an empty failed tree; preserve dirty partial work for recovery."""
    if not worktree:
        return None
    path = Path(worktree["path"])
    if not path.is_dir():
        return {**worktree, "exists": False}
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode != 0 or status.stdout.strip():
        return {**worktree, "exists": True, "dirty": True, "recovery_required": True}
    repo = Path(worktree["repo_root"])
    removed = subprocess.run(
        ["git", "worktree", "remove", "--force", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if removed.returncode == 0:
        subprocess.run(
            ["git", "branch", "-D", worktree["branch"]],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        return {**worktree, "exists": False, "discarded": True}
    return {**worktree, "exists": True, "cleanup_error": removed.stderr.strip()}


def commit_and_verify_worktree(
    worktree: dict[str, str] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if not worktree:
        return None, "worktree metadata is missing"
    path = Path(worktree["path"])
    if not path.is_dir():
        return None, "worktree path no longer exists"

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], cwd=path, capture_output=True, text=True, check=False
        )

    def recovery_receipt(message: str) -> tuple[dict[str, Any], str]:
        current = git("status", "--porcelain")
        dirty = bool(current.stdout.strip()) if current.returncode == 0 else None
        return (
            {
                **worktree,
                "exists": path.is_dir(),
                "dirty": dirty,
                "recovery_required": True,
            },
            message,
        )

    before = git("status", "--porcelain")
    if before.returncode != 0:
        return recovery_receipt("worktree status is unreadable")
    if not before.stdout.strip():
        recover_failed_worktree(worktree)
        return None, "model produced no file changes; empty worktree discarded"
    staged = git("add", "-A")
    if staged.returncode != 0:
        return recovery_receipt("worktree changes could not be staged")
    committed = git("commit", "-m", "1hermes: preserve file-only model result")
    if committed.returncode != 0:
        return recovery_receipt(
            "worktree changes could not be committed: " + committed.stderr.strip()
        )

    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    status = git("status", "--porcelain")
    unpushed = git("rev-list", "--count", "HEAD", "--not", "--remotes")
    checks = (head, branch, status, unpushed)
    if any(item.returncode != 0 for item in checks):
        return recovery_receipt("preserved worktree git evidence is unreadable")
    if branch.stdout.strip() != worktree["branch"]:
        return recovery_receipt("worktree branch identity changed")
    if status.stdout.strip():
        return recovery_receipt("preserved worktree is not clean after commit")
    unpushed_count = int(unpushed.stdout.strip() or "0")
    if unpushed_count < 1:
        return recovery_receipt("preserved worktree has no unpushed commit")
    return {
        **worktree,
        "head": head.stdout.strip(),
        "unpushed_commits": unpushed_count,
        "clean": True,
    }, None
