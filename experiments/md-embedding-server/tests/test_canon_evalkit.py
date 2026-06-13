from __future__ import annotations

import json
from pathlib import Path

import pytest

from navigator.canon.evalkit import CaseResult, EvalCase, false_alarm, load_cases, owner_hit_at, render_markdown


def _case(kind: str = "conflict") -> EvalCase:
    return EvalCase(
        id="c1",
        source_file="source.md",
        claim_text="claim",
        expected_owner_file="owner.md",
        expected_line_hint=12,
        kind=kind,
        owner_role="authority",
        why_this_owner="unit test",
        source_last_verified="2026-06-11",
        expected_owner_glob=None,
    )


def test_load_cases_validates_schema(tmp_path: Path) -> None:
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([{"id": "x"}]), encoding="utf-8")

    with pytest.raises(ValueError):
        load_cases(path)


def test_metrics_and_markdown_render() -> None:
    result = CaseResult(
        case=_case(),
        mode="A",
        rows=[{"relative_path": "noise.md"}, {"relative_path": "owner.md"}],
        elapsed_ms=7,
    )
    clean = CaseResult(case=_case("clean"), mode="A", rows=[{"relative_path": "noise.md"}], elapsed_ms=9)

    assert owner_hit_at(result, 5) is True
    assert false_alarm(clean) is True
    report = render_markdown([result, clean])
    assert "| A (single) |" in report
    assert "| B (pack) |" not in report
    assert "Acceptance Matrix" in report
    assert "c1" in report
