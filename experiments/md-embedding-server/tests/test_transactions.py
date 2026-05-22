from __future__ import annotations

import json
import time
from pathlib import Path

from md_cli.transactions import (
    compute_fingerprint,
    consume_transaction,
    create_transaction,
    transaction_path,
    verify_fingerprint,
    verify_transaction,
)


def test_dry_run_creates_transaction_cache(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    assert txn["id"].startswith("txn_")
    assert transaction_path(txn["id"]).exists()


def test_confirm_matching_fingerprint_success(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    verified = verify_transaction(txn["id"], "md_strip", {"paths": [str(target)]})
    assert verified["ok"] is True
    consume_transaction(txn["id"])
    assert not transaction_path(txn["id"]).exists()


def test_confirm_stale_fingerprint_detects_drift(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    target.write_text("b", encoding="utf-8")
    verified = verify_transaction(txn["id"], "md_strip", {"paths": [str(target)]})
    assert verified["ok"] is False
    assert verified["reason"] == "drift_detected"


def test_confirm_wrong_tool_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    verified = verify_transaction(txn["id"], "md_init", {"paths": [str(target)]})
    assert verified["ok"] is False
    assert verified["reason"] == "tool_mismatch"


def test_confirm_expired_transaction_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    path = transaction_path(txn["id"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["expires_at"] = "2000-01-01T00:00:00+00:00"
    path.write_text(json.dumps(payload), encoding="utf-8")
    verified = verify_transaction(txn["id"], "md_strip", {"paths": [str(target)]})
    assert verified["ok"] is False
    assert verified["reason"] == "expired"


def test_stateless_fingerprint_fallback(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, _files = compute_fingerprint([target])
    assert verify_fingerprint([target], fingerprint)["ok"] is True
    target.write_text("b", encoding="utf-8")
    assert verify_fingerprint([target], fingerprint)["reason"] == "drift_detected"


def test_confirm_args_mismatch_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    other = tmp_path / "b.md"
    target.write_text("a", encoding="utf-8")
    other.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    verified = verify_transaction(txn["id"], "md_strip", {"paths": [str(other)]})
    assert verified["ok"] is False
    assert verified["reason"] == "args_mismatch"


def test_confirm_path_filter_mismatch_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction(
        "md_strip",
        {"paths": ["."], "path_include": ["a.md"], "path_exclude": None},
        fingerprint,
        files,
    )
    verified = verify_transaction(
        txn["id"],
        "md_strip",
        {"paths": ["."], "path_include": ["b.md"], "path_exclude": None},
    )
    assert verified["ok"] is False
    assert verified["reason"] == "args_mismatch"
    assert "path_include" in verified["mismatch"]


def test_confirm_affected_files_mismatch_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    other = tmp_path / "b.md"
    target.write_text("a", encoding="utf-8")
    other.write_text("b", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": ["."], "path_include": ["*.md"]}, fingerprint, files)
    verified = verify_transaction(
        txn["id"],
        "md_strip",
        {"paths": ["."], "path_include": ["*.md"]},
        confirm_files=[other],
    )
    assert verified["ok"] is False
    assert verified["reason"] == "affected_files_mismatch"
