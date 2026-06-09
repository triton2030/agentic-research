from __future__ import annotations

import json
import os
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path

from md_cli.catalog import COST_AWARE_TOOLS, TOOLS, TRANSACTION_REQUIRED_TOOLS
from md_cli.handlers import _generic


ROOT = Path(__file__).resolve().parents[1]


def _run_md(cwd: Path, *args: str) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "md_cli", *args, "--json"],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (args, result.stderr, result.stdout)
    return json.loads(result.stdout)


def test_mutating_dry_runs_share_guard_shape(tmp_path: Path) -> None:
    (tmp_path / "plain.md").write_text("# Plain\n", encoding="utf-8")
    (tmp_path / "legacy.md").write_text(
        "---\ndescription: Legacy\ndepends-on: []\nowner: old\n---\n\n# Legacy\n",
        encoding="utf-8",
    )

    commands = {
        "md_init": ["init", "--paths", "plain.md", "--dry-run"],
        "md_strip": ["strip", "--paths", "legacy.md", "--dry-run"],
        "md_index": ["index", str(tmp_path), "--dry-run"],
        "md_profile_sections": ["profile-sections", str(tmp_path), "--dry-run", "--mode", "llm"],
    }

    for tool_id, argv in commands.items():
        payload = _run_md(tmp_path, *argv)
        assert payload["_envelope"]["tool"] == tool_id
        assert payload["dry_run"] is True
        # Schema 2.0.0: lock handle lives in envelope; payload keeps only data.
        lock = payload["_envelope"]["lock"]
        assert lock["transaction_id"].startswith("txn_")
        assert len(lock["fingerprint"]) == 32
        assert isinstance(payload["files"], list)
        assert "transaction_id" not in payload


def test_mutating_guard_scope_comes_from_catalog() -> None:
    mutating_tools = {tool.name for tool in TOOLS if tool.category == "mutating"}
    assert mutating_tools == {"md_index", "md_init", "md_profile_sections", "md_strip"}
    transaction_tools = {tool.name for tool in TOOLS if tool.requires_transaction({})}
    cost_aware_tools = {tool.name for tool in TOOLS if tool.is_cost_bearing({})}
    assert transaction_tools == set(TRANSACTION_REQUIRED_TOOLS)
    assert transaction_tools == mutating_tools
    assert all(tool.transaction_required for tool in TOOLS if tool.name in transaction_tools)
    assert {"md_search", "md_index", "md_profile_sections"} <= cost_aware_tools
    assert cost_aware_tools == set(COST_AWARE_TOOLS)

    generic_source = (ROOT / "src" / "md_cli" / "handlers" / "_generic.py").read_text(encoding="utf-8")
    catalog_source = (ROOT / "src" / "md_cli" / "catalog.py").read_text(encoding="utf-8")
    assert "MUTATING_TOOLS" not in generic_source
    assert "md_profile_sections" not in generic_source
    assert "requires_transaction" in generic_source
    assert "return self.transaction_required" in catalog_source
    assert "return self.name in TRANSACTION_REQUIRED_TOOLS" not in catalog_source
    assert "return self.category == \"mutating\"" not in catalog_source


def test_transaction_control_args_do_not_reach_target_callable() -> None:
    seen: dict[str, object] = {}

    def target(**kwargs: object) -> dict[str, object]:
        seen.update(kwargs)
        return {"ok": True}

    result = _generic._call(
        target,
        {
            "corpus": "docs",
            "confirm": True,
            "transaction_id": "txn_123",
            "fingerprint": "abc",
        },
    )

    assert result.exit_code == 0
    assert seen == {"corpus": "docs", "confirm": True}


def test_fingerprint_confirm_returns_preview_failure() -> None:
    def target(**kwargs: object) -> dict[str, object]:
        if kwargs.get("dry_run"):
            return {"_exit_code": 2, "error": "preview_failed"}
        return {"ok": True}

    result = _generic._run_mutating(
        "md_init",
        target,
        SimpleNamespace(confirm=True, fingerprint="bad"),
        {"confirm": True, "fingerprint": "bad"},
    )

    assert result.exit_code == 2
    assert result.payload["error"] == "preview_failed"


def test_affected_files_contract_uses_preview_keys_only() -> None:
    assert _generic._affected_files({"affected_files": ["a.md"]}) == ["a.md"]
    assert _generic._affected_files({"files_to_modify": ["b.md"]}) == ["b.md"]
    assert _generic._affected_files({"modified": ["c.md"], "files": ["d.md"]}) == []
