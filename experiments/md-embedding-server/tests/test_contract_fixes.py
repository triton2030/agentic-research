"""Tests for the 5 agent-contract drifts surfaced by independent review:

  1. `repeated-concepts --json` now ALWAYS prints to stdout (used to
     silently write a file unless `--stdout` was also passed).
  2. `schemas.ALL_SCHEMAS` covers overlaps + repeated-concepts +
     cluster (used to be missing).
  3. Search engine.rerank_top_n + engine.rerank_api_url surfaced in
     JSON when rerank applied (only model was visible before).
  4. Single-file corpus → `relative_path` is the filename, not the
     absolute path (used to leak the absolute path).
  5. `read-related --token-budget` help text now flags best-effort
     semantics (anchor never trimmed).
  6. Graph-generated related-reading recipes use the uv script runner
     instead of raw `python3`, so inline script dependencies resolve.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from navigator.cli import build_manifest, parser_commands
from navigator.folder_map import build_map
from navigator.graph import navigator_read_related_command
from navigator.index import cmd_index
from navigator.schemas import ALL_SCHEMAS
from navigator.search import cmd_search


# --- 1. repeated-concepts --json ----------------------------------


def test_repeated_concepts_json_prints_to_stdout(tiny_corpus, mock_embed, capsys):
    """`--json` must print JSON to stdout regardless of --stdout."""
    from navigator.repeated_concepts import cmd_repeated_concepts

    # Build the index first.
    index_args = Namespace(
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
    assert cmd_index(index_args) == 0
    capsys.readouterr()

    rc_args = Namespace(
        path=str(tiny_corpus),
        threshold=0.0,
        top=10,
        min_tokens=0,
        min_files=1,
        min_sections=1,
        top_members=3,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        json=True,
        stdout=False,
        output=None,
        path_include=[],
        path_exclude=[],
    )
    rc = cmd_repeated_concepts(rc_args)
    captured = capsys.readouterr()
    assert rc == 0
    # Stdout must contain a parseable JSON object — NOT a "JSON report → ..." marker.
    assert "JSON report →" not in captured.out
    payload = json.loads(captured.out)
    assert "concepts" in payload
    assert "root" in payload


# --- 2. schemas completeness --------------------------------------


def test_all_schemas_cover_stable_machine_contracts():
    """Stable agent-facing JSON contracts must have schema entries. Catches
    the agent-contract drift the user surfaced: overlaps +
    repeated-concepts + cluster used to be missing."""
    required = {
        "search",
        "map",
        "headings",
        "status",
        "overlaps",
        "repeated-concepts",
        "cluster",
    }
    missing = required - set(ALL_SCHEMAS.keys())
    assert not missing, f"Schemas missing for: {missing}"


def test_manifest_commands_are_generated_from_parser_surface():
    """The manifest must not drift from argparse choices when a command is
    added or removed."""
    assert build_manifest()["commands"] == parser_commands()


def test_overlaps_schema_has_pairs_structure():
    s = ALL_SCHEMAS["overlaps"]
    assert "pairs" in s["properties"]
    pair_props = s["properties"]["pairs"]["items"]["properties"]
    assert {"similarity", "a", "b"} <= set(pair_props.keys())


def test_repeated_concepts_schema_has_concepts_structure():
    s = ALL_SCHEMAS["repeated-concepts"]
    assert "concepts" in s["properties"]
    concept_props = s["properties"]["concepts"]["items"]["properties"]
    assert {"representative", "unique_files", "section_count", "members"} <= set(
        concept_props.keys()
    )


def test_cluster_schema_has_clusters_structure():
    s = ALL_SCHEMAS["cluster"]
    assert "clusters" in s["properties"]
    cluster_props = s["properties"]["clusters"]["items"]["properties"]
    assert {"id", "size", "cohesion", "centroid_section"} <= set(cluster_props.keys())


# --- 3. rerank engine metadata ------------------------------------


def test_search_json_includes_rerank_top_n_when_applied(
    tiny_corpus, mock_embed, monkeypatch, capsys
):
    """When rerank fires, engine.rerank_top_n must reflect the cap actually
    used. Was missing — only `rerank_model` was surfaced."""
    from navigator import rerank as rerank_module
    from navigator import search as search_mod

    index_args = Namespace(
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
    assert cmd_index(index_args) == 0
    capsys.readouterr()

    monkeypatch.setattr(
        rerank_module,
        "rerank_documents",
        lambda q, docs, **kw: [(i, 1.0 - i * 0.1) for i in range(len(docs))],
    )
    monkeypatch.setattr(
        search_mod,
        "rerank_documents",
        lambda q, docs, **kw: [(i, 1.0 - i * 0.1) for i in range(len(docs))],
    )

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
        rerank=True,
        rerank_model="test-rr",
        rerank_api_url="http://test.local/rerank",
        rerank_timeout=5,
        rerank_top_n=15,
        path_include=[],
        path_exclude=[],
    )
    assert cmd_search(args) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["engine"]["rerank"] is True
    assert payload["engine"]["rerank_top_n"] == 15
    assert payload["engine"]["rerank_api_url"] == "http://test.local/rerank"


def test_search_json_rerank_metadata_null_when_off(tiny_corpus, mock_embed, capsys):
    """Without --rerank, the metadata fields are null (not silently absent)."""
    index_args = Namespace(
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
    assert cmd_index(index_args) == 0
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
        path_include=[],
        path_exclude=[],
    )
    assert cmd_search(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["engine"]["rerank"] is False
    assert payload["engine"]["rerank_top_n"] is None
    assert payload["engine"]["rerank_api_url"] is None


# --- 4. single-file corpus relative_path ---------------------------


def test_single_file_corpus_relative_path_is_filename(tmp_path):
    """Field literally named `relative_path` must not be absolute when
    the corpus root is a single file."""
    f = tmp_path / "one_file.md"
    f.write_text("# Single\n\nBody.\n", encoding="utf-8")

    data = build_map(f, max_heading_level=6, with_tokens=False)
    assert data["file_count"] == 1
    rel = data["files"][0]["relative_path"]
    assert rel == "one_file.md", f"Expected 'one_file.md', got {rel!r}"
    assert not Path(rel).is_absolute()


# --- 6. pick/read on a directory: helpful error, not IsADirectoryError ----


def test_pick_on_directory_surfaces_pre_formed_recipe(tmp_path, capsys):
    """Passing a directory where a JSON map is expected used to crash with
    `IsADirectoryError` from `read_text`. The dispatcher must instead name
    the surface confusion (`map`/`headings` take directories, `pick` takes
    their JSON output) and pre-form both next commands with the user's
    actual flags, so the recipe is copy-pasteable."""
    from navigator.cli import _dispatch_pick_or_read

    d = tmp_path / "some-folder"
    d.mkdir()
    (d / "a.md").write_text("# A\n\nbody\n", encoding="utf-8")

    args = Namespace(
        command="pick",
        map_json=str(d),
        map_alias=None,
        files="",
        headings="5.1,4.1,2.1",
        extract=True,
        token_budget=0,
        json=False,
    )
    rc = _dispatch_pick_or_read(args)
    err = capsys.readouterr().err

    assert rc == 2
    assert "expects a JSON map" in err
    assert "not a directory" in err
    # Two-step recipe present.
    assert "md_navigator.py headings" in err
    assert "md_navigator.py pick" in err
    # User's flags carried over verbatim.
    assert "--headings 5.1,4.1,2.1" in err
    assert "--extract" in err


def test_read_on_directory_surfaces_pre_formed_recipe(tmp_path, capsys):
    """Same guard for `read`: directory input must not crash with
    IsADirectoryError; recipe must propose `read` (not `pick`) as the
    second step."""
    from navigator.cli import _dispatch_pick_or_read

    d = tmp_path / "another-folder"
    d.mkdir()
    (d / "a.md").write_text("# A\n\nbody\n", encoding="utf-8")

    args = Namespace(
        command="read",
        map_json=str(d),
        map_alias=None,
        files="1",
        headings="",
        token_budget=0,
        json=False,
        output=None,
        offset=1,
        limit=2000,
        line_numbers=False,
    )
    rc = _dispatch_pick_or_read(args)
    err = capsys.readouterr().err

    assert rc == 2
    assert "md_navigator.py read" in err
    assert "--files 1" in err


def test_graph_related_reading_recipe_uses_md_cli():
    cmd = navigator_read_related_command(
        "knowledge/agents/tool-design.md",
        scan="knowledge",
        token_budget=3000,
    )

    assert cmd.startswith("md read-related --paths ")
    assert " python3 " not in f" {cmd} "
    assert "md_navigator.py" not in cmd
    assert "--paths knowledge/agents/tool-design.md" in cmd
    assert "--scan knowledge" in cmd
    assert "--token-budget 3000" in cmd
