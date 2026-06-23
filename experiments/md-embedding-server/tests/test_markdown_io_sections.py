from __future__ import annotations

from pathlib import Path

from navigator.markdown_io import (
    extract_section_by_anchor,
    extract_section_by_line,
    find_section_by_anchor,
    strip_frontmatter_text,
)


def test_extract_section_by_line_stops_at_sibling_heading(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text(
        "# Title\n\n## Alpha\n\nBody alpha.\n\n### Child\n\nNested.\n\n## Beta\n\nBody beta.\n",
        encoding="utf-8",
    )

    assert extract_section_by_line(path, 3) == (
        "## Alpha\n\nBody alpha.\n\n### Child\n\nNested."
    )


def test_find_section_by_anchor_normalizes_case_and_whitespace(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\n## Some   Heading\n\nBody.\n", encoding="utf-8")

    section = find_section_by_anchor(path, " some heading ")

    assert section is not None
    assert section.line == 3
    assert section.text == "Some   Heading"
    assert section.content == "## Some   Heading\n\nBody."


def test_extract_section_by_anchor_ignores_fenced_headings(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text(
        "\n".join(
            [
                "# Title",
                "",
                "## Alpha",
                "",
                "```",
                "## Not A Heading",
                "```",
                "",
                "Still alpha.",
                "",
                "## Beta",
                "",
                "Body beta.",
            ]
        ),
        encoding="utf-8",
    )

    assert extract_section_by_anchor(path, "alpha") == (
        "## Alpha\n\n```\n## Not A Heading\n```\n\nStill alpha."
    )


def test_strip_frontmatter_text_removes_yaml_header() -> None:
    text = "---\ndescription: hidden\n---\n\n# Visible\n"

    assert strip_frontmatter_text(text) == "# Visible"


def test_extract_section_by_anchor_returns_none_for_missing_anchor(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\n## Alpha\n\nBody.\n", encoding="utf-8")

    assert extract_section_by_anchor(path, "missing") is None
