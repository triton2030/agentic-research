"""Path-filter tests: --path-include / --path-exclude narrow the result
set by relative_path with fnmatch-style globs. Substring fallback for
non-glob patterns. Filters apply before rerank so the cross-encoder
budget isn't spent on dropped candidates."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from navigator.index import cmd_index
from navigator.index_status import cmd_status
from navigator.overlaps import cmd_overlaps
from navigator.api import search_read, status as api_status
from navigator.search import (
    _apply_path_filters,
    _path_matches_any,
    cmd_search,
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


def _search_args(corpus: Path, query: str, **overrides) -> Namespace:
    base = dict(
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
        limit=10,
        candidates=50,
        output=None,
        batch_size=32,
        batch_pause_ms=0,
        rerank=False,
        rerank_model="unused",
        rerank_api_url="unused",
        rerank_timeout=5,
        rerank_top_n=10,
        path_include=[],
        path_exclude=[],
    )
    base.update(overrides)
    return Namespace(**base)


def _status_args(corpus: Path, **overrides) -> Namespace:
    base = dict(
        path=str(corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=50,
        json=False,
        path_include=[],
        path_exclude=[],
    )
    base.update(overrides)
    return Namespace(**base)


def _overlaps_args(corpus: Path, **overrides) -> Namespace:
    base = dict(
        path=str(corpus),
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
        json=True,
        path_include=[],
        path_exclude=[],
    )
    base.update(overrides)
    return Namespace(**base)


def test_search_path_include_narrows_to_subtree(
    tiny_corpus: Path, mock_embed, capsys
) -> None:
    _index(tiny_corpus)
    capsys.readouterr()

    # Tiny corpus has agents.md, criteria.md, knowledge.md, noise.md at root.
    # Include only criteria.md.
    args = _search_args(tiny_corpus, "приёмки", path_include=["criteria.md"])
    rc = cmd_search(args)
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["engine"]["path_include"] == ["criteria.md"]
    for row in payload["results"]:
        assert "criteria.md" in row["relative_path"]


def test_search_path_exclude_drops_subtree(
    tiny_corpus: Path, mock_embed, capsys
) -> None:
    _index(tiny_corpus)
    capsys.readouterr()

    # Exclude noise.md — everything else should remain.
    args = _search_args(tiny_corpus, "embeddings", path_exclude=["noise.md"])
    rc = cmd_search(args)
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["engine"]["path_exclude"] == ["noise.md"]
    for row in payload["results"]:
        assert "noise.md" not in row["relative_path"]


def test_search_filters_in_engine_metadata(
    tiny_corpus: Path, mock_embed, capsys
) -> None:
    _index(tiny_corpus)
    capsys.readouterr()
    args = _search_args(tiny_corpus, "embeddings")
    rc = cmd_search(args)
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    # Even with no filters, the keys must be present (= empty arrays)
    assert payload["engine"]["path_include"] == []
    assert payload["engine"]["path_exclude"] == []


def test_partial_index_scoped_search_ignores_unindexed_skipped_paths(
    tmp_path: Path, mock_embed, capsys
) -> None:
    corpus = _partial_corpus(tmp_path)
    include = [str(corpus / "keep" / "*.md")]

    _index_args = Namespace(
        path=str(corpus),
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
    assert cmd_index(_index_args) == 0
    capsys.readouterr()

    scoped = _search_args(
        corpus,
        "partial scoped retrieval",
        max_auto_embed=1,
        path_include=include,
    )
    assert cmd_search(scoped) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["results"]
    assert all(row["relative_path"].startswith("keep/") for row in payload["results"])

    unscoped = _search_args(corpus, "partial scoped retrieval", max_auto_embed=1)
    assert cmd_search(unscoped) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["partial_index"]["active"] is True
    assert payload["partial_index"]["pending_files"] == [
        {
            "relative_path": "skip/many.md",
            "added_sections": 9,
            "pending_chunks": 9,
        }
    ]
    assert payload["results"]
    assert all(row["relative_path"].startswith("keep/") for row in payload["results"])

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
    tmp_path: Path, mock_embed, capsys
) -> None:
    corpus = _partial_corpus(tmp_path)
    include = ["keep/*"]
    args = Namespace(
        path=str(corpus),
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
    assert cmd_index(args) == 0
    capsys.readouterr()

    assert cmd_status(_status_args(corpus, max_auto_embed=1, path_include=include)) == 0
    assert "Status: FRESH" in capsys.readouterr().out

    assert cmd_status(_status_args(corpus, max_auto_embed=1)) == 0
    assert "Status: NEEDS WARMUP" in capsys.readouterr().out

    assert cmd_status(_status_args(corpus, max_auto_embed=1, json=True)) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pending_files"] == [
        {
            "relative_path": "skip/many.md",
            "added_sections": 9,
            "pending_chunks": 9,
        }
    ]


def test_status_no_index_reports_pending_chunks_for_dry_run_estimate(
    tmp_path: Path, capsys
) -> None:
    corpus = _partial_corpus(tmp_path)
    assert cmd_status(_status_args(corpus, path_include=["keep/*"])) == 0
    out = capsys.readouterr().out
    assert "Status: NO INDEX" in out
    assert "pending_chunks=" in out
    assert "pending_chunks=0" not in out


def test_status_public_api_and_legacy_json_share_core(
    tmp_path: Path, mock_embed, capsys
) -> None:
    corpus = _partial_corpus(tmp_path)
    _index(corpus)
    capsys.readouterr()

    api_payload = api_status(
        str(corpus),
        path_include=["keep/*"],
        max_auto_embed=1,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
    )

    assert cmd_status(
        _status_args(
            corpus,
            path_include=["keep/*"],
            max_auto_embed=1,
            json=True,
        )
    ) == 0
    legacy_payload = json.loads(capsys.readouterr().out)

    assert legacy_payload == api_payload


def test_partial_index_scoped_overlaps_compares_only_included_chunks(
    tmp_path: Path, mock_embed, capsys
) -> None:
    corpus = _partial_corpus(tmp_path)
    include = ["keep/*"]
    args = Namespace(
        path=str(corpus),
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
    assert cmd_index(args) == 0
    capsys.readouterr()

    assert cmd_overlaps(_overlaps_args(corpus, path_include=include)) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["stats"]["chunks_compared"] == 3
    assert all(
        pair["a"]["relative_path"].startswith("keep/")
        and pair["b"]["relative_path"].startswith("keep/")
        for pair in payload["pairs"]
    )
