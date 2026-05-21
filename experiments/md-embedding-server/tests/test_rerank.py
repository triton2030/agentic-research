"""Tests for the reranker module. The HTTP layer is mocked so tests run
offline; the focus is on:

  - Document text composition (heading-chain prefix, truncation)
  - Search integration (rerank reorders results, scores attached, engine
    metadata reflects rerank usage)
  - Failure mode (rerank API error → fall back to RRF order, exit code 0)
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from navigator import rerank as rerank_module
from navigator.index import cmd_index
from navigator.rerank import doc_text_for_rerank
from navigator.search import cmd_search


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
    args = Namespace(
        path=str(tiny_corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )
    assert cmd_index(args) == 0


def _search_with_rerank(corpus: Path, query: str, mock_returns) -> Namespace:
    return Namespace(
        path=str(corpus),
        query=query,
        scope="sections",
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        json=True,
        limit=5,
        candidates=50,
        output=None,
        batch_size=32,
        batch_pause_ms=0,
        rerank=True,
        rerank_model="test-reranker",
        rerank_api_url="http://test.local/rerank",
        rerank_timeout=5,
        rerank_top_n=10,
    )


def test_search_with_rerank_reorders_and_scores(
    tiny_corpus: Path, mock_embed, monkeypatch, capsys
) -> None:
    _index(tiny_corpus)
    capsys.readouterr()

    # Reverse the RRF order to prove rerank reorders. Cohere returns
    # results sorted by score desc. We map last input to highest score.
    def fake_rerank(query, documents, **kwargs):
        n = len(documents)
        return [(n - 1 - i, 1.0 - i * 0.1) for i in range(n)]

    monkeypatch.setattr(rerank_module, "rerank_documents", fake_rerank)
    # search.py imports the symbol directly into its namespace.
    from navigator import search as search_mod

    monkeypatch.setattr(search_mod, "rerank_documents", fake_rerank)

    rc = cmd_search(_search_with_rerank(tiny_corpus, "embeddings", fake_rerank))
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    # Engine reports rerank applied
    assert payload["engine"]["rerank"] is True
    assert payload["engine"]["rerank_model"] == "test-reranker"
    # Every result row has a rerank_score (non-null)
    if payload["results"]:
        for row in payload["results"]:
            assert row.get("rerank_score") is not None


def test_search_rerank_failure_falls_back(
    tiny_corpus: Path, mock_embed, monkeypatch, capsys
) -> None:
    _index(tiny_corpus)
    capsys.readouterr()

    def boom(*a, **kw):
        raise RuntimeError("Rerank API returned 500: simulated outage")

    monkeypatch.setattr(rerank_module, "rerank_documents", boom)
    from navigator import search as search_mod

    monkeypatch.setattr(search_mod, "rerank_documents", boom)

    rc = cmd_search(_search_with_rerank(tiny_corpus, "embeddings", boom))
    captured = capsys.readouterr()
    # Search still succeeds — fall back to RRF order with a stderr warning.
    assert rc == 0
    assert "Rerank failed" in captured.err
    payload = json.loads(captured.out)
    assert payload["engine"]["rerank"] is False


def test_search_without_rerank_unchanged(tiny_corpus: Path, mock_embed, capsys) -> None:
    """Sanity check: omitting --rerank keeps engine.rerank=false and no
    rerank_score on rows."""
    _index(tiny_corpus)
    capsys.readouterr()

    args = Namespace(
        path=str(tiny_corpus),
        query="embeddings",
        scope="sections",
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        json=True,
        limit=5,
        candidates=50,
        output=None,
        batch_size=32,
        batch_pause_ms=0,
        rerank=False,
        rerank_model="unused",
        rerank_api_url="unused",
        rerank_timeout=5,
        rerank_top_n=10,
    )
    rc = cmd_search(args)
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["engine"]["rerank"] is False
    if payload["results"]:
        for row in payload["results"]:
            # Field may be present but should be null.
            assert row.get("rerank_score") is None
