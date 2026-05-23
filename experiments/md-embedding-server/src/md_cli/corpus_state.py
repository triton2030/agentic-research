from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterable

from .cost_ledger import cache_root


TTL_SECONDS = 30
CACHE_SCHEMA_VERSION = 2
_CACHE: dict[str, tuple[float, dict[str, Any] | None]] = {}


def quick_corpus_state(
    corpus_root: str | Path | None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any] | None:
    if not corpus_root:
        return None
    root = str(Path(corpus_root).expanduser().resolve())
    include = _list_filter(path_include)
    exclude = _list_filter(path_exclude)
    key = _cache_key(root, include, exclude)
    cached = _CACHE.get(key)
    if cached and time.time() - cached[0] < TTL_SECONDS:
        return _sanitize_state(cached[1])
    disk_cached = _read_disk_cache(key)
    if disk_cached and time.time() - disk_cached[0] < TTL_SECONDS:
        _CACHE[key] = disk_cached
        return disk_cached[1]
    state = _read_status(root, path_include=include, path_exclude=exclude)
    entry = (time.time(), state)
    _CACHE[key] = entry
    _write_disk_cache(key, entry)
    return state


def invalidate_corpus_state_cache(corpus_root: str | Path | None = None) -> None:
    if corpus_root is None:
        _CACHE.clear()
        return
    root = str(Path(corpus_root).expanduser().resolve())
    for key in [key for key in _CACHE if key == root or key.startswith(f"{root}::")]:
        _CACHE.pop(key, None)
    _delete_disk_cache(root)


def _cache_path() -> Path:
    return cache_root() / "corpus-state-cache.json"


def _read_disk_cache(key: str) -> tuple[float, dict[str, Any] | None] | None:
    try:
        raw = json.loads(_cache_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    entry = raw.get(key)
    if not isinstance(entry, dict):
        return None
    if entry.get("version") != CACHE_SCHEMA_VERSION:
        return None
    fetched_at = entry.get("fetched_at")
    if not isinstance(fetched_at, (int, float)):
        return None
    state = entry.get("state")
    if state is not None and not isinstance(state, dict):
        return None
    return float(fetched_at), _sanitize_state(state)


def _write_disk_cache(key: str, entry: tuple[float, dict[str, Any] | None]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    raw[key] = {
        "version": CACHE_SCHEMA_VERSION,
        "fetched_at": entry[0],
        "state": _sanitize_state(entry[1]),
    }
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
    if not isinstance(raw, dict):
        return
    for key in [key for key in raw if key == root or key.startswith(f"{root}::")]:
        raw.pop(key, None)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def _read_status(
    root: str,
    *,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> dict[str, Any] | None:
    try:
        from navigator.api import status
    except Exception:
        return None
    try:
        parsed = status(root, path_include=path_include, path_exclude=path_exclude)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    if parsed.get("_exit_code") not in {None, 0, 1}:
        return None
    return _sanitize_state({
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
    })


def _sanitize_state(state: dict[str, Any] | None) -> dict[str, Any] | None:
    if state is None:
        return None
    sanitized = dict(state)
    action = sanitized.get("recommended_action")
    if not isinstance(action, dict):
        return sanitized
    args = action.get("args")
    if not isinstance(args, dict):
        return sanitized
    if args.get("confirm") is True and not (
        args.get("transaction_id") or args.get("fingerprint")
    ):
        safe_args = dict(args)
        safe_args.pop("confirm", None)
        safe_args["dry_run"] = True
        sanitized["recommended_action"] = {**action, "args": safe_args}
    return sanitized


def _list_filter(value: Iterable[str] | str | None) -> list[str] | None:
    if value is None or value == []:
        return None
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value if item]


def _cache_key(root: str, path_include: list[str] | None, path_exclude: list[str] | None) -> str:
    if not path_include and not path_exclude:
        return root
    scope = json.dumps(
        {"path_include": path_include or [], "path_exclude": path_exclude or []},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"{root}::{scope}"
