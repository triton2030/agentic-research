from __future__ import annotations

from pathlib import Path

from navigator import api_graph
from navigator.graph_edges import (
    markdown_links,
    parse_wikilink,
    resolve_markdown_link,
    resolve_target,
    wikilinks_from_text,
)
from navigator.markdown_io import parse_frontmatter


def _run_graph(tmp_path: Path, monkeypatch, command: str, **kwargs) -> tuple[int, dict]:
    """Direct canonical-api call: chdir into the corpus, invoke the
    ``navigator.api_graph`` function for ``command``, and return its payload
    together with the exit code it carries.

    Replaces the old ``build_parser`` argparse roundtrip + stdout JSON parse:
    api functions return the payload dict directly, with ``_exit_code`` baked
    in by ``_exit`` for scan/check. Mutators (init/strip) are called with
    ``confirm=True`` so they take the write path the old ``cmd_*`` --json
    handlers always took.
    """
    monkeypatch.chdir(tmp_path)
    func = getattr(api_graph, command)
    payload = func(**kwargs)
    return payload.get("_exit_code", 0), payload


def test_init_json_live_returns_machine_json_and_respects_include(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "keep.md").write_text("# Keep\n", encoding="utf-8")
    (tmp_path / "skip.md").write_text("# Skip\n", encoding="utf-8")

    rc, payload = _run_graph(
        tmp_path,
        monkeypatch,
        "init",
        paths=["."],
        path_include=["keep.md"],
        confirm=True,
    )

    assert rc == 0
    assert payload == {
        "command": "init",
        "targets": 1,
        "changed": 1,
        "unchanged": 0,
        "modified": ["keep.md"],
    }
    assert parse_frontmatter((tmp_path / "keep.md").read_text(encoding="utf-8").splitlines()) == {
        "description": "TODO",
        "depends-on": [],
    }
    assert (tmp_path / "skip.md").read_text(encoding="utf-8") == "# Skip\n"


def test_strip_json_removes_legacy_and_unknown_fields_preserving_allowed_fields(
    tmp_path: Path, monkeypatch
) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "---\n"
        "description: Keep me\n"
        "depends-on:\n"
        '  - "[[source.md]]"\n'
        "read-before-edit:\n"
        '  - "[[legacy-source.md]]"\n'
        "edit-after-edit: []\n"
        "owner: old-owner\n"
        "custom: remove-me\n"
        "depends_on:\n"
        "  - legacy.md\n"
        "---\n"
        "\n"
        "# Title\n\n"
        "Body stays.\n\n"
        "## Related documents\n"
        "- [[old.md]]\n\n"
        "## Keep\n"
        "Still here.\n",
        encoding="utf-8",
    )

    scan_rc, scan_payload = _run_graph(
        tmp_path, monkeypatch, "scan", paths=["doc.md"]
    )
    assert scan_rc == 1
    assert {issue["code"] for issue in scan_payload["issues"]} >= {
        "LEGACY_FIELD",
        "UNKNOWN_FIELD",
    }

    rc, payload = _run_graph(
        tmp_path, monkeypatch, "strip", paths=["doc.md"], confirm=True
    )

    assert rc == 0
    assert payload["modified"] == ["doc.md"]
    assert payload["changes"] == [
        {
            "path": "doc.md",
            "removed_fields": ["read-before-edit", "edit-after-edit", "owner", "custom", "depends_on"],
            "related_section_removed": False,
        }
    ]
    text = doc.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text.splitlines())
    assert frontmatter == {
        "description": "Keep me",
        "depends-on": ["[[source.md]]"],
    }
    assert "read-before-edit:" not in text
    assert "edit-after-edit:" not in text
    assert "owner:" not in text
    assert "custom:" not in text
    assert "depends_on:" not in text
    assert "## Related documents" in text
    assert "Body stays." in text
    assert "## Keep" in text


def test_strip_related_section_removes_only_related_section_body(
    tmp_path: Path, monkeypatch
) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "---\n"
        "description: Related cleanup\n"
        "depends-on: []\n"
        "---\n"
        "\n"
        "# Title\n\n"
        "Intro stays.\n\n"
        "## Related documents\n"
        "- [[old.md]]\n\n"
        "# Next top-level section\n\n"
        "This must stay.\n",
        encoding="utf-8",
    )

    rc, payload = _run_graph(
        tmp_path,
        monkeypatch,
        "strip",
        paths=["doc.md"],
        also_related_section=True,
        confirm=True,
    )

    assert rc == 0
    assert payload["changes"] == [
        {
            "path": "doc.md",
            "removed_fields": [],
            "related_section_removed": True,
        }
    ]
    text = doc.read_text(encoding="utf-8")
    assert "## Related documents" not in text
    assert "Intro stays." in text
    assert "# Next top-level section" in text
    assert "This must stay." in text


def test_strip_related_section_without_frontmatter_does_not_add_frontmatter(
    tmp_path: Path, monkeypatch
) -> None:
    doc = tmp_path / "plain.md"
    doc.write_text(
        "# Plain\n\n"
        "Intro stays.\n\n"
        "## Related documents\n"
        "- [[old.md]]\n\n"
        "## Next\n\n"
        "This stays.\n",
        encoding="utf-8",
    )

    rc, payload = _run_graph(
        tmp_path,
        monkeypatch,
        "strip",
        paths=["plain.md"],
        also_related_section=True,
        confirm=True,
    )

    assert rc == 0
    assert payload["changes"] == [
        {
            "path": "plain.md",
            "removed_fields": [],
            "related_section_removed": True,
        }
    ]
    text = doc.read_text(encoding="utf-8")
    assert not text.startswith("---")
    assert "## Related documents" not in text
    assert "Intro stays." in text
    assert "## Next" in text


def test_strip_json_respects_include_and_exclude_filters(
    tmp_path: Path, monkeypatch
) -> None:
    for name in ("selected.md", "skipped.md"):
        (tmp_path / name).write_text(
            "---\n"
            f"description: {name}\n"
            "depends-on: []\n"
            "owner: old\n"
            "---\n"
            "\n"
            "# Body\n",
            encoding="utf-8",
        )

    rc, payload = _run_graph(
        tmp_path,
        monkeypatch,
        "strip",
        paths=["."],
        path_include=["*.md"],
        path_exclude=["skipped.md"],
        confirm=True,
    )

    assert rc == 0
    assert payload["modified"] == ["selected.md"]
    assert "owner:" not in (tmp_path / "selected.md").read_text(encoding="utf-8")
    assert "owner:" in (tmp_path / "skipped.md").read_text(encoding="utf-8")


def test_graph_edges_reuse_markdown_io_link_semantics(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    target = tmp_path / "target.md"
    target.write_text("# Target\n\n## Heading\n", encoding="utf-8")
    source.write_text(
        "[[target|alias]] [[target#Heading]] "
        "[relative](<target.md?utm=1#Heading>) "
        "[external](https://example.com) [email](mailto:test@example.com)",
        encoding="utf-8",
    )
    body = source.read_text(encoding="utf-8")

    assert wikilinks_from_text(body) == ["target", "target#Heading"]
    assert parse_wikilink("[[target.md?utm=1#Heading|alias]]") == ("target.md", "Heading")
    assert markdown_links(body) == ["target.md"]
    assert resolve_target("target", source, tmp_path) == target.resolve()
    assert resolve_markdown_link("target.md?utm=1#Heading", source, tmp_path) == target.resolve()
