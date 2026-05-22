from __future__ import annotations

from pathlib import Path

from navigator.workflows import edit_context, orient, query_by_type, refactor_candidates


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


def test_orient_compact_returns_status_map_and_importance() -> None:
    payload = orient(str(CORPUS), compact=True)

    assert payload["workflow"] == "md_orient"
    assert payload["compact"] is True
    assert payload["status"]["state"] in {"NO_INDEX", "FRESH", "HEALTHY", "NEEDS_WARMUP", "NEEDS_REBUILD"}
    assert payload["files"]["file_count"] == 2
    assert payload["importance"]["files"]


def test_edit_context_strict_returns_only_blocker_summary() -> None:
    payload = edit_context(str(README), scan=str(CORPUS), mode="strict")

    assert payload["workflow"] == "md_edit_context"
    assert payload["mode"] == "strict"
    assert "blockers" in payload
    assert "related" not in payload
    assert "search" not in payload


def test_profile_backed_workflows_fail_closed_on_cold_corpus() -> None:
    for payload in (
        query_by_type(str(CORPUS), ["rule"]),
        refactor_candidates(str(CORPUS), compact=True),
    ):
        assert payload["error"] == "index_warmup_required"
        assert payload["_exit_code"] == 4
