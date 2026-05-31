from __future__ import annotations

from pathlib import Path

from navigator.workflows import edit_context, orient, query_by_type, refactor_candidates


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


def test_orient_normal_returns_status_map_and_importance() -> None:
    payload = orient(str(CORPUS))

    assert payload["workflow"] == "md_orient"
    assert payload["expanded"] is False
    assert payload["status"]["state"] in {"NO_INDEX", "FRESH", "HEALTHY", "NEEDS_WARMUP", "NEEDS_REBUILD"}
    assert payload["shape"]["file_count"] == 2
    assert payload["shape"]["folders"]
    assert "start_here" in payload


def test_orient_expanded_returns_full_map() -> None:
    payload = orient(str(CORPUS), expanded=True)

    assert payload["workflow"] == "md_orient"
    assert payload["expanded"] is True
    assert payload["files"]["files"][0]["headings"]


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


def test_refactor_candidates_read_next_preserves_thresholds(monkeypatch) -> None:
    import navigator.api_profile as api_profile
    import navigator.refactor_proposals as refactor_proposals
    import navigator.section_profile as section_profile

    monkeypatch.setattr(section_profile, "open_profile_db", lambda _root: object())
    monkeypatch.setattr(api_profile, "_profiled_section_count", lambda *_args, **_kwargs: 1)

    def fake_compute(_conn, **kwargs):
        assert kwargs["top"] == 4
        assert kwargs["uniqueness_threshold"] == 0.22
        assert kwargs["owner_confidence_threshold"] == 0.66
        return {"proposals": [], "method": "fake", "thresholds": {}, "no_automation": True}

    monkeypatch.setattr(refactor_proposals, "refactor_candidates", fake_compute)

    payload = refactor_candidates(
        "corpus",
        top=4,
        uniqueness_threshold=0.22,
        owner_confidence_threshold=0.66,
        path_include=["docs/**"],
        path_exclude=["old/**"],
    )

    args = payload["read_next"][0]["args"]
    assert args["top"] == 4
    assert args["uniqueness_threshold"] == 0.22
    assert args["owner_confidence_threshold"] == 0.66
    assert args["path_include"] == ["docs/**"]
    assert args["path_exclude"] == ["old/**"]
