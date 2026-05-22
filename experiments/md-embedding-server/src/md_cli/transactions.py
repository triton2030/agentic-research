from __future__ import annotations

import hashlib
import json
import os
import time
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .cost_ledger import cache_root


TXN_TTL_SECONDS = 5 * 60
CONTROL_KEYS = {"dry_run", "confirm", "transaction_id", "fingerprint", "json", "subcommand"}


def compute_fingerprint(file_paths: Iterable[str | Path]) -> tuple[str, list[dict[str, str]]]:
    entries = []
    for raw_path in file_paths:
        path = str(Path(raw_path).expanduser().resolve())
        try:
            content = Path(path).read_bytes()
        except FileNotFoundError:
            short_hash = "MISSING"
        except OSError:
            short_hash = "UNREADABLE"
        else:
            short_hash = hashlib.sha256(content).hexdigest()[:16]
        entries.append({"path": path, "hash": short_hash})
    entries.sort(key=lambda item: item["path"])
    combined = "\n".join(f"{item['path']}:{item['hash']}" for item in entries)
    fingerprint = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:32]
    return fingerprint, entries


def create_transaction(
    tool: str,
    args: dict[str, Any],
    fingerprint: str,
    files: list[dict[str, str]],
) -> dict[str, Any]:
    gc_expired()
    txn_id = f"txn_{os.urandom(8).hex()}"
    now = time.time()
    txn = {
        "id": txn_id,
        "tool": tool,
        "args": _jsonable_args(args),
        "intent": canonical_intent(args),
        "cwd": str(Path.cwd().resolve()),
        "fingerprint": fingerprint,
        "files": files,
        "created_at": _iso(now),
        "expires_at": _iso(now + TXN_TTL_SECONDS),
    }
    path = transaction_path(txn_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(txn, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    return {"id": txn_id, "expires_at": txn["expires_at"]}


def verify_transaction(
    transaction_id: str,
    expected_tool: str,
    confirm_args: dict[str, Any] | None = None,
    confirm_files: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    txn = _read_transaction(transaction_id)
    if txn is None:
        return {"ok": False, "reason": "unknown"}
    return _verify_loaded_transaction(txn, expected_tool, confirm_args, confirm_files)


def verify_and_consume_transaction(
    transaction_id: str,
    expected_tool: str,
    confirm_args: dict[str, Any] | None = None,
    confirm_files: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    path = transaction_path(transaction_id)
    claimed = path.with_name(f"{path.name}.{os.getpid()}.claim")
    try:
        path.rename(claimed)
    except FileNotFoundError:
        return {"ok": False, "reason": "unknown"}
    txn = _read_transaction_path(claimed)
    if txn is None:
        with suppress(FileNotFoundError):
            claimed.unlink()
        return {"ok": False, "reason": "unknown"}
    verified = _verify_loaded_transaction(txn, expected_tool, confirm_args, confirm_files)
    if verified["ok"]:
        with suppress(FileNotFoundError):
            claimed.unlink()
    else:
        try:
            claimed.rename(path)
        except OSError:
            pass
    return verified


def _verify_loaded_transaction(
    txn: dict[str, Any],
    expected_tool: str,
    confirm_args: dict[str, Any] | None = None,
    confirm_files: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    if _parse_iso(txn["expires_at"]) < time.time():
        return {"ok": False, "reason": "expired", "txn": txn}
    if txn.get("tool") != expected_tool:
        return {
            "ok": False,
            "reason": "tool_mismatch",
            "expected": expected_tool,
            "got": txn.get("tool"),
        }
    if confirm_args is not None:
        expected_cwd = txn.get("cwd")
        current_cwd = str(Path.cwd().resolve())
        if expected_cwd and expected_cwd != current_cwd:
            return {"ok": False, "reason": "cwd_mismatch", "expected": expected_cwd, "got": current_cwd}
        if "intent" in txn:
            mismatch = _intent_mismatch(txn.get("intent", {}), canonical_intent(confirm_args))
        else:
            mismatch = _intent_mismatch(canonical_intent(txn.get("args", {})), canonical_intent(confirm_args))
        if mismatch:
            return {"ok": False, "reason": "args_mismatch", "mismatch": mismatch, "txn": txn}
    if confirm_files is not None:
        _confirm_fingerprint, confirm_file_entries = compute_fingerprint(confirm_files)
        original_file_set = _file_set(txn.get("files", []))
        confirm_file_set = _file_set(confirm_file_entries)
        if confirm_file_set != original_file_set:
            return {
                "ok": False,
                "reason": "affected_files_mismatch",
                "original_files": txn.get("files", []),
                "confirm_files": confirm_file_entries,
            }
    current_fingerprint, current_files = compute_fingerprint(
        item["path"] for item in txn.get("files", [])
    )
    if current_fingerprint != txn.get("fingerprint"):
        return {
            "ok": False,
            "reason": "drift_detected",
            "original_fingerprint": txn.get("fingerprint"),
            "current_fingerprint": current_fingerprint,
            "original_files": txn.get("files", []),
            "current_files": current_files,
        }
    return {"ok": True, "txn": txn}


def verify_fingerprint(file_paths: Iterable[str | Path], expected_fingerprint: str) -> dict[str, Any]:
    current_fingerprint, files = compute_fingerprint(file_paths)
    if current_fingerprint != expected_fingerprint:
        return {
            "ok": False,
            "reason": "drift_detected",
            "original_fingerprint": expected_fingerprint,
            "current_fingerprint": current_fingerprint,
            "current_files": files,
        }
    return {"ok": True, "fingerprint": current_fingerprint, "files": files}


def consume_transaction(transaction_id: str) -> None:
    path = transaction_path(transaction_id)
    tmp = path.with_suffix(".consuming")
    try:
        path.rename(tmp)
    except FileNotFoundError:
        return
    try:
        tmp.unlink()
    except FileNotFoundError:
        pass


def gc_expired() -> None:
    directory = transactions_dir()
    if not directory.exists():
        return
    now = time.time()
    for path in directory.glob("txn_*.json"):
        txn = _read_transaction_path(path)
        if txn is None or _parse_iso(txn.get("expires_at", "")) < now:
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def transactions_dir() -> Path:
    return cache_root() / "transactions"


def transaction_path(transaction_id: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "-" for ch in transaction_id)
    return transactions_dir() / f"{safe}.json"


def _read_transaction(transaction_id: str) -> dict[str, Any] | None:
    return _read_transaction_path(transaction_path(transaction_id))


def _read_transaction_path(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _jsonable_args(args: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in args.items():
        if key.startswith("_"):
            continue
        if isinstance(value, Path):
            out[key] = str(value)
        elif isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value
        elif isinstance(value, (list, tuple)):
            out[key] = [str(item) if isinstance(item, Path) else item for item in value]
        else:
            out[key] = str(value)
    return out


def canonical_intent(args: dict[str, Any]) -> dict[str, Any]:
    jsonable = _jsonable_args(args)
    return {
        key: jsonable[key]
        for key in sorted(jsonable)
        if not key.startswith("_") and key not in CONTROL_KEYS
    }


def _intent_mismatch(original_args: dict[str, Any], confirm_args: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mismatches = {}
    original = canonical_intent(original_args)
    confirm = canonical_intent(confirm_args)
    for key in sorted(set(original) | set(confirm)):
        left = original.get(key)
        right = confirm.get(key)
        if left != right:
            mismatches[key] = {"dry_run": left, "confirm": right}
    return mismatches


def _file_set(files: Iterable[dict[str, str]]) -> list[str]:
    return sorted(str(Path(item["path"]).expanduser().resolve()) for item in files if "path" in item)


def _iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def _parse_iso(value: str) -> float:
    try:
        return datetime.fromisoformat(value).timestamp()
    except (TypeError, ValueError):
        return 0.0
