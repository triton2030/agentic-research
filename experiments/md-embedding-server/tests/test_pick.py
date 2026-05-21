"""Tests for `pick` extraction semantics — specifically the bundled fix:
`pick --files X --extract` must auto-expand to all headings of those files
(intent: "give me the content of file X"). Without --extract, behaviour is
metadata-only — backward compat preserved."""

from __future__ import annotations

from pathlib import Path

from navigator.pick import pick_items


def _tiny_map(tmp_path: Path) -> dict:
    """Two-file map with three headings each, body content per heading."""
    a = tmp_path / "a.md"
    a.write_text(
        "# A\n\n## A.one\n\nbody a1.\n\n## A.two\n\nbody a2.\n",
        encoding="utf-8",
    )
    b = tmp_path / "b.md"
    b.write_text(
        "# B\n\n## B.one\n\nbody b1.\n\n## B.two\n\nbody b2.\n",
        encoding="utf-8",
    )
    return {
        "root": str(tmp_path),
        "file_count": 2,
        "files": [
            {
                "id": 1,
                "path": str(a),
                "relative_path": "a.md",
                "description": "",
                "title": "A",
                "heading_count": 3,
                "headings": [
                    {"id": "1.1", "line": 1, "level": 1, "text": "A"},
                    {"id": "1.2", "line": 3, "level": 2, "text": "A.one"},
                    {"id": "1.3", "line": 7, "level": 2, "text": "A.two"},
                ],
            },
            {
                "id": 2,
                "path": str(b),
                "relative_path": "b.md",
                "description": "",
                "title": "B",
                "heading_count": 3,
                "headings": [
                    {"id": "2.1", "line": 1, "level": 1, "text": "B"},
                    {"id": "2.2", "line": 3, "level": 2, "text": "B.one"},
                    {"id": "2.3", "line": 7, "level": 2, "text": "B.two"},
                ],
            },
        ],
    }


def test_pick_files_with_extract_auto_includes_all_sections(tmp_path: Path) -> None:
    """`pick --files 1 --extract` must pull headings of file 1 with content."""
    data = _tiny_map(tmp_path)
    out = pick_items(
        data,
        file_ids={"1"},
        heading_ids=set(),
        extract=True,
    )
    head_ids = {h["id"] for h in out["headings"]}
    assert head_ids == {"1.1", "1.2", "1.3"}, f"Expected all of file 1 headings, got {head_ids}"
    # Every heading must carry `content` because extract=True
    assert all("content" in h for h in out["headings"])


def test_pick_files_without_extract_keeps_metadata_only(tmp_path: Path) -> None:
    """Backward compat — without --extract, headings list stays empty."""
    data = _tiny_map(tmp_path)
    out = pick_items(
        data,
        file_ids={"1"},
        heading_ids=set(),
        extract=False,
    )
    assert out["headings"] == []
    assert len(out["files"]) == 1
    assert out["files"][0]["id"] == 1


def test_pick_files_and_headings_union_when_extract(tmp_path: Path) -> None:
    """Explicit --headings remain additive (union, not override)."""
    data = _tiny_map(tmp_path)
    out = pick_items(
        data,
        file_ids={"1"},          # → 1.1, 1.2, 1.3
        heading_ids={"2.2"},     # → plus 2.2
        extract=True,
    )
    head_ids = {h["id"] for h in out["headings"]}
    assert head_ids == {"1.1", "1.2", "1.3", "2.2"}


def test_pick_files_extract_two_files(tmp_path: Path) -> None:
    """Multi-file selection."""
    data = _tiny_map(tmp_path)
    out = pick_items(
        data,
        file_ids={"1", "2"},
        heading_ids=set(),
        extract=True,
    )
    head_ids = {h["id"] for h in out["headings"]}
    assert head_ids == {"1.1", "1.2", "1.3", "2.1", "2.2", "2.3"}
