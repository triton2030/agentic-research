"""Tests for the agent-contract drifts surfaced by independent review.

Retargeted onto the canonical ``navigator.api`` surface: index / search /
repeated-concepts go through ``api.index`` / ``api.search`` /
``api.repeated_concepts`` (dict payloads with ``_exit_code``), not legacy
``cmd_index`` / ``cmd_search`` / ``cmd_repeated_concepts`` (argparse
Namespace + stdout JSON). The graph recipe builder is imported from its
canonical home ``navigator.graph_reports`` instead of the legacy
``navigator.graph`` re-export shim. No import from ``navigator.cli`` or
``navigator.graph`` remains.

Contract checks preserved:

  1. ``repeated-concepts`` payload carries the machine contract directly —
     ``concepts`` + ``root`` on the returned dict. (The legacy ``--json``
     "always print to stdout, never write a file" behavior was a CLI
     presentation concern; the importable API just returns the dict.)
  2. ``schemas.ALL_SCHEMAS`` covers overlaps + repeated-concepts + cluster.
  3. Search ``engine.rerank_top_n`` + ``engine.rerank_api_url`` surface in
     the payload when rerank applied (only model was visible before).
  4. Single-file corpus → ``relative_path`` is the filename, not the
     absolute path.
  6. Graph-generated related-reading recipes use the ``md`` CLI runner.

Two legacy-CLI-internal tests were dropped (see the inline notes where they
used to live): the argparse manifest/parser-surface consistency check and
the pick/read directory-misuse stderr-recipe checks. Both asserted behavior
that lives only in the legacy ``navigator.cli`` presentation/argument layer
and has no ``navigator.api`` analog.
"""

from __future__ import annotations

from pathlib import Path

from navigator import api
from navigator.folder_map import build_map
from navigator.graph_reports import navigator_read_related_command
from navigator.schemas import ALL_SCHEMAS


def _index(corpus: Path) -> None:
    """Build the index through the canonical API. Mirrors the helper in
    ``tests/test_rerank.py``: ``confirm=True`` to actually embed, success is
    ``_exit_code`` 0 (absent key defaults to 0)."""
    payload = api.index(
        str(corpus),
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


# --- 1. repeated-concepts --json ----------------------------------


def test_repeated_concepts_payload_carries_machine_contract(tiny_corpus, mock_embed):
    """The repeated-concepts payload must expose the machine contract
    directly — ``concepts`` + ``root`` on the returned dict.

    Originally this asserted ``--json`` printed JSON to stdout (never a
    "JSON report → file" marker). That stdout-vs-file behavior was a CLI
    presentation concern; ``api.repeated_concepts`` returns the dict, so the
    check is the same contract minus the stdout-capture machinery."""
    _index(tiny_corpus)

    payload = api.repeated_concepts(
        str(tiny_corpus),
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
        path_include=[],
        path_exclude=[],
    )
    assert payload.get("_exit_code", 0) == 0
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


# NOTE (dropped): ``test_manifest_commands_are_generated_from_parser_surface``
# asserted ``build_manifest()["commands"] == parser_commands()`` — pure
# internal consistency of the legacy ``navigator.cli`` argparse manifest.
# Both functions are legacy-CLI internals with no ``navigator.api`` analog
# (the canonical tool surface is the static ``md_cli`` catalog, covered by
# ``tests/golden/mcp-tool-snapshot.json`` and ``test_navigator_public_api``).
# Removing the ``navigator.cli`` import is the goal of this refactor, and the
# assert had no public-surface meaning, so it was deleted rather than reframed.


def test_overlaps_schema_has_pairs_structure():
    s = ALL_SCHEMAS["overlaps"]
    assert "pairs" in s["properties"]
    pair_props = s["properties"]["pairs"]["items"]["properties"]
    assert {"similarity", "a", "b"} <= set(pair_props.keys())


def test_repeated_concepts_schema_has_concepts_structure():
    s = ALL_SCHEMAS["repeated-concepts"]
    assert "concepts" in s["properties"]
    concept_props = s["properties"]["concepts"]["items"]["properties"]
    assert {"representative", "unique_files", "section_count", "top_handles"} <= set(
        concept_props.keys()
    )


def test_cluster_schema_has_clusters_structure():
    s = ALL_SCHEMAS["cluster"]
    assert "clusters" in s["properties"]
    cluster_props = s["properties"]["clusters"]["items"]["properties"]
    assert {"id", "size", "cohesion", "centroid_section"} <= set(cluster_props.keys())


# --- 3. rerank engine metadata ------------------------------------


def test_search_json_includes_rerank_top_n_when_applied(
    tiny_corpus, mock_embed, monkeypatch
):
    """When rerank fires, engine.rerank_top_n must reflect the cap actually
    used. Was missing — only `rerank_model` was surfaced."""
    from navigator import rerank as rerank_module
    from navigator import search as search_mod

    _index(tiny_corpus)

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
        rerank=True,
        rerank_model="test-rr",
        rerank_api_url="http://test.local/rerank",
        rerank_timeout=5,
        rerank_top_n=15,
        path_include=[],
        path_exclude=[],
    )
    assert payload.get("_exit_code", 0) == 0
    assert payload["engine"]["rerank"] is True
    assert payload["engine"]["rerank_top_n"] == 15
    assert payload["engine"]["rerank_api_url"] == "http://test.local/rerank"


