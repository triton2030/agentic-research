from __future__ import annotations

from pathlib import Path

import navigator
from navigator import workflows


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


ATOMIC_NAMES = [
    "audit",
    "changed",
    "check",
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


def test_public_api_exports_24_atomic_and_5_workflows() -> None:
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
        navigator.importance(str(CORPUS)),
        navigator.preflight(str(README), scan=str(CORPUS)),
        navigator.impact(str(README), scan=str(CORPUS)),
        navigator.deps(str(README), scan=str(CORPUS)),
        navigator.scan(paths=[str(CORPUS)]),
        navigator.check(paths=[str(CORPUS)]),
        navigator.health(paths=[str(CORPUS)]),
        navigator.cycles(paths=[str(CORPUS)]),
        navigator.changed(scan=str(CORPUS), staged=True),
        navigator.search(str(CORPUS), "sample"),
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
    assert len(calls) == 29
    assert all(isinstance(payload, dict) for payload in calls)


def test_query_by_type_docstring_documents_re_export() -> None:
    """Brooks F1 anti-regression: workflows/query_by_type.py honestly documents
    that real composition lives in api.py. If a future maintainer inlines the
    logic here, this docstring sentinel must be removed deliberately."""
    import importlib

    module = importlib.import_module("navigator.workflows.query_by_type")
    doc = module.__doc__ or ""
    assert "real composition lives in navigator.api" in doc, (
        "workflows/query_by_type.py docstring must document its re-export nature"
    )


def test_refactor_candidates_docstring_documents_re_export() -> None:
    """Symmetric sentinel for refactor_candidates workflow."""
    import importlib

    module = importlib.import_module("navigator.workflows.refactor_candidates")
    doc = module.__doc__ or ""
    assert "real composition lives in navigator.api" in doc, (
        "workflows/refactor_candidates.py docstring must document its re-export nature"
    )


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
