from __future__ import annotations

import json
from pathlib import Path

from md_cli.envelope import wrap


ROOT = Path(__file__).resolve().parents[1]


def test_envelope_shape_matches_golden_keys_and_types() -> None:
    golden = json.loads((ROOT / "tests/golden/envelope_shape.json").read_text())
    actual = wrap({}, tool_name="md_ping", args={})["_envelope"]
    assert actual.keys() == golden.keys()
    for key, value in golden.items():
        if value == "__VOLATILE__":
            continue
        if isinstance(value, dict):
            assert isinstance(actual[key], dict)
            assert actual[key].keys() == value.keys()
            continue
        if isinstance(value, list):
            assert isinstance(actual[key], list)
            continue
        if value is None:
            assert actual[key] is None
            continue
        assert isinstance(actual[key], type(value))


def test_index_warmup_next_step_has_no_runnable_confirm() -> None:
    result = wrap(
        {"error": "index_warmup_required"},
        tool_name="md_search",
        args={"corpus": "knowledge", "query": "x"},
    )
    steps = result["_envelope"]["next_step"]
    assert steps[0] == {
        "tool": "md_index",
        "args": {"corpus": str((ROOT / "knowledge").resolve()), "dry_run": True},
        "reason": "Preview embedding cost before warming the index.",
    }
    assert all(step["args"].get("confirm") is not True for step in steps)
    assert steps[-1]["tool"] == "md_search"


def test_confirm_required_next_step_is_dry_run_only() -> None:
    result = wrap(
        {"error": "confirm_required"},
        tool_name="md_init",
        args={"paths": ["README.md"], "confirm": True},
    )
    steps = result["_envelope"]["next_step"]
    assert len(steps) == 1
    assert steps[0]["args"]["dry_run"] is True
    assert "confirm" not in steps[0]["args"]


def test_large_reply_size_estimate() -> None:
    result = wrap({"results": [{"text": "x" * 11_000}]}, tool_name="md_search", args={})
    estimate = result["_envelope"]["size_estimate"]
    assert estimate["large_reply"] is True
    assert estimate["items_returned"] == 1


def test_empty_search_suggests_broader_scope() -> None:
    result = wrap(
        {"empty": True},
        tool_name="md_search",
        args={"corpus": "knowledge", "query": "missing"},
    )
    assert result["_envelope"]["next_step"] == [
        {
            "tool": "md_search",
            "args": {"corpus": "knowledge", "query": "missing", "scope": "descriptions"},
            "reason": "Retry with scope='descriptions' for higher-level matching.",
        }
    ]

