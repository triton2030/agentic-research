"""Path-filter tests: --path-include / --path-exclude narrow the result
set by relative_path with fnmatch-style globs. Substring fallback for
non-glob patterns. Filters apply before rerank so the cross-encoder
budget isn't spent on dropped candidates."""

from __future__ import annotations

from pathlib import Path

from navigator.api import index as api_index
from navigator.api import overlaps as api_overlaps
from navigator.api import search as api_search
from navigator.api import search_read, status as api_status
from navigator.filters import normalize_path_filter_patterns
from navigator.search import (
    _apply_path_filters,
    _path_matches_any,
)


def test_path_matches_any_glob_star() -> None:
    assert _path_matches_any("_ops/criteria/foo.md", ["_ops/criteria/*"]) is True
    assert _path_matches_any("knowledge/wisdom.md", ["_ops/criteria/*"]) is False


def test_path_matches_any_double_star_treated_as_star() -> None:
    # fnmatch: `**` collapses to `*` which matches anything including slashes
    assert _path_matches_any("_ops/criteria/sub/a.md", ["_ops/**"]) is True


def test_path_matches_any_substring_fallback() -> None:
    # No glob metachars → substring containment
    assert _path_matches_any("knowledge/wisdom-agents.md", ["wisdom"]) is True
    assert _path_matches_any("_ops/findings/note.md", ["criteria"]) is False


def test_path_matches_any_empty_patterns_returns_false() -> None:
    assert _path_matches_any("anything", []) is False


def test_apply_path_filters_include_narrows() -> None:
    results = [
        {"relative_path": "_ops/criteria/a.md"},
        {"relative_path": "knowledge/b.md"},
        {"relative_path": "_ops/criteria/c.md"},
    ]
    out = _apply_path_filters(results, include_patterns=["_ops/criteria/*"], exclude_patterns=[])
    assert len(out) == 2
    assert all("_ops/criteria/" in r["relative_path"] for r in out)


def test_apply_path_filters_exclude_drops() -> None:
    results = [
        {"relative_path": "_ops/criteria/a.md"},
        {"relative_path": "experiments/runs/log.md"},
        {"relative_path": "knowledge/b.md"},
    ]
    out = _apply_path_filters(results, include_patterns=[], exclude_patterns=["experiments/*"])
    assert len(out) == 2
    assert all("experiments" not in r["relative_path"] for r in out)


def test_apply_path_filters_include_then_exclude() -> None:
    """Include first, then exclude from matched set."""
    results = [
        {"relative_path": "_ops/criteria/a.md"},
        {"relative_path": "_ops/criteria/_archive/old.md"},
        {"relative_path": "_ops/plans/task.md"},
    ]
    out = _apply_path_filters(
        results,
        include_patterns=["_ops/criteria/*"],
        exclude_patterns=["*_archive*"],
    )
    assert len(out) == 1
    assert out[0]["relative_path"] == "_ops/criteria/a.md"


def test_apply_path_filters_no_filters_returns_input() -> None:
    results = [{"relative_path": "a.md"}, {"relative_path": "b.md"}]
    out = _apply_path_filters(results, include_patterns=[], exclude_patterns=[])
    assert out == results


