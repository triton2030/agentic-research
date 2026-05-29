from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

from md_cli.catalog import TOOLS, TOOLS_BY_ID


ROOT = Path(__file__).resolve().parents[1]


def test_catalog_contains_32_entries() -> None:
    assert len(TOOLS) == 32
    assert len(TOOLS_BY_ID) == 32


def test_catalog_names_match_mcp_snapshot() -> None:
    snapshot = json.loads((ROOT / "tests/golden/mcp-tool-snapshot.json").read_text())
    assert sorted(TOOLS_BY_ID) == sorted(tool["name"] for tool in snapshot["tools"])


def test_catalog_values_match_mcp_snapshot_without_runtime_patching() -> None:
    snapshot = json.loads((ROOT / "tests/golden/mcp-tool-snapshot.json").read_text())
    for tool in snapshot["tools"]:
        assert TOOLS_BY_ID[tool["name"]].to_dict() == tool

    source = (ROOT / "src/md_cli/catalog.py").read_text(encoding="utf-8")
    assert "$schema" not in source
    assert "object.__setattr__" not in source
    assert "input_schema.pop" not in source
    assert "for _tool in TOOLS_BY_ID.values()" not in source
    assert "setdefault(\"fingerprint\"" not in source
    assert "COMMON_ARG_HELP" not in (ROOT / "src/md_cli/main.py").read_text(encoding="utf-8")


def test_catalog_required_fields_and_import_targets() -> None:
    for tool in TOOLS:
        assert tool.name
        assert tool.category in {"atomic", "workflow", "mutating"}
        assert tool.description["when"]
        assert tool.description["input"]
        assert tool.description["output"]
        assert tool.input_schema["type"] == "object"
        assert bool(tool.library_function) ^ bool(tool.workflow_function)
        importlib.import_module(tool.handler_module)
        importlib.import_module(tool.tests_module)
        target = tool.library_function or tool.workflow_function
        assert target is not None
        module_name, attr = target.rsplit(".", 1)
        assert hasattr(importlib.import_module(module_name), attr)


def test_catalog_input_properties_have_help_descriptions() -> None:
    missing = []
    for tool in TOOLS:
        properties = tool.input_schema.get("properties") or {}
        for name, schema in properties.items():
            if not str(schema.get("description", "")).strip():
                missing.append(f"{tool.name}.{name}")
    assert missing == []


def _run_md(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_md_tools_json_returns_catalog_with_envelope() -> None:
    result = _run_md("tools", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload["tools"]) == 32
    assert payload["_envelope"]["tool"] == "md_tools"


def test_md_tools_one_tool_human_detail() -> None:
    result = _run_md("tools", "md_orient")
    assert result.returncode == 0
    assert "WHEN:" in result.stdout
    assert "md orient" in result.stdout


def test_md_tools_unknown_returns_2() -> None:
    result = _run_md("tools", "missing", "--json")
    assert result.returncode == 2
    assert json.loads(result.stdout)["error"] == "unknown_tool"