def test_search_json_rerank_metadata_null_when_off(tiny_corpus, mock_embed):
    """Without rerank, the metadata fields are null (not silently absent)."""
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
        path_include=[],
        path_exclude=[],
    )
    assert payload.get("_exit_code", 0) == 0
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


# NOTE (dropped): ``test_pick_on_directory_surfaces_pre_formed_recipe`` and
# ``test_read_on_directory_surfaces_pre_formed_recipe`` exercised
# ``navigator.cli._dispatch_pick_or_read`` — a legacy-CLI argument-resolution
# helper. Their asserts checked stderr wording, ``rc == 2``, and
# copy-pasteable ``md_navigator.py`` two-step recipes with the user's flags
# carried over. That directory-misuse recipe is a CLI presentation contract
# with no ``navigator.api`` analog: ``api.extract`` takes already-parsed map
# data (dict / JSON string) and a known section selection — it never receives
# a directory and never emits ``md_navigator.py`` recipes. Reframing onto the
# public surface would test a different thing, so (like the rerank stderr
# warning dropped in ``tests/test_rerank.py``, which is owned by the
# ``cmd_search`` presentation layer) these were deleted, not migrated. The
# directory-resolution guard itself stays exercised by the legacy CLI tests.


# --- 6. graph related-reading recipe uses the md CLI runner ----


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
    assert "--expanded" in cmd


def _write_graph_doc(
    path: Path,
    *,
    description: str,
    depends_on: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    depends_items = "\n".join(f'  - "{item}"' for item in depends_on or [])
    path.write_text(
        "\n".join(
            [
                "---",
                f'description: "{description}"',
                "depends-on:" if depends_items else "depends-on: []",
                depends_items,
                "---",
                f"# {description}",
                "",
            ]
        ).replace("\n\n---", "\n---"),
        encoding="utf-8",
    )


def test_graph_scan_parent_becomes_root_from_nested_cwd(tmp_path, monkeypatch) -> None:
    """Skill scripts often run from a nested tool folder and pass
    `--scan ../..`. Graph commands must then resolve repo-root links like
    `_ops/...` against the scan root, not the process cwd."""
    from navigator import api

    repo = tmp_path / "repo"
    nested = repo / "experiments" / "md-embedding-server"
    nested.mkdir(parents=True)
    roadmap = repo / "_ops" / "PROJECT-ROADMAP.md"
    task = repo / "_ops" / "plans" / "demo" / "task.md"

    _write_graph_doc(roadmap, description="Roadmap")
    _write_graph_doc(
        task,
        description="Task",
        depends_on=["[[_ops/PROJECT-ROADMAP.md]]"],
    )

    monkeypatch.chdir(nested)

    preflight = api.preflight("../../_ops/plans/demo/task.md", scan="../..")
    assert preflight["_exit_code"] == 0
    assert preflight["file"]["path"] == "_ops/plans/demo/task.md"
    assert preflight["must_read"][0]["status"] == "ok"
    assert preflight["must_read"][0]["path"] == "_ops/PROJECT-ROADMAP.md"

    deps = api.deps("../../_ops/plans/demo/task.md", scan="../..")
    assert deps["file"]["path"] == "_ops/plans/demo/task.md"
    assert deps["fields"]["depends-on"][0]["status"] == "ok"

    impact = api.impact("../../_ops/PROJECT-ROADMAP.md", scan="../..")
    assert impact["file"]["path"] == "_ops/PROJECT-ROADMAP.md"
    assert impact["dependent_breaks"] == [
        {
            "path": "_ops/plans/demo/task.md",
            "description": "Task",
            "has_frontmatter": True,
        }
    ]
