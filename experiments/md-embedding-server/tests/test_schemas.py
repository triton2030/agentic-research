"""Schema-layer tests: schemas are well-formed JSON Schema docs and
match the actual `--json` output of search/map commands."""

from __future__ import annotations

from pathlib import Path

from navigator.api import index, search
from navigator.schemas import (
    ALL_SCHEMAS,
    SCHEMA_DIALECT,
    SCHEMA_VERSION,
)


def test_schema_version_is_semver_like() -> None:
    parts = SCHEMA_VERSION.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


def test_all_schemas_have_required_keys() -> None:
    for name, schema in ALL_SCHEMAS.items():
        assert schema.get("$schema") == SCHEMA_DIALECT, f"{name} missing dialect"
        assert "type" in schema, f"{name} missing top-level type"
        assert "title" in schema, f"{name} missing title"


def test_search_schema_describes_top_level_fields() -> None:
    s = ALL_SCHEMAS["search"]
    required = set(s["required"])
    assert required >= {"root", "query", "scope", "engine", "stats", "results"}
    # result row spec includes the key handles agents read
    row = s["properties"]["results"]["items"]
    row_required = set(row["required"])
    assert row_required >= {
        "section_id",
        "relative_path",
        "start_line",
        "heading_chain",
        "rrf_score",
        "fields_hit",
    }


def test_search_read_schema_describes_body_sections() -> None:
    s = ALL_SCHEMAS["search-read"]
    required = set(s["required"])
    assert required >= {"root", "query", "scope", "sections", "expanded", "token_total"}
    row = s["properties"]["sections"]["items"]
    assert set(row["required"]) >= {"section_id", "relative_path", "start_line"}
    assert "content" in row["properties"]


def test_specific_schema_is_retrievable_by_target() -> None:
    """A named schema is reachable as data and carries its dialect/title.
    (Replaces the retired `md schema --for search` CLI test — same intent:
    one schema is extractable by key.)"""
    schema = ALL_SCHEMAS["search"]
    assert schema["$schema"] == SCHEMA_DIALECT
    assert schema["title"] == "md-navigator search output"


def test_all_schemas_map_covers_every_target() -> None:
    """The whole-schema map exposes every documented target alongside the
    version constant. (Replaces the retired `md schema --for all` CLI test —
    same intent: the map of all schemas is available.)"""
    assert SCHEMA_VERSION  # version constant published for consumers
    assert set(ALL_SCHEMAS) >= {
        "search",
        "search-read",
        "map",
        "headings",
        "status",
        "overlaps",
        "repeated-concepts",
        "cluster",
        "audit",
    }
    for name, schema in ALL_SCHEMAS.items():
        assert schema["$schema"] == SCHEMA_DIALECT, f"{name} missing dialect"


# Dropped: test_cmd_schema_unknown_target_returns_2. Its intent was purely
# CLI behaviour ("md schema" prints "Unknown schema target" + returns exit
# code 2). With the legacy CLI gone there is no product equivalent — an
# unknown key is just a dict miss, already implied by the membership checks
# above. No data-level contract to assert, so the test is removed.


def test_search_json_output_matches_schema_required_keys(
    tiny_corpus: Path, mock_embed
) -> None:
    """Build index, run search, verify the result has every required
    field from the schema. Catches drift where a render change forgets
    a field."""
    # Build the index first. `confirm=True` performs the real embed pass;
    # the default dry-run would not produce a searchable index.
    index_payload = index(
        str(tiny_corpus),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )
    assert index_payload.get("_exit_code", 0) == 0

    payload = search(
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
    )
    assert payload.get("_exit_code", 0) == 0

    required_top = set(ALL_SCHEMAS["search"]["required"])
    assert required_top <= set(payload.keys()), (
        f"Missing top-level keys: {required_top - set(payload.keys())}"
    )

    if payload["results"]:
        required_row = set(ALL_SCHEMAS["search"]["properties"]["results"]["items"]["required"])
        first_row = payload["results"][0]
        missing = required_row - set(first_row.keys())
        assert not missing, f"Result row missing required keys: {missing}"
