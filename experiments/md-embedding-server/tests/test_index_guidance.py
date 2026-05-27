from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from navigator.overlaps import cmd_overlaps
from navigator.repeated_concepts import cmd_repeated_concepts


def _nested_corpus(tmp_path: Path) -> tuple[Path, Path]:
    parent = tmp_path / "parent corpus"
    child = parent / "child corpus"
    child.mkdir(parents=True)
    (child / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")
    index_dir = parent / ".md-navigator"
    index_dir.mkdir()
    (index_dir / "index.sqlite").write_bytes(b"")
    return parent, child


def _args(child: Path) -> Namespace:
    return Namespace(
        path=str(child),
        path_include=None,
        path_exclude=["drafts/**"],
        max_heading_level=6,
        cache_dir=None,
    )


def test_overlaps_parent_guidance_includes_scoped_index_and_rerun(
    tmp_path: Path,
    capsys,
) -> None:
    parent, child = _nested_corpus(tmp_path)

    assert cmd_overlaps(_args(child)) == 4

    stderr = capsys.readouterr().err
    assert f"Requested path is inside indexed parent corpus: {parent}" in stderr
    assert (
        f"md index '{parent}' --path-include 'child corpus/**' "
        "--path-exclude 'child corpus/drafts/**' --dry-run --json"
    ) in stderr
    assert (
        f"md index '{parent}' --path-include 'child corpus/**' "
        "--path-exclude 'child corpus/drafts/**' --confirm --transaction-id <id> --json"
    ) in stderr
    assert (
        f"md overlaps '{parent}' --path-include 'child corpus/**' "
        "--path-exclude 'child corpus/drafts/**' --json"
    ) in stderr


def test_repeated_concepts_parent_guidance_includes_scoped_index_and_rerun(
    tmp_path: Path,
    capsys,
) -> None:
    parent, child = _nested_corpus(tmp_path)

    assert cmd_repeated_concepts(_args(child)) == 4

    stderr = capsys.readouterr().err
    assert f"Requested path is inside indexed parent corpus: {parent}" in stderr
    assert (
        f"md index '{parent}' --path-include 'child corpus/**' "
        "--path-exclude 'child corpus/drafts/**' --dry-run --json"
    ) in stderr
    assert (
        f"md index '{parent}' --path-include 'child corpus/**' "
        "--path-exclude 'child corpus/drafts/**' --confirm --transaction-id <id> --json"
    ) in stderr
    assert (
        f"md repeated-concepts '{parent}' --path-include 'child corpus/**' "
        "--path-exclude 'child corpus/drafts/**' --json"
    ) in stderr
