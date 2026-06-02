from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from md_cli.catalog import TOOLS_BY_ID


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_RESPONSES = ROOT / "tests" / "golden" / "mcp-responses"


def test_response_snapshots_cover_every_catalog_tool() -> None:
    snapshot_names = {path.stem for path in GOLDEN_RESPONSES.glob("md_*.json")}
    assert snapshot_names == set(TOOLS_BY_ID)


def test_response_snapshots_use_generated_wrapper_shape() -> None:
    for path in sorted(GOLDEN_RESPONSES.glob("md_*.json")):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        assert set(snapshot) == {"tool", "canonical_args", "is_error", "payload"}
        assert snapshot["tool"] == path.stem
        assert isinstance(snapshot["canonical_args"], dict)
        assert isinstance(snapshot["is_error"], bool)
        assert isinstance(snapshot["payload"], dict)
        assert "_envelope" in snapshot["payload"]


def test_preflight_snapshot_includes_edit_plan_contract() -> None:
    snapshot = json.loads((GOLDEN_RESPONSES / "md_preflight.json").read_text(encoding="utf-8"))
    payload = snapshot["payload"]
    assert "edit_plan" in payload
    assert {"must_update", "also_check", "must_read", "to_clear"} <= set(payload["edit_plan"])


def test_agent_facing_response_snapshots_do_not_suggest_legacy_cli() -> None:
    offenders: list[str] = []
    for path in sorted(GOLDEN_RESPONSES.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))["payload"]
        for json_path, value in _string_values(payload):
            if "md_navigator.py" not in value:
                continue
            offenders.append(f"{path.name}:{json_path}")

    assert not offenders, "legacy md_navigator.py leaked into agent-facing hints: " + ", ".join(offenders)


def _string_values(value: Any, prefix: str = ""):
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from _string_values(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            yield from _string_values(item, child)
