from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from md_cli.transactions import (
    compute_fingerprint,
    create_transaction,
    transaction_path,
    verify_and_consume_transaction,
    verify_fingerprint,
    verify_transaction,
)


ROOT = Path(__file__).resolve().parents[1]


def _txn(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    return target, txn


def test_args_mismatch(monkeypatch, tmp_path: Path) -> None:
    target, txn = _txn(monkeypatch, tmp_path)
    other = tmp_path / "b.md"
    other.write_text("a", encoding="utf-8")
    result = verify_transaction(txn["id"], "md_strip", {"paths": [str(other)]})
    assert result["reason"] == "args_mismatch"


def test_double_confirm(monkeypatch, tmp_path: Path) -> None:
    target, txn = _txn(monkeypatch, tmp_path)
    assert verify_and_consume_transaction(txn["id"], "md_strip", {"paths": [str(target)]})["ok"]
    assert verify_and_consume_transaction(txn["id"], "md_strip", {"paths": [str(target)]})["reason"] == "unknown"


def test_concurrent_confirm_race(tmp_path: Path) -> None:
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    env = os.environ.copy()
    env["MD_TOOLS_CACHE_DIR"] = str(tmp_path / "cache")
    env["PYTHONPATH"] = str(ROOT / "src")
    fingerprint, files = compute_fingerprint([target])
    os.environ["MD_TOOLS_CACHE_DIR"] = str(tmp_path / "cache")
    txn = create_transaction("md_strip", {"paths": [str(target)]}, fingerprint, files)
    code = (
        "import json; "
        "from md_cli.transactions import verify_and_consume_transaction; "
        f"print(json.dumps(verify_and_consume_transaction({txn['id']!r}, 'md_strip', {{'paths': [{str(target)!r}]}})))"
    )
    procs = [
        subprocess.Popen([sys.executable, "-c", code], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE)
        for _ in range(2)
    ]
    results = [json.loads(proc.communicate(timeout=10)[0]) for proc in procs]
    assert [result["ok"] for result in results].count(True) == 1


def test_corrupt_txn_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    path = transaction_path("txn_bad")
    path.parent.mkdir(parents=True)
    path.write_text("{not-json", encoding="utf-8")
    assert verify_transaction("txn_bad", "md_strip")["reason"] == "unknown"


def test_confirm_without_token_or_fingerprint_is_not_stateless(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    assert verify_fingerprint([target], "bad")["reason"] == "drift_detected"


def _make_txn(monkeypatch, tmp_path: Path, corpus_value: str) -> tuple[Path, dict[str, str]]:
    """Helper for path-normalization adversarial tests."""
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    target = tmp_path / "a.md"
    target.write_text("a", encoding="utf-8")
    fingerprint, files = compute_fingerprint([target])
    txn = create_transaction("md_index", {"corpus": corpus_value}, fingerprint, files)
    return target, txn


def test_intent_normalizes_relative_vs_absolute_corpus(monkeypatch, tmp_path: Path) -> None:
    """dry-run with relative corpus + confirm with absolute (same place) → no args_mismatch."""
    monkeypatch.chdir(tmp_path)
    # dry-run records corpus="." (relative)
    _, txn = _make_txn(monkeypatch, tmp_path, ".")
    # confirm uses absolute path to the same directory
    result = verify_transaction(txn["id"], "md_index", {"corpus": str(tmp_path)})
    assert result["ok"], f"expected ok, got {result!r}"


def test_intent_normalizes_tilde_expansion(monkeypatch, tmp_path: Path) -> None:
    """Tilde-expanded path must match expanded form."""
    monkeypatch.setenv("HOME", str(tmp_path))
    _, txn = _make_txn(monkeypatch, tmp_path, "~/repo")
    # Confirm uses the resolved equivalent
    resolved = str((tmp_path / "repo").resolve())
    result = verify_transaction(txn["id"], "md_index", {"corpus": resolved})
    assert result["ok"], f"expected ok, got {result!r}"


def test_intent_normalizes_paths_list(monkeypatch, tmp_path: Path) -> None:
    """List-valued PATH-like keys normalize per element."""
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.chdir(tmp_path)
    a = tmp_path / "a.md"
    a.write_text("a", encoding="utf-8")
    b = tmp_path / "b.md"
    b.write_text("b", encoding="utf-8")
    fingerprint, files = compute_fingerprint([a, b])
    txn = create_transaction("md_init", {"paths": ["a.md", "b.md"]}, fingerprint, files)
    result = verify_transaction(
        txn["id"],
        "md_init",
        {"paths": [str(a), str(b)]},
    )
    assert result["ok"], f"expected ok, got {result!r}"


def test_intent_still_catches_different_paths(monkeypatch, tmp_path: Path) -> None:
    """Normalization must not mask actual user mistakes — different paths still mismatch."""
    monkeypatch.chdir(tmp_path)
    _, txn = _make_txn(monkeypatch, tmp_path, "./docs")
    result = verify_transaction(txn["id"], "md_index", {"corpus": "./other"})
    assert result["reason"] == "args_mismatch", f"expected args_mismatch, got {result!r}"

