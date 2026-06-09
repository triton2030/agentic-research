from __future__ import annotations

from pathlib import Path

import navigator
import pytest
from navigator import workflows


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


ATOMIC_NAMES = [
    "audit",
    "check",
    "cluster",
    "coherence_audit",
    "corpus_scan",
    "cycles",
    "deps",
    "extract",
    "health",
    "impact",
    "importance",
    "index",
    "init",
    "ls",
    "overlaps",
    "ping",
    "preflight",
    "profile_sections",
    "read_related",
    "repeated_concepts",
    "scan",
    "search",
    "search_read",
    "status",
    "strip",
    "toc",
]

WORKFLOW_NAMES = [
    "edit_context",
    "orient",
    "query_by_type",
    "refactor_candidates",
    "section_blast_radius",
]


def test_public_api_exports_26_atomic_and_5_workflows() -> None:
    assert len(ATOMIC_NAMES) == 26
    assert len(WORKFLOW_NAMES) == 5
    for name in ATOMIC_NAMES:
        assert callable(getattr(navigator, name))
    for name in WORKFLOW_NAMES:
        assert callable(getattr(workflows, name))


def test_public_api_smoke_on_fixture_corpus() -> None:
    map_data = navigator.ls(str(CORPUS))
    calls = [
        navigator.ping(),
        navigator.corpus_scan(str(CORPUS)),
        navigator.status(str(CORPUS)),
        map_data,
        navigator.toc(str(CORPUS)),
        navigator.extract(map_data, files="1"),
        navigator.read_related(paths=[str(README)], scan=str(CORPUS), mode="preview"),
        navigator.coherence_audit(str(README), scan=str(CORPUS), depth=1),
        navigator.importance(str(CORPUS)),
        navigator.preflight(str(README), scan=str(CORPUS)),
        navigator.impact(str(README), scan=str(CORPUS)),
        navigator.deps(str(README), scan=str(CORPUS)),
        navigator.scan(paths=[str(CORPUS)]),
        navigator.check(paths=[str(CORPUS)]),
        navigator.health(paths=[str(CORPUS)]),
        navigator.cycles(paths=[str(CORPUS)]),
        navigator.cluster(str(CORPUS)),
        navigator.search(str(CORPUS), "sample"),
        navigator.search_read(str(CORPUS), "sample"),
        navigator.walk(str(README), anchor="Rule", scan=str(CORPUS), depth=1),
        navigator.overlaps(str(CORPUS)),
        navigator.repeated_concepts(str(CORPUS)),
        navigator.audit(str(CORPUS)),
        navigator.init(paths=[str(CORPUS)], dry_run=True),
        navigator.strip(paths=[str(CORPUS)], dry_run=True),
        navigator.index(str(CORPUS), dry_run=True),
        navigator.profile_sections(str(CORPUS), dry_run=True, mode="llm"),
        workflows.orient(str(CORPUS), compact=True),
        workflows.edit_context(str(README), scan=str(CORPUS), mode="strict"),
        workflows.query_by_type(str(CORPUS), ["rule"]),
        workflows.refactor_candidates(str(CORPUS), compact=True),
        workflows.section_blast_radius(str(README), str(CORPUS), "sample", scan=str(CORPUS)),
    ]
    assert len(calls) == 32
    assert all(isinstance(payload, dict) for payload in calls)


def test_graph_public_api_builds_graph_args(monkeypatch, tmp_path: Path) -> None:
    from navigator import api_graph
    from navigator.graph_core import GraphArgs

    monkeypatch.chdir(tmp_path)
    seen_args: list[GraphArgs] = []

    def fake_load_docs(paths, root, args):
        seen_args.append(args)
        return []

    monkeypatch.setattr(api_graph, "load_docs", fake_load_docs)

    payload = navigator.scan(paths=["."], path_include="docs")

    assert payload["_exit_code"] == 0
    assert isinstance(seen_args[0], GraphArgs)
    assert seen_args[0].paths == ["."]
    assert seen_args[0].path_include == ["docs"]


