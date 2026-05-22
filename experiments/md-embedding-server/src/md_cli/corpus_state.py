from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .cost_ledger import cache_root


TTL_SECONDS = 30
_CACHE: dict[str, tuple[float, dict[str, Any] | None]] = {}


def quick_corpus_state(corpus_root: str | Path | None) -> dict[str, Any] | None:
    if not corpus_root:
        return None
    root = str(Path(corpus_root).expanduser().resolve())
    cached = _CACHE.get(root)
    if cached and time.time() - cached[0] < TTL_SECONDS:
        return cached[1]
    disk_cached = _read_disk_cache(root)
    if disk_cached and time.time() - disk_cached[0] < TTL_SECONDS:
        _CACHE[root] = disk_cached
        return disk_cached[1]
    state = _read_status(root)
    entry = (time.time(), state)
    _CACHE[root] = entry
    _write_disk_cache(root, entry)
    return state


def invalidate_corpus_state_cache(corpus_root: str | Path | None = None) -> None:
    if corpus_root is None:
        _CACHE.clear()
        return
    _CACHE.pop(str(Path(corpus_root).expanduser().resolve()), None)
    _delete_disk_cache(str(Path(corpus_root).expanduser().resolve()))


def _cache_path() -> Path:
    return cache_root() / "corpus-state-cache.json"


def _read_disk_cache(root: str) -> tuple[float, dict[str, Any] | None] | None:
    try:
        raw = json.loads(_cache_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    entry = raw.get(root)
    if not isinstance(entry, dict):
        return None
    fetched_at = entry.get("fetched_at")
    if not isinstance(fetched_at, (int, float)):
        return None
    state = entry.get("state")
    if state is not None and not isinstance(state, dict):
        return None
    return float(fetched_at), state


def _write_disk_cache(root: str, entry: tuple[float, dict[str, Any] | None]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    raw[root] = {"fetched_at": entry[0], "state": entry[1]}
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def _delete_disk_cache(root: str) -> None:
    path = _cache_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(raw, dict) or root not in raw:
        return
    raw.pop(root, None)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def _read_status(root: str) -> dict[str, Any] | None:
    try:
        from navigator.api import status
    except Exception:
        return None
    try:
        parsed = status(root)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    if parsed.get("_exit_code") not in {None, 0, 1}:
        return None
    return {
        "state": parsed.get("state"),
        "model": parsed.get("model"),
        "index_exists": parsed.get("index_exists", False),
        "last_touched": parsed.get("last_touched"),
        "added_sections": parsed.get("added_sections", 0),
        "removed_sections": parsed.get("removed_sections", 0),
        "pending_chunks": parsed.get("pending_chunks", 0),
        "drift_count": parsed.get("drift_count", 0),
        "metadata_mismatch": parsed.get("metadata_mismatch", False),
        "delta_too_large": parsed.get("delta_too_large", False),
        "recommended_action": parsed.get("recommended_action"),
    }
