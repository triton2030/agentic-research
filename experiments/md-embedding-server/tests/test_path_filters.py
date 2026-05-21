"""Path-filter tests: --path-include / --path-exclude narrow the result
set by relative_path with fnmatch-style globs. Substring fallback for
non-glob patterns. Filters apply before rerank so the cross-encoder
budget isn't spent on dropped candidates."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from navigator.index import cmd_index
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