def test_graph_init_rolls_back_partial_write(monkeypatch, tmp_path: Path) -> None:
    from navigator import graph_core

    monkeypatch.chdir(tmp_path)
    first = tmp_path / "a.md"
    second = tmp_path / "b.md"
    first.write_text("# A\n", encoding="utf-8")
    second.write_text("# B\n", encoding="utf-8")
    originals = {path: path.read_text(encoding="utf-8") for path in (first, second)}
    docs = [graph_core.load_doc(path, tmp_path) for path in (first, second)]
    original_replace = graph_core.os.replace
    calls = 0

    def flaky_replace(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("boom")
        return original_replace(*args, **kwargs)

    monkeypatch.setattr(graph_core.os, "replace", flaky_replace)

    with pytest.raises(RuntimeError):
        graph_core.write_doc_plan(
            [
                graph_core.DocWrite.from_frontmatter(
                    doc,
                    {"description": "TODO", "depends-on": []},
                    doc.body,
                )
                for doc in docs
            ]
        )

    assert {path: path.read_text(encoding="utf-8") for path in (first, second)} == originals


def test_public_api_does_not_import_legacy_graph_module() -> None:
    source = (ROOT / "src" / "navigator" / "api.py").read_text(encoding="utf-8")
    assert "from . import graph" not in source


def test_query_by_type_workflow_is_thin_domain_alias() -> None:
    """Profile query internals belong to the profile adapter, not workflows."""
    import importlib

    module = importlib.import_module("navigator.workflows.query_by_type")
    source = Path(module.__file__ or "").read_text(encoding="utf-8")
    assert callable(module.query_by_type)
    assert "from navigator.api import query_by_type" not in source
    assert "section_profile" not in source
    assert "profile_unprofiled_sections" not in source
    assert "api_profile" in source


def test_refactor_candidates_workflow_is_thin_domain_alias() -> None:
    """Refactor proposal internals belong to the profile adapter."""
    import importlib

    module = importlib.import_module("navigator.workflows.refactor_candidates")
    source = Path(module.__file__ or "").read_text(encoding="utf-8")
    assert callable(module.refactor_candidates)
    assert "from navigator.api import refactor_candidates" not in source
    assert "refactor_proposals" not in source
    assert "api_profile" in source


def test_warm_index_tools_filter_tool_specific_kwargs(tiny_corpus: Path, mock_embed) -> None:
    indexed = navigator.index(str(tiny_corpus), confirm=True)
    assert indexed["embedded"] >= 1

    search_payload = navigator.search(str(tiny_corpus), "definition", scope="descriptions", limit=2)
    assert "results" in search_payload

    overlaps_payload = navigator.overlaps(str(tiny_corpus), threshold=0.1, top=2, min_tokens=1)
    assert overlaps_payload.get("error") != "usage_error"

    repeated_payload = navigator.repeated_concepts(
        str(tiny_corpus),
        threshold=0.1,
        top=2,
        min_tokens=1,
        min_files=1,
        min_sections=1,
    )
    assert repeated_payload.get("error") != "usage_error"

    audit_payload = navigator.audit(str(tiny_corpus), threshold_smear=0.1, cluster_k=2)
    assert "health" in audit_payload

    cluster_payload = navigator.cluster(str(tiny_corpus), k=2)
    assert cluster_payload.get("error") != "usage_error"
    assert "clusters" in cluster_payload


def test_public_search_no_cache_routes_to_mutating_index(tiny_corpus: Path, mock_embed) -> None:
    payload = navigator.search(
        str(tiny_corpus),
        "definition",
        scope="descriptions",
        no_cache=True,
        max_auto_embed=10000,
    )

    assert payload["error"] == "cache_rebuild_requires_index"
    assert payload["read_next"][0]["tool"] == "md_index"
    assert payload["read_next"][0]["args"]["dry_run"] is True


def test_public_search_rejects_unknown_kwargs(tiny_corpus: Path) -> None:
    with pytest.raises(TypeError, match="unexpected keyword"):
        navigator.search(str(tiny_corpus), "definition", surprise=True)


def test_path_filter_values_reject_mappings(tiny_corpus: Path) -> None:
    with pytest.raises(TypeError, match="Expected a string or iterable of strings"):
        navigator.search(str(tiny_corpus), "definition", path_include={"bad": "shape"})


def test_profile_sections_dry_run_respects_path_include(tmp_path: Path) -> None:
    keep = tmp_path / "keep"
    skip = tmp_path / "skip"
    keep.mkdir()
    skip.mkdir()
    keep_doc = keep / "doc.md"
    skip_doc = skip / "doc.md"
    keep_doc.write_text("# Keep\n", encoding="utf-8")
    skip_doc.write_text("# Skip\n", encoding="utf-8")

    payload = navigator.profile_sections(
        str(tmp_path),
        dry_run=True,
        mode="llm",
        path_include="keep/**",
    )

    assert payload["sections_to_profile_estimate"] == 1
    assert payload["affected_files"] == [str(keep_doc.resolve())]