def test_normalize_path_filter_patterns_accepts_single_string(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    assert normalize_path_filter_patterns("docs/*.md", root) == ["docs/*.md"]


def test_normalize_path_filter_patterns_accepts_generator(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    patterns = (item for item in ["docs/*.md", "notes"])
    assert normalize_path_filter_patterns(patterns, root) == ["docs/*.md", "notes"]


def test_normalize_path_filter_patterns_accepts_absolute_path_under_corpus(
    tmp_path: Path,
) -> None:
    root = tmp_path / "corpus"
    absolute = str(root / "docs" / "guide.md")
    assert normalize_path_filter_patterns([absolute], root) == ["docs/guide.md"]


def _index(tiny_corpus: Path) -> dict:
    return api_index(
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


def _partial_corpus(tmp_path: Path) -> Path:
    root = tmp_path / "partial-corpus"
    (root / "keep").mkdir(parents=True)
    (root / "skip").mkdir(parents=True)
    (root / "keep" / "a.md").write_text(
        "# Keep\n\n"
        "## Alpha\n\n"
        "Partial scoped retrieval should keep working here.\n\n"
        "## Beta\n\n"
        "Another useful scoped section for partial indexing.\n",
        encoding="utf-8",
    )
    (root / "skip" / "many.md").write_text(
        "# Skip\n\n"
        + "\n\n".join(
            f"## Skip {i}\n\nThis intentionally unindexed section should not block scoped tools."
            for i in range(8)
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def _search_kwargs(query: str, **overrides) -> dict:
    base = dict(
        query=query,
        scope="sections",
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        limit=10,
        candidates=50,
        rerank=False,
        rerank_model="unused",
        rerank_api_url="unused",
        rerank_timeout=5,
        rerank_top_n=10,
        path_include=[],
        path_exclude=[],
    )
    base.update(overrides)
    return base


def _search(corpus: Path, query: str, **overrides) -> dict:
    kwargs = _search_kwargs(query, **overrides)
    return api_search(str(corpus), kwargs.pop("query"), **kwargs)


def _status_kwargs(**overrides) -> dict:
    base = dict(
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=50,
        path_include=[],
        path_exclude=[],
    )
    base.update(overrides)
    return base


def _status(corpus: Path, **overrides) -> dict:
    return api_status(str(corpus), **_status_kwargs(**overrides))


def _overlaps_kwargs(**overrides) -> dict:
    base = dict(
        threshold=-1.0,
        top=20,
        min_tokens=0,
        include_same_file=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=1,
        no_cache=False,
        path_include=[],
        path_exclude=[],
    )
    base.update(overrides)
    return base


def _overlaps(corpus: Path, **overrides) -> dict:
    # expanded=True returns the raw overlap output (pairs + stats), matching
    # the legacy `cmd_overlaps --json` payload the asserts below rely on.
    return api_overlaps(str(corpus), expanded=True, **_overlaps_kwargs(**overrides))


def test_search_path_include_narrows_to_subtree(
    tiny_corpus: Path, mock_embed
) -> None:
    _index(tiny_corpus)

    # Tiny corpus has agents.md, criteria.md, knowledge.md, noise.md at root.
    # Include only criteria.md.
    payload = _search(tiny_corpus, "приёмки", path_include=["criteria.md"])
    assert payload.get("_exit_code", 0) == 0
    assert payload["engine"]["path_include"] == ["criteria.md"]
    for row in payload["results"]:
        assert "criteria.md" in row["relative_path"]


def test_search_path_exclude_drops_subtree(
    tiny_corpus: Path, mock_embed
) -> None:
    _index(tiny_corpus)

    # Exclude noise.md — everything else should remain.
    payload = _search(tiny_corpus, "embeddings", path_exclude=["noise.md"])
    assert payload.get("_exit_code", 0) == 0
    assert payload["engine"]["path_exclude"] == ["noise.md"]
    for row in payload["results"]:
        assert "noise.md" not in row["relative_path"]


def test_search_filters_in_engine_metadata(
    tiny_corpus: Path, mock_embed
) -> None:
    _index(tiny_corpus)
    payload = _search(tiny_corpus, "embeddings")
    assert payload.get("_exit_code", 0) == 0
    # Even with no filters, the keys must be present (= empty arrays)
    assert payload["engine"]["path_include"] == []
    assert payload["engine"]["path_exclude"] == []


def test_partial_index_scoped_search_ignores_unindexed_skipped_paths(
    tmp_path: Path, mock_embed
) -> None:
    corpus = _partial_corpus(tmp_path)
    include = [str(corpus / "keep" / "*.md")]

    indexed = api_index(
        str(corpus),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        batch_size=32,
        batch_pause_ms=0,
        path_include=include,
        path_exclude=[],
    )
    assert indexed.get("_exit_code", 0) == 0

    scoped = _search(
        corpus,
        "partial scoped retrieval",
        max_auto_embed=1,
        path_include=include,
    )
    assert scoped.get("_exit_code", 0) == 0
    assert scoped["results"]
    assert all(row["relative_path"].startswith("keep/") for row in scoped["results"])

    unscoped = _search(corpus, "partial scoped retrieval", max_auto_embed=1)
    assert unscoped.get("_exit_code", 0) == 0
    assert unscoped["partial_index"]["active"] is True
    assert unscoped["partial_index"]["pending_files"] == [
        {
            "relative_path": "skip/many.md",
            "added_sections": 9,
            "pending_chunks": 9,
        }
    ]
    assert unscoped["results"]
    assert all(row["relative_path"].startswith("keep/") for row in unscoped["results"])

    read_payload = search_read(
        str(corpus),
        "partial scoped retrieval",
        max_auto_embed=1,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
    )
    assert read_payload["partial_index"]["active"] is True
    assert read_payload["sections"]


def test_partial_index_scoped_status_is_fresh_when_unscoped_needs_warmup(
    tmp_path: Path, mock_embed
) -> None:
    corpus = _partial_corpus(tmp_path)
    include = ["keep/*"]
    indexed = api_index(
        str(corpus),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        batch_size=32,
        batch_pause_ms=0,
        path_include=include,
        path_exclude=[],
    )
    assert indexed.get("_exit_code", 0) == 0

    scoped_status = _status(corpus, max_auto_embed=1, path_include=include)
    assert scoped_status.get("_exit_code", 0) == 0
    assert scoped_status["state"] == "FRESH"

    unscoped_status = _status(corpus, max_auto_embed=1, expanded=True)
    assert unscoped_status.get("_exit_code", 0) == 0
    assert unscoped_status["state"] == "NEEDS_WARMUP"

    assert unscoped_status["pending_files"] == [
        {
            "relative_path": "skip/many.md",
            "added_sections": 9,
            "pending_chunks": 9,
        }
    ]


def test_status_no_index_reports_pending_chunks_for_dry_run_estimate(
    tmp_path: Path,
) -> None:
    corpus = _partial_corpus(tmp_path)
    payload = _status(corpus, path_include=["keep/*"])
    assert payload.get("_exit_code", 0) == 0
    assert payload["state"] == "NO_INDEX"
    assert payload["pending_chunks"] > 0


def test_status_public_api_and_legacy_json_share_core(
    tmp_path: Path, mock_embed
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)

    api_payload = api_status(
        str(corpus),
        path_include=["keep/*"],
        max_auto_embed=1,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
    )

    # Both call sites now route through navigator.api.status with the same
    # inputs, so the payloads are identical by construction.
    other_payload = _status(
        corpus,
        path_include=["keep/*"],
        max_auto_embed=1,
    )

    assert other_payload == api_payload


def test_partial_index_scoped_overlaps_compares_only_included_chunks(
    tmp_path: Path, mock_embed
) -> None:
    corpus = _partial_corpus(tmp_path)
    include = ["keep/*"]
    indexed = api_index(
        str(corpus),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        batch_size=32,
        batch_pause_ms=0,
        path_include=include,
        path_exclude=[],
    )
    assert indexed.get("_exit_code", 0) == 0

    payload = _overlaps(corpus, path_include=include)
    assert payload.get("_exit_code", 0) == 0
    assert payload["stats"]["chunks_compared"] == 3
    assert all(
        pair["a"]["relative_path"].startswith("keep/")
        and pair["b"]["relative_path"].startswith("keep/")
        for pair in payload["pairs"]
    )


def test_index_allow_nested_corpus_escape_hatch(tmp_path: Path, mock_embed) -> None:
    corpus = _partial_corpus(tmp_path)
    child = corpus / "keep"
    api_index(
        str(corpus),
        confirm=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )

    refused = api_index(
        str(child),
        dry_run=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert refused["error"] == "nested_corpus_refused"
    assert not (child / ".md-navigator").exists()

    allowed = api_index(
        str(child),
        dry_run=True,
        allow_nested_corpus=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert allowed["pending_chunks"] >= 1

    confirmed = api_index(
        str(child),
        confirm=True,
        allow_nested_corpus=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert confirmed["embedded"] >= 1
    assert (child / ".md-navigator" / "index.sqlite").exists()


def test_legacy_cmd_index_refuses_nested_corpus(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    child = parent / "child"
    child.mkdir(parents=True)
    (child / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")
    (parent / ".md-navigator").mkdir()
    (parent / ".md-navigator" / "index.sqlite").write_bytes(b"")

    refused = api_index(
        str(child),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        batch_size=32,
        batch_pause_ms=0,
        path_include=[],
        path_exclude=[],
    )
    assert refused.get("_exit_code", 0) == 1
    assert refused["error"] == "nested_corpus_refused"
    assert not (child / ".md-navigator").exists()


def test_index_dry_run_reports_zero_delta_for_fresh_index(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    api_index(
        str(corpus),
        confirm=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )

    dry = api_index(
        str(corpus),
        dry_run=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["pending_chunks"] == 0
    assert dry["added_sections"] == 0
