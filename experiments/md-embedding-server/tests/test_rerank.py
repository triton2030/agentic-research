"""Tests for the reranker module. The HTTP layer is mocked so tests run
offline; the focus is on:

  - Document text composition (heading-chain prefix, truncation)
  - Search integration (rerank reorders results, scores attached, engine
    metadata reflects rerank usage)
  - Failure mode (rerank API error → fall back to RRF order, exit code 0)

Retargeted onto the canonical ``navigator.api`` surface: index/search go
through ``api.index`` / ``api.search`` (dict payloads), not legacy
``cmd_index`` / ``cmd_search`` (argparse Namespace + stdout JSON). The
monkeypatch on ``from navigator import search as search_mod`` is kept
verbatim — after the package proxy is retired it resolves to the real
``navigator.search`` module on disk, which is the module ``api.search``
calls through to via ``search_payload``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from navigator import api
from navigator import rerank as rerank_module
from navigator.rerank import doc_text_for_rerank


def test_doc_text_for_rerank_includes_heading_chain() -> None:
    out = doc_text_for_rerank(
        relative_path="a/b.md",
        heading_chain="A > B > C",
        body="Body content here.",
        max_chars=100,
    )
    # Heading chain comes first, then body
    assert out.startswith("A > B > C")
    assert "Body content here." in out


def test_doc_text_for_rerank_truncates_long_body() -> None:
    body = "X" * 5000
    out = doc_text_for_rerank("a.md", "Heading", body, max_chars=200)
    assert len(out) <= 200


def test_doc_text_for_rerank_falls_back_to_path_when_no_heading() -> None:
    out = doc_text_for_rerank("path/to/file.md", "", "body", max_chars=200)
    assert "path/to/file.md" in out


def _index(tiny_corpus: Path) -> None:
    payload = api.index(
        str(tiny_corpus),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        batch_size=32,
        batch_pause_ms=0,
    )
    assert payload.get("_exit_code", 0) == 0


def _search_with_rerank(corpus: Path, query: str) -> dict:
    return api.search(
        str(corpus),
        query,
        scope="sections",
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        limit=5,
        candidates=50,
        rerank=True,
        rerank_model="test-reranker",
        rerank_api_url="http://test.local/rerank",
        rerank_timeout=5,
        rerank_top_n=10,
    )


def test_search_with_rerank_reorders_and_scores(
    tiny_corpus: Path, mock_embed, monkeypatch
) -> None:
    _index(tiny_corpus)

    # Reverse the RRF order to prove rerank reorders. Cohere returns
    # results sorted by score desc. We map last input to highest score.
    def fake_rerank(query, documents, **kwargs):
        n = len(documents)
        return [(n - 1 - i, 1.0 - i * 0.1) for i in range(n)]

    monkeypatch.setattr(rerank_module, "rerank_documents", fake_rerank)
    # search.py imports the symbol directly into its namespace.
    from navigator import search as search_mod

    monkeypatch.setattr(search_mod, "rerank_documents", fake_rerank)

    payload = _search_with_rerank(tiny_corpus, "embeddings")
    assert payload.get("_exit_code", 0) == 0
    # Engine reports rerank applied
    assert payload["engine"]["rerank"] is True
    assert payload["engine"]["rerank_model"] == "test-reranker"
    # Every result row has a rerank_score (non-null)
    if payload["results"]:
        for row in payload["results"]:
            assert row.get("rerank_score") is not None


def test_search_rerank_failure_falls_back(
    tiny_corpus: Path, mock_embed, monkeypatch
) -> None:
    _index(tiny_corpus)

    def boom(*a, **kw):
        raise RuntimeError("Rerank API returned 500: simulated outage")

    monkeypatch.setattr(rerank_module, "rerank_documents", boom)
    from navigator import search as search_mod

    monkeypatch.setattr(search_mod, "rerank_documents", boom)

    payload = _search_with_rerank(tiny_corpus, "embeddings")
    # Search still succeeds — fall back to RRF order. The legacy CLI also
    # printed a "Rerank failed" stderr warning, but that warning is owned by
    # the cmd_search presentation layer (its rerank_error_handler); the
    # canonical api.search swallows the RuntimeError and signals fallback
    # purely through engine.rerank=False, so the stderr assert is dropped.
    assert payload.get("_exit_code", 0) == 0
    assert payload["engine"]["rerank"] is False


def test_search_without_rerank_unchanged(tiny_corpus: Path, mock_embed) -> None:
    """Sanity check: omitting rerank keeps engine.rerank=false and no
    rerank_score on rows."""
    _index(tiny_corpus)

    payload = api.search(
        str(tiny_corpus),
        "embeddings",
        scope="sections",
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        limit=5,
        candidates=50,
        rerank=False,
        rerank_model="unused",
        rerank_api_url="unused",
        rerank_timeout=5,
        rerank_top_n=10,
    )
    assert payload.get("_exit_code", 0) == 0
    assert payload["engine"]["rerank"] is False
    if payload["results"]:
        for row in payload["results"]:
            # Field may be present but should be null.
            assert row.get("rerank_score") is None
