from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from navigator.markdown_io import parse_frontmatter


ROOT = Path(__file__).resolve().parents[1]


def _run_md(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args, "--json"],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


def test_init_requires_dry_run_then_allows_fingerprint_confirm(tmp_path: Path) -> None:
    doc = tmp_path / "plain.md"
    doc.write_text("# Plain\n\nBody.\n", encoding="utf-8")

    blocked = _run_md(tmp_path, "init", "--paths", "plain.md", "--confirm")
    assert blocked.returncode == 1
    assert _json(blocked)["error"] == "transaction_required"

    dry = _run_md(tmp_path, "init", "--paths", "plain.md", "--dry-run")
    dry_payload = _json(dry)
    assert dry.returncode == 0
    assert dry_payload["files_to_modify"] == [str(doc)]

    confirmed = _run_md(
        tmp_path,
        "init",
        "--paths",
        "plain.md",
        "--confirm",
        "--fingerprint",
        str(dry_payload["_envelope"]["lock"]["fingerprint"]),
    )
    assert confirmed.returncode == 0
    frontmatter = parse_frontmatter(doc.read_text(encoding="utf-8").splitlines())
    assert frontmatter["description"] == "TODO"


def test_strip_detects_fingerprint_drift_and_transaction_confirm(tmp_path: Path) -> None:
    doc = tmp_path / "legacy.md"
    doc.write_text(
        "---\n"
        "description: Legacy\n"
        "depends-on: []\n"
        "owner: old\n"
        "---\n"
        "\n"
        "# Legacy\n",
        encoding="utf-8",
    )

    dry = _run_md(tmp_path, "strip", "--paths", "legacy.md", "--dry-run")
    dry_payload = _json(dry)
    doc.write_text(doc.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")

    stale = _run_md(
        tmp_path,
        "strip",
        "--paths",
        "legacy.md",
        "--confirm",
        "--fingerprint",
        str(dry_payload["_envelope"]["lock"]["fingerprint"]),
    )
    assert stale.returncode == 1
    assert _json(stale)["error"] == "drift_detected"

    fresh = _run_md(tmp_path, "strip", "--paths", "legacy.md", "--dry-run")
    confirmed = _run_md(
        tmp_path,
        "strip",
        "--paths",
        "legacy.md",
        "--confirm",
        "--transaction-id",
        str(_json(fresh)["_envelope"]["lock"]["transaction_id"]),
    )
    assert confirmed.returncode == 0
    assert "owner:" not in doc.read_text(encoding="utf-8")


def test_strip_transaction_rejects_changed_path_filter(tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    content = (
        "---\n"
        "description: Legacy\n"
        "depends-on: []\n"
        "owner: old\n"
        "---\n\n"
        "# Legacy\n"
    )
    a.write_text(content, encoding="utf-8")
    b.write_text(content, encoding="utf-8")

    dry = _run_md(tmp_path, "strip", "--paths", ".", "--path-include", "a.md", "--dry-run")
    assert dry.returncode == 0

    changed_scope = _run_md(
        tmp_path,
        "strip",
        "--paths",
        ".",
        "--path-include",
        "b.md",
        "--confirm",
        "--transaction-id",
        str(_json(dry)["_envelope"]["lock"]["transaction_id"]),
    )
    assert changed_scope.returncode == 1
    assert _json(changed_scope)["error"] == "args_mismatch"
    assert "owner:" in b.read_text(encoding="utf-8")


def test_index_dry_run_returns_cost_and_profile_llm_requires_confirm(tmp_path: Path) -> None:
    (tmp_path / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")

    index = _run_md(tmp_path, "index", str(tmp_path), "--dry-run")
    assert index.returncode == 0
    index_payload = _json(index)
    assert index_payload["pending_chunks"] >= 1
    assert "estimated_cost_usd" in index_payload

    profile = _run_md(tmp_path, "profile-sections", str(tmp_path), "--mode", "llm")
    assert profile.returncode == 1
    assert _json(profile)["error"] == "confirm_required"

    heuristic_profile = _run_md(tmp_path, "profile-sections", str(tmp_path), "--mode", "heuristic")
    assert heuristic_profile.returncode == 1
    assert _json(heuristic_profile)["error"] == "confirm_required"


def test_index_dry_run_vacuum_returns_preview(tmp_path: Path) -> None:
    (tmp_path / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")

    result = _run_md(tmp_path, "index", str(tmp_path), "--dry-run", "--vacuum")

    assert result.returncode == 0
    payload = _json(result)
    assert payload["vacuum"]["requested"] is True
    assert payload["vacuum"]["would_run"] is False
    assert payload["vacuum"]["reason"] == "no_index"


def test_index_detects_config_drift_between_dry_run_and_confirm(
    tmp_path: Path,
) -> None:
    (tmp_path / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")

    dry = _run_md(tmp_path, "index", str(tmp_path), "--dry-run")
    assert dry.returncode == 0
    payload = _json(dry)
    files = payload["files"]
    assert {"path": ".md-tools.toml", "hash": "MISSING"} in files

    (tmp_path / ".md-tools.toml").write_text("[index]\n", encoding="utf-8")

    stale = _run_md(
        tmp_path,
        "index",
        str(tmp_path),
        "--confirm",
        "--transaction-id",
        str(payload["_envelope"]["lock"]["transaction_id"]),
    )
    assert stale.returncode == 1
    assert _json(stale)["error"] == "drift_detected"


def test_index_refuses_nested_corpus_when_parent_index_exists(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    child = parent / "child"
    child.mkdir(parents=True)
    (child / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")
    (parent / ".md-navigator").mkdir()
    (parent / ".md-navigator" / "index.sqlite").write_bytes(b"")

    blocked = _run_md(tmp_path, "index", str(child), "--dry-run")
    assert blocked.returncode == 1
    payload = _json(blocked)
    assert payload["error"] == "nested_corpus_refused"
    assert payload["requested_corpus"] == str(child)
    assert payload["parent_corpus"] == str(parent)
    assert payload["suggested_index_args"]["corpus"] == str(parent)
    assert payload["suggested_index_args"]["path_include"] == ["child/**"]
    assert not (child / ".md-navigator").exists()

    allowed = _run_md(
        tmp_path,
        "index",
        str(child),
        "--dry-run",
        "--allow-nested-corpus",
    )
    assert allowed.returncode == 0
    assert _json(allowed)["pending_chunks"] >= 1
    assert not (child / ".md-navigator").exists()
