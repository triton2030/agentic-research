from __future__ import annotations

import time
from pathlib import Path

import navigator.api as api
from navigator.workflows.section_blast_radius import section_blast_radius


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


def test_section_blast_radius_requires_query() -> None:
    payload = section_blast_radius(str(README), str(CORPUS), "")

    assert payload["error"] == "query_required"
    assert payload["_exit_code"] == 2


def test_section_blast_radius_keeps_graph_and_semantic_layers() -> None:
    payload = section_blast_radius(
        str(README),
        str(CORPUS),
        "sample frontmatter contract",
        scan=str(CORPUS),
    )

    assert payload["workflow"] == "md_section_blast_radius"
    assert payload["graph"]["command"] == "preflight"
    assert payload["semantic"]["error"] == "index_warmup_required"
    assert payload["semantic"]["_exit_code"] == 4


def test_section_blast_radius_runs_graph_and_semantic_in_parallel(monkeypatch) -> None:
    def slow_preflight(*args, **kwargs):
        time.sleep(0.2)
        return {"command": "preflight"}

    def slow_search(*args, **kwargs):
        time.sleep(0.2)
        return {"results": []}

    monkeypatch.setattr(api, "preflight", slow_preflight)
    monkeypatch.setattr(api, "search", slow_search)

    started = time.perf_counter()
    payload = section_blast_radius(str(README), str(CORPUS), "parallel check")
    elapsed = time.perf_counter() - started

    assert payload["graph"] == {"command": "preflight"}
    assert payload["semantic"] == {"results": []}
    assert elapsed < 0.35
