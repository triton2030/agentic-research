"""Integration smoke test: build index on a tiny corpus, search, verify
the matching file surfaces. Uses mocked embeddings (deterministic
hash-based vectors) so no network or API key required.

This catches regressions in the index → search → render pipeline that
unit tests on pure helpers miss."""

from __future__ import annotations

from pathlib import Path

from navigator.api import index as api_index
from navigator.api import search as api_search
from navigator.api import search_read

# Embedding/model knobs the old argparse Namespace carried. The mock_embed
# fixture stubs the HTTP call, so the URL/timeout are inert but still passed
# to mirror the real call path.
_EMBED_KWARGS = dict(
    embed_model="test/stub-1",
    embedding_api_url="http://test.local/v1",
    embedding_timeout=5,
    cache_dir=None,
    max_heading_level=6,
)


def _build_index(corpus: Path) -> dict:
    """Warm the persistent index for `corpus` across both scopes. `confirm=True`
    reaches the build branch in `api.index` (the unconfirmed default is a
    dry-run preview); this mirrors the unconditional warmup the legacy
    `cmd_index` performed."""
    return api_index(
        str(corpus),
        confirm=True,
        batch_size=32,
        batch_pause_ms=0,
        **_EMBED_KWARGS,
    )


def _search(corpus: Path, query: str, scope: str = "sections") -> dict:
    return api_search(
        str(corpus),
        query,
        scope=scope,
        limit=5,
        candidates=50,
        no_cache=False,
        **_EMBED_KWARGS,
    )


def _paths(payload: dict) -> list[str]:
    return [row.get("relative_path") or "" for row in payload.get("results", [])]


def test_index_builds_without_errors(tiny_corpus, mock_embed):
    payload = _build_index(tiny_corpus)
    assert payload.get("_exit_code", 0) == 0, f"index failed: {payload!r}"
    # Index file exists where expected
    assert (tiny_corpus / ".md-navigator" / "index.sqlite").exists()


def test_search_returns_zero_and_renders_results(tiny_corpus, mock_embed):
    assert _build_index(tiny_corpus).get("_exit_code", 0) == 0

    payload = _search(tiny_corpus, "критериев приёмки")
    assert payload.get("_exit_code", 0) == 0, f"search failed: {payload!r}"

    # The payload is the structured form of the old compact header: it carries
    # the query and scope the header rendered.
    assert payload["query"] == "критериев приёмки"
    assert payload["scope"] == "sections"
    # signals: every result row carries the channel-diagnosis data the old
    # `signals:` line was built from (fields_hit + fusion scores).
    assert payload["results"], payload
    assert all("fields_hit" in row and "rrf_score" in row for row in payload["results"])
    # The criteria file should surface (BM25 matches "критериев" via lemma → "критерий")
    assert any("criteria.md" in path for path in _paths(payload)), _paths(payload)


def test_search_descriptions_scope_finds_file_by_frontmatter(tiny_corpus, mock_embed):
    assert _build_index(tiny_corpus).get("_exit_code", 0) == 0

    payload = _search(tiny_corpus, "критерии приёмки задач", scope="descriptions")
    assert payload.get("_exit_code", 0) == 0
    assert any("criteria.md" in path for path in _paths(payload)), _paths(payload)


def test_search_signals_label_appears_for_bm25_match(tiny_corpus, mock_embed):
    """Verify that for a query whose tokens are present in the body text,
    BM25 contributed to at least one result — i.e. some row has a non-empty
    `fields_hit` (which is exactly what made the old `signals:` line read
    `BM25+Dense` / `BM25 only` rather than `Dense only`). The morphology-miss
    warning should only fire when BM25 truly missed."""
    assert _build_index(tiny_corpus).get("_exit_code", 0) == 0

    # Use an English token that appears verbatim in knowledge.md
    payload = _search(tiny_corpus, "embeddings")
    assert payload.get("_exit_code", 0) == 0
    # Some result row should have a BM25 field hit in its signals
    assert any(row.get("fields_hit") for row in payload["results"]), payload["results"]


def test_search_read_normal_returns_section_map(tiny_corpus, mock_embed):
    assert _build_index(tiny_corpus).get("_exit_code", 0) == 0

    payload = search_read(str(tiny_corpus), "embeddings", limit=2)
    assert "sections" in payload
    assert payload["sections"], payload
    assert payload["expanded"] is False
    assert payload["view"] == "map"
    assert all("content" not in row for row in payload["sections"])
    assert all("read_next" not in row for row in payload["sections"])
    assert payload["read_next"]
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

    monkeypatch.setattr("navigator.api_search._search_rich", fake_search)

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


def test_search_read_expanded_returns_section_bodies(tiny_corpus, mock_embed):
    assert _build_index(tiny_corpus).get("_exit_code", 0) == 0

    payload = search_read(str(tiny_corpus), "embeddings", limit=2, expanded=True)
    assert payload["expanded"] is True
    assert payload["view"] == "expanded"
    assert any("Vector embeddings encode semantic meaning" in row["content"] for row in payload["sections"])
    assert payload["token_total"] >= 1
