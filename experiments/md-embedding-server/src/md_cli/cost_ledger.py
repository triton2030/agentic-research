from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None  # type: ignore[assignment]


TURN_BOUNDARY_SECONDS = 30
ROTATE_BYTES = 1_000_000
ROTATE_SECONDS = 24 * 60 * 60
GC_ARCHIVE_SECONDS = 30 * 24 * 60 * 60


def cache_root() -> Path:
    override = os.environ.get("MD_TOOLS_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".cache" / "md-tools"


def session_id() -> str:
    for env_name in ("CLAUDE_CODE_SESSION_ID", "CODEX_SESSION_ID", "MD_CLI_SESSION_ID"):
        value = os.environ.get(env_name)
        if value:
            return _safe_id(value)
    root = cache_root()
    root.mkdir(parents=True, exist_ok=True)
    path = root / "session-id"
    try:
        existing = path.read_text(encoding="utf-8").strip()
    except OSError:
        existing = ""
    if existing:
        return _safe_id(existing)
    generated = f"local-{uuid.uuid4().hex}"
    path.write_text(generated, encoding="utf-8")
    return generated


def ledger_path() -> Path:
    root = cache_root()
    root.mkdir(parents=True, exist_ok=True)
    return root / f"cost-{session_id()}.jsonl"


def _safe_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)


def _rotate_if_needed(path: Path) -> None:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return
    too_large = stat.st_size > ROTATE_BYTES
    too_old = time.time() - stat.st_mtime > ROTATE_SECONDS
    if not too_large and not too_old:
        return
    archive = path.with_name(f"{path.stem}-{int(time.time())}.archive.jsonl")
    try:
        path.rename(archive)
    except FileNotFoundError:
        pass


def _gc_archives(root: Path) -> None:
    cutoff = time.time() - GC_ARCHIVE_SECONDS
    for path in root.glob("cost-*.archive.jsonl"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except FileNotFoundError:
            pass


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, line.encode("utf-8"))
    finally:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def record_cost(usd: float, *, turn_boundary: bool = False) -> None:
    if not isinstance(usd, (int, float)) or usd <= 0:
        return
    path = ledger_path()
    _rotate_if_needed(path)
    if turn_boundary:
        _append_jsonl(path, {"ts": time.time(), "type": "turn_boundary"})
    _append_jsonl(path, {"ts": time.time(), "type": "cost", "usd": float(usd)})


def get_cost_snapshot() -> dict[str, float]:
    root = cache_root()
    root.mkdir(parents=True, exist_ok=True)
    _gc_archives(root)
    path = ledger_path()
    records = _read_records(path)
    session_usd = 0.0
    turn_usd = 0.0
    for record in records:
        if record.get("type") == "turn_boundary":
            turn_usd = 0.0
            continue
        if record.get("type") != "cost":
            continue
        usd = float(record.get("usd") or 0)
        session_usd += usd
        turn_usd += usd
    try:
        if time.time() - path.stat().st_mtime >= TURN_BOUNDARY_SECONDS:
            turn_usd = 0.0
    except FileNotFoundError:
        pass
    return {"turn_usd": _round4(turn_usd), "session_usd": _round4(session_usd)}


def _read_records(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    records = []
    for line in lines:
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def _round4(value: float) -> float:
    return round(value + 1e-12, 4)

