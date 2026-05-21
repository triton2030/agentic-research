"""Schema-layer tests: schemas are well-formed JSON Schema docs and
match the actual `--json` output of search/map commands."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from navigator.index import cmd_index
from navigator.schemas import (
    ALL_SCHEMAS,
    SCHEMA_DIALECT,
    SCHEMA_VERSION,
    cmd_schema,
)
from navigator.search import cmd_search


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


def test_cmd_schema_prints_specific_target(capsys) -> None:
    args = Namespace(target="search")
    rc = cmd_schema(args)
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["version"] == SCHEMA_VERSION
    assert payload["for"] == "search"


def test_cmd_schema_all_returns_map(capsys) -> None:
    args = Namespace(target="all")
    rc = cmd_schema(args)
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["version"] == SCHEMA_VERSION
    assert "schemas" in payload
    for key in ALL_SCHEMAS:
        assert key in payload["schemas"]


def test_cmd_schema_unknown_target_returns_2(capsys) -> None:
    args = Namespace(target="nonexistent")
    rc = cmd_schema(args)
    err = capsys.readouterr().err
    assert rc == 2
    assert "Unknown schema target" in err


def test_search_json_output_matches_schema_required_keys(
    tiny_corpus: Path, mock_embed, capsys
) -> None:
    """Build index, run search --json, verify the result has every
    required field from the schema. Catches drift where a render change
    forgets a field."""
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

    search_args = Namespace(
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
    )
    assert cmd_search(search_args) == 0
    out = capsys.readouterr().out
    payload = json.loads(out)

    required_top = set(ALL_SCHEMAS["search"]["required"])
    assert required_top <= set(payload.keys()), (
        f"Missing top-level keys: {required_top - set(payload.keys())}"
    )

    if payload["results"]:
        required_row = set(ALL_SCHEMAS["search"]["properties"]["results"]["items"]["required"])
        first_row = payload["results"][0]
        missing = required_row - set(first_row.keys())
        assert not missing, f"Result row missing required keys: {missing}"
