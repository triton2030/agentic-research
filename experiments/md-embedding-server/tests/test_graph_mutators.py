from __future__ import annotations

import json
from pathlib import Path

from navigator.graph import build_parser
from navigator.markdown_io import parse_frontmatter


def _run_graph(tmp_path: Path, monkeypatch, capsys, argv: list[str]) -> tuple[int, dict]:
    monkeypatch.chdir(tmp_path)
    parser = build_parser()
    args = parser.parse_args(argv)
    rc = args.func(args)
    captured = capsys.readouterr()
    return rc, json.loads(captured.out)


def test_init_json_live_returns_machine_json_and_respects_include(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    (tmp_path / "keep.md").write_text("# Keep\n", encoding="utf-8")
    (tmp_path / "skip.md").write_text("# Skip\n", encoding="utf-8")

    rc, payload = _run_graph(
        tmp_path,
        monkeypatch,
        capsys,
        ["init", "--json", "--path-include", "keep.md", "."],
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
        "read-before-edit": [],
        "edit-after-edit": [],
    }
    assert (tmp_path / "skip.md").read_text(encoding="utf-8") == "# Skip\n"


def test_strip_json_removes_legacy_and_unknown_fields_preserving_allowed_fields(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "---\n"
        "description: Keep me\n"
        "read-before-edit:\n"
        '  - "[[source.md]]"\n'
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
        tmp_path, monkeypatch, capsys, ["scan", "--json", "doc.md"]
    )
    assert scan_rc == 1
    assert {issue["code"] for issue in scan_payload["issues"]} >= {
        "LEGACY_FIELD",
        "UNKNOWN_FIELD",
    }

    rc, payload = _run_graph(
        tmp_path, monkeypatch, capsys, ["strip", "--json", "doc.md"]
    )

    assert rc == 0
    assert payload["modified"] == ["doc.md"]
    assert payload["changes"] == [
        {
            "path": "doc.md",
            "removed_fields": ["owner", "custom", "depends_on"],
            "related_section_removed": False,
        }
    ]
    text = doc.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text.splitlines())
    assert frontmatter == {
        "description": "Keep me",
        "read-before-edit": ["[[source.md]]"],
        "edit-after-edit": [],
    }
    assert "owner:" not in text
    assert "custom:" not in text
    assert "depends_on:" not in text
    assert "## Related documents" in text
    assert "Body stays." in text
    assert "## Keep" in text


def test_strip_related_section_removes_only_related_section_body(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "---\n"
        "description: Related cleanup\n"
        "read-before-edit: []\n"
        "edit-after-edit: []\n"
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
        capsys,
        ["strip", "--json", "--also-related-section", "doc.md"],
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
    tmp_path: Path, monkeypatch, capsys
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
        capsys,
        ["strip", "--json", "--also-related-section", "plain.md"],
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
    tmp_path: Path, monkeypatch, capsys
) -> None:
    for name in ("selected.md", "skipped.md"):
        (tmp_path / name).write_text(
            "---\n"
            f"description: {name}\n"
            "read-before-edit: []\n"
            "edit-after-edit: []\n"
            "owner: old\n"
            "---\n"
            "\n"
            "# Body\n",
            encoding="utf-8",
        )

    rc, payload = _run_graph(
        tmp_path,
        monkeypatch,
        capsys,
        [
            "strip",
            "--json",
            "--path-include",
            "*.md",
            "--path-exclude",
            "skipped.md",
            ".",
        ],
    )

    assert rc == 0
    assert payload["modified"] == ["selected.md"]
    assert "owner:" not in (tmp_path / "selected.md").read_text(encoding="utf-8")
    assert "owner:" in (tmp_path / "skipped.md").read_text(encoding="utf-8")
