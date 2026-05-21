"""Integration smoke test: build index on a tiny corpus, search, verify
the matching file surfaces. Uses mocked embeddings (deterministic
hash-based vectors) so no network or API key required.

This catches regressions in the index → search → render pipeline that
unit tests on pure helpers miss."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from navigator.index import cmd_index
from navigator.search import cmd_search


def _index_args(corpus: Path) -> Namespace:
    return Namespace(
        path=str(corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )


def _search_args(corpus: Path, query: str, scope: str = "sections") -> Namespace:
    return Namespace(
        path=str(corpus),
        query=query,
        scope=scope,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        json=False,
        limit=5,
        candidates=50,
        output=None,
        batch_size=32,
        batch_pause_ms=0,
    )


def test_index_builds_without_errors(tiny_corpus, mock_embed, capsys):
    rc = cmd_index(_index_args(tiny_corpus))
    captured = capsys.readouterr()
    assert rc == 0, f"cmd_index failed: out={captured.out!r} err={captured.err!r}"
    # Index file exists where expected
    assert (tiny_corpus / ".md-navigator" / "index.sqlite").exists()


def test_search_returns_zero_and_renders_results(tiny_corpus, mock_embed, capsys):
    assert cmd_index(_index_args(tiny_corpus)) == 0
    capsys.readouterr()  # clear

    rc = cmd_search(_search_args(tiny_corpus, "критериев приёмки"))
    out = capsys.readouterr().out
    assert rc == 0, f"cmd_search failed: out={out!r}"

    # New compact header with query
    assert "# search:" in out
    # signals: line is present on every result row
    assert "signals:" in out
    # The criteria file should surface (BM25 matches "критериев" via lemma → "критерий")
    assert "criteria.md" in out


def test_search_descriptions_scope_finds_file_by_frontmatter(
    tiny_corpus, mock_embed, capsys
):
    assert cmd_index(_index_args(tiny_corpus)) == 0
    capsys.readouterr()

    args = _search_args(tiny_corpus, "критерии приёмки задач", scope="descriptions")
    rc = cmd_search(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "criteria.md" in out


def test_search_signals_label_appears_for_bm25_match(tiny_corpus, mock_embed, capsys):
    """Verify that for a query whose tokens are present in the body text,
    `BM25+Dense` (or `BM25 only`) appears — not `Dense only`. The
    morphology-miss warning should only fire when BM25 truly missed."""
    assert cmd_index(_index_args(tiny_corpus)) == 0
    capsys.readouterr()

    # Use an English token that appears verbatim in knowledge.md
    rc = cmd_search(_search_args(tiny_corpus, "embeddings"))
    out = capsys.readouterr().out
    assert rc == 0
    # Some result row should have BM25 in its signals
    assert "BM25" in out
