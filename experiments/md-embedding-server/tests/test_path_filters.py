"""Path-filter tests: --path-include / --path-exclude narrow the result
set by relative_path with fnmatch-style globs. Substring fallback for
non-glob patterns. Filters apply before rerank so the cross-encoder
budget isn't spent on dropped candidates."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from navigator.api import index as api_index
from navigator.api import overlaps as api_overlaps
from navigator.api import search as api_search
from navigator.api import search_read, status as api_status
from navigator.filters import normalize_path_filter_patterns
from navigator.markdown_io import iter_markdown
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


def test_iter_markdown_allows_corpus_hosted_under_agent_worktrees(
    tmp_path: Path,
) -> None:
    roots = [
        tmp_path / ".codex" / "worktrees" / "abc" / "repo",
        tmp_path / ".claude" / "worktrees" / "abc" / "repo",
    ]
    for root in roots:
        root.mkdir(parents=True)
        readme = root / "README.md"
        readme.write_text("# Worktree\n", encoding="utf-8")

        assert iter_markdown(root) == [readme]


def test_iter_markdown_default_excludes_apply_inside_corpus_only(
    tmp_path: Path,
) -> None:
    root = tmp_path / ".codex" / "worktrees" / "abc" / "repo"
    for dirname in (".codex", ".claude"):
        nested = root / dirname
        nested.mkdir(parents=True)
        hidden = nested / "hidden.md"
        hidden.write_text("# Hidden\n", encoding="utf-8")
    visible = root / "visible.md"
    visible.write_text("# Visible\n", encoding="utf-8")

    assert iter_markdown(root) == [visible]


def test_iter_markdown_keeps_default_excluded_root_empty(
    tmp_path: Path,
) -> None:
    for dirname in (".codex", ".claude"):
        root = tmp_path / dirname
        root.mkdir()
        hidden = root / "hidden.md"
        hidden.write_text("# Hidden\n", encoding="utf-8")

        assert iter_markdown(root) == []


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


def _write_index_config(corpus: Path, body: str) -> None:
    (corpus / ".md-tools.toml").write_text(body, encoding="utf-8")


def _index_counts(corpus: Path) -> dict[str, int]:
    import sqlite_vec  # type: ignore[import-not-found]

    conn = sqlite3.connect(corpus / ".md-navigator" / "index.sqlite")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    try:
        return {
            "sections": int(conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]),
            "chunks": int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]),
            "sections_vec": int(conn.execute("SELECT COUNT(*) FROM sections_vec").fetchone()[0]),
            "sections_fts": int(conn.execute("SELECT COUNT(*) FROM sections_fts").fetchone()[0]),
            "skip_sections": int(
                conn.execute(
                    "SELECT COUNT(*) FROM sections WHERE relative_path GLOB 'skip/*'"
                ).fetchone()[0]
            ),
        }
    finally:
        conn.close()


def _delete_one_vector_row(corpus: Path) -> None:
    import sqlite_vec  # type: ignore[import-not-found]

    conn = sqlite3.connect(corpus / ".md-navigator" / "index.sqlite")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    try:
        rowid = conn.execute("SELECT MIN(chunk_id) FROM chunks").fetchone()[0]
        conn.execute("DELETE FROM sections_vec WHERE rowid = ?", (rowid,))
        conn.commit()
    finally:
        conn.close()


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


def test_config_exclude_cleanup_prunes_persistent_rows(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)
    assert before["skip_sections"] > 0

    _write_index_config(corpus, '[index]\nexclude = ["skip/*"]\n')

    dry = api_index(
        str(corpus),
        dry_run=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["pending_chunks"] == 0
    assert dry["removed_sections"] == 0
    assert dry["cleanup_sections"] == before["skip_sections"]
    assert dry["cleanup_reasons"] == {"config_excluded": before["skip_sections"]}
    assert [item["relative_path"] for item in dry["cleanup_files"]] == ["skip/many.md"]

    confirmed = api_index(
        str(corpus),
        confirm=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    assert confirmed["cleanup_sections"] == before["skip_sections"]
    after = _index_counts(corpus)
    assert after["skip_sections"] == 0
    assert after["sections"] == before["sections"] - confirmed["cleanup_sections"]
    assert after["chunks"] == before["chunks"] - confirmed["cleanup_chunks"]
    assert after["sections_vec"] == after["chunks"]
    assert after["sections_fts"] == after["sections"]


def test_cli_path_exclude_does_not_prune_unrelated_rows(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)

    dry = api_index(
        str(corpus),
        dry_run=True,
        path_exclude=["skip/*"],
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["cleanup_enabled"] is False
    assert dry["cleanup_disabled_reason"] == "operation_scope"
    assert dry["cleanup_sections"] == 0

    confirmed = api_index(
        str(corpus),
        confirm=True,
        path_exclude=["skip/*"],
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    assert confirmed["cleanup_sections"] == 0
    after = _index_counts(corpus)
    assert after["skip_sections"] == before["skip_sections"]


def test_config_exclude_cleanup_prunes_missing_rows_in_excluded_scope(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)
    (corpus / "skip" / "many.md").unlink()

    _write_index_config(corpus, '[index]\nexclude = ["skip/*"]\n')

    dry = api_index(
        str(corpus),
        dry_run=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["removed_sections"] == 0
    assert dry["cleanup_sections"] == before["skip_sections"]
    assert dry["cleanup_reasons"] == {"config_excluded": before["skip_sections"]}


def test_config_include_cleanup_prunes_rows_outside_canonical_scope(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)

    _write_index_config(corpus, '[index]\ninclude = ["keep/*"]\n')

    dry = api_index(
        str(corpus),
        dry_run=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["cleanup_sections"] == before["skip_sections"]
    assert dry["cleanup_reasons"] == {"config_not_included": before["skip_sections"]}


def test_partial_path_include_does_not_cleanup_missing_sibling_rows(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    (corpus / "skip" / "many.md").unlink()
    before = _index_counts(corpus)
    assert before["skip_sections"] > 0

    dry = api_index(
        str(corpus),
        dry_run=True,
        path_include=["keep/*"],
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["cleanup_enabled"] is False
    assert dry["cleanup_sections"] == 0

    confirmed = api_index(
        str(corpus),
        confirm=True,
        path_include=["keep/*"],
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    assert confirmed["cleanup_sections"] == 0
    after = _index_counts(corpus)
    assert after["skip_sections"] == before["skip_sections"]


def test_nested_parent_suggestion_scope_does_not_cleanup_siblings(
    tmp_path: Path,
    mock_embed,
) -> None:
    parent = tmp_path / "parent"
    child = parent / "child"
    sibling = parent / "sibling"
    child.mkdir(parents=True)
    sibling.mkdir()
    (child / "doc.md").write_text("# Child\n\n## Topic\n\nBody.\n", encoding="utf-8")
    (sibling / "doc.md").write_text("# Sibling\n\n## Topic\n\nBody.\n", encoding="utf-8")

    api_index(
        str(parent),
        confirm=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    (sibling / "doc.md").unlink()
    before = _index_counts(parent)

    scoped = api_index(
        str(parent),
        dry_run=True,
        path_include=["child/**"],
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert scoped["cleanup_enabled"] is False
    assert scoped["cleanup_sections"] == 0

    confirmed = api_index(
        str(parent),
        confirm=True,
        path_include=["child/**"],
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    assert confirmed["cleanup_sections"] == 0
    after = _index_counts(parent)
    assert after["sections"] == before["sections"]


def test_status_expanded_reports_cleanup_separately_from_removed_files(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)
    _write_index_config(corpus, '[index]\nexclude = ["skip/*"]\n')

    payload = _status(corpus, expanded=True)
    assert payload["cleanup_sections"] == before["skip_sections"]
    assert payload["removed_sections"] == 0
    assert payload["pending_chunks"] == 0
    assert [item["relative_path"] for item in payload["cleanup_files"]] == ["skip/many.md"]
    assert payload["removed_files"] == []


def test_status_expanded_reports_healthy_index_integrity(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)

    payload = _status(corpus, expanded=True)

    assert payload["index_integrity"]["ok"] is True
    assert payload["index_integrity"]["issues"] == []
    assert payload["index_integrity"]["counts"]["sections"] == _index_counts(corpus)["sections"]


def test_status_default_omits_healthy_index_integrity(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)

    payload = _status(corpus)

    assert "index_integrity" not in payload


def test_status_reports_vector_integrity_issue_in_default_output(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    _delete_one_vector_row(corpus)

    payload = _status(corpus)

    assert payload["state"] == "NEEDS_REBUILD"
    assert payload["index_integrity"]["ok"] is False
    assert "sections_vec_count_mismatch" in payload["index_integrity"]["issues"]
    assert any(
        issue.startswith("chunks_without_vector:")
        for issue in payload["index_integrity"]["issues"]
    )
    assert payload["recommended_action"]["tool"] == "md_index"
    assert "integrity mismatch" in payload["recommended_action"]["reason"]


def test_missing_file_uses_ordinary_removed_sections_not_lifecycle_cleanup(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)
    (corpus / "skip" / "many.md").unlink()

    payload = _status(corpus, expanded=True)
    assert payload["removed_sections"] == before["skip_sections"]
    assert payload["cleanup_sections"] == 0
    assert payload["cleanup_reasons"] == {}
    assert [item["relative_path"] for item in payload["removed_files"]] == ["skip/many.md"]

    dry = api_index(
        str(corpus),
        dry_run=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
    )
    assert dry["removed_sections"] == before["skip_sections"]
    assert dry["cleanup_sections"] == 0

    confirmed = api_index(
        str(corpus),
        confirm=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    assert confirmed["removed_sections"] == before["skip_sections"]
    assert confirmed["cleanup_sections"] == 0
    after = _index_counts(corpus)
    assert after["skip_sections"] == 0
    assert after["sections"] == before["sections"] - confirmed["removed_sections"]


def test_status_reports_cleanup_when_config_excludes_all_live_files(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    before = _index_counts(corpus)
    _write_index_config(corpus, '[index]\nexclude = ["*.md"]\n')

    payload = _status(corpus, expanded=True)
    assert payload.get("_exit_code", 0) == 0
    assert payload["state"] == "HEALTHY"
    assert payload["removed_sections"] == 0
    assert payload["cleanup_sections"] == before["sections"]
    assert payload["cleanup_reasons"] == {"config_excluded": before["sections"]}
    assert payload["pending_chunks"] == 0


def test_index_vacuum_returns_before_after_metadata(
    tmp_path: Path,
    mock_embed,
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    _write_index_config(corpus, '[index]\nexclude = ["skip/*"]\n')

    payload = api_index(
        str(corpus),
        confirm=True,
        vacuum=True,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )

    assert payload["vacuum"]["requested"] is True
    assert payload["vacuum"]["ran"] is True
    assert payload["vacuum"]["before"]["freelist_count"] >= payload["vacuum"]["after"]["freelist_count"]
    assert payload["vacuum"]["reclaimed_bytes"] >= 0
