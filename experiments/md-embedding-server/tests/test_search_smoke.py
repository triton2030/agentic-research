"""Integration smoke test: build index on a tiny corpus, search, verify
the matching file surfaces. Uses mocked embeddings (deterministic
hash-based vectors) so no network or API key required.

This catches regressions in the index → search → render pipeline that
unit tests on pure helpers miss."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from navigator.index import cmd_index
from navigator.api import search_read
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


def test_search_read_normal_returns_section_map(tiny_corpus, mock_embed, capsys):
    assert cmd_index(_index_args(tiny_corpus)) == 0
    capsys.readouterr()

    payload = search_read(str(tiny_corpus), "embeddings", limit=2)
    assert "sections" in payload
    assert payload["sections"], payload
    assert payload["expanded"] is False
    assert payload["content_included"] is False
    assert all("content" not in row for row in payload["sections"])
    assert all(row["read_next"] for row in payload["sections"])
    assert payload["candidate_token_total"] >= 1


def test_search_read_read_next_preserves_contract_args(monkeypatch):
    def fake_search(corpus, query, **kwargs):
        return {
            "root": corpus,
            "query": query,
            "scope": kwargs["scope"],
            "engine": "fake",
            "stats": {},
            "results": [
                {
                    "section_id": 1,
                    "file_id": 1,
                    "relative_path": "docs/a.md",
                    "start_line": 10,
                    "heading_chain": "A",
                    "heading_text": "A",
                    "token_count": 0,
                    "snippet": "needle",
                }
            ],
        }

    monkeypatch.setattr("navigator.api.search", fake_search)

    payload = search_read(
        "corpus",
        "needle",
        scope="descriptions",
        limit=7,
        candidates=11,
        max_heading_level=2,
        rerank=True,
        path_include=["docs/*"],
        path_exclude=["old/*"],
        token_budget=0,
    )

    top_args = payload["read_next"][0]["args"]
    assert top_args["scope"] == "descriptions"
    assert top_args["candidates"] == 11
    assert top_args["max_heading_level"] == 2
    assert top_args["rerank"] is True
    assert top_args["path_include"] == ["docs/*"]
    assert top_args["path_exclude"] == ["old/*"]
    assert top_args["token_budget"] == 0

    row_args = payload["sections"][0]["read_next"][0]["args"]
    assert row_args["scope"] == "descriptions"
    assert row_args["path_include"] == ["docs/a.md"]
    assert row_args["path_exclude"] == ["old/*"]
    assert row_args["token_budget"] == 0


def test_search_read_expanded_returns_section_bodies(tiny_corpus, mock_embed, capsys):
    assert cmd_index(_index_args(tiny_corpus)) == 0
    capsys.readouterr()

    payload = search_read(str(tiny_corpus), "embeddings", limit=2, expanded=True)
    assert payload["expanded"] is True
    assert payload["content_included"] is True
    assert any("Vector embeddings encode semantic meaning" in row["content"] for row in payload["sections"])
    assert payload["token_total"] >= 1
