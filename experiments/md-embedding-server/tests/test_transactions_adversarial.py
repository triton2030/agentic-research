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
    # Second consume of the same id must be distinguishable as already-applied,
    # not a generic "unknown" — agents must know the mutation succeeded once.
    assert (
        verify_and_consume_transaction(txn["id"], "md_strip", {"paths": [str(target)]})["reason"]
        == "transaction_consumed"
    )


def test_unknown_id_is_not_found(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    # No transaction has ever been created with this id.
    assert (
        verify_and_consume_transaction("txn_never_existed", "md_strip")["reason"]
        == "transaction_not_found"
    )


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
    # The loser must see transaction_consumed, not transaction_not_found —
    # otherwise the agent can't tell "race lost" apart from "bad id".
    losers = [result.get("reason") for result in results if not result["ok"]]
    assert losers == ["transaction_consumed"], f"expected one consumed loser, got {losers!r}"


def test_corrupt_txn_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    path = transaction_path("txn_bad")
    path.parent.mkdir(parents=True)
    path.write_text("{not-json", encoding="utf-8")
    # Corrupt JSON from an agent's perspective is "this id is unusable" —
    # surfaced as transaction_not_found to route them through fresh --dry-run.
    assert verify_transaction("txn_bad", "md_strip")["reason"] == "transaction_not_found"


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


def test_consumed_sentinel_persists_after_success(monkeypatch, tmp_path: Path) -> None:
    """After successful consume the .consumed sentinel must survive on disk
    so a second confirm with the same id can be distinguished from never-existed."""
    target, txn = _txn(monkeypatch, tmp_path)
    assert verify_and_consume_transaction(txn["id"], "md_strip", {"paths": [str(target)]})["ok"]
    sentinel = transaction_path(txn["id"]).with_suffix(".consumed")
    assert sentinel.exists(), "sentinel file should remain after consume"
    # Original txn file is gone.
    assert not transaction_path(txn["id"]).exists()


def test_consumed_gc_runs_after_grace_period(monkeypatch, tmp_path: Path) -> None:
    """gc_expired must clean .consumed sentinels older than 2 * TXN_TTL_SECONDS,
    so the cache doesn't grow unbounded."""
    import time as _time
    from md_cli import transactions as txns

    target, txn = _txn(monkeypatch, tmp_path)
    assert verify_and_consume_transaction(txn["id"], "md_strip", {"paths": [str(target)]})["ok"]
    sentinel = transaction_path(txn["id"]).with_suffix(".consumed")
    assert sentinel.exists()
    # Backdate mtime past 2 * TTL grace.
    old_time = _time.time() - 3 * txns.TXN_TTL_SECONDS
    os.utime(sentinel, (old_time, old_time))
    txns.gc_expired()
    assert not sentinel.exists(), "gc should have removed expired sentinel"


def test_sentinel_rename_failure_rolls_back_claim(monkeypatch, tmp_path: Path) -> None:
    """If sentinel write fails (OSError), the claim must be rolled back so the
    transaction can be re-attempted — and the caller sees internal_error,
    not a silent inconsistency."""
    from pathlib import Path as _Path

    target, txn = _txn(monkeypatch, tmp_path)
    original_rename = _Path.rename
    calls = {"n": 0}

    def flaky_rename(self, target_path):
        calls["n"] += 1
        # First rename: path → .claim (succeeds).
        # Second rename: .claim → .consumed (fail).
        # Third rename (rollback): .claim → path (must succeed).
        if calls["n"] == 2:
            raise OSError("disk full")
        return original_rename(self, target_path)

    monkeypatch.setattr(_Path, "rename", flaky_rename)
    result = verify_and_consume_transaction(txn["id"], "md_strip", {"paths": [str(target)]})
    assert result == {
        "ok": False,
        "reason": "internal_error",
        "detail": "sentinel write failed: disk full",
    }
    # Claim was rolled back — txn file lives again, sentinel does not.
    assert transaction_path(txn["id"]).exists()
    assert not transaction_path(txn["id"]).with_suffix(".consumed").exists()

