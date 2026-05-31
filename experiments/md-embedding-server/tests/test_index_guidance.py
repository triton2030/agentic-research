from __future__ import annotations

from pathlib import Path

from navigator.api import overlaps, repeated_concepts


def _nested_corpus(tmp_path: Path) -> tuple[Path, Path]:
    parent = tmp_path / "parent corpus"
    child = parent / "child corpus"
    child.mkdir(parents=True)
    (child / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")
    index_dir = parent / ".md-navigator"
    index_dir.mkdir()
    (index_dir / "index.sqlite").write_bytes(b"")
    return parent, child


def _call_kwargs(child: Path) -> dict[str, object]:
    return {
        "corpus": str(child),
        "path_exclude": ["drafts/**"],
        "max_heading_level": 6,
    }


def test_overlaps_parent_guidance_includes_scoped_index_and_rerun(
    tmp_path: Path,
) -> None:
    parent, child = _nested_corpus(tmp_path)

    kwargs = _call_kwargs(child)
    payload = overlaps(kwargs.pop("corpus"), **kwargs)

    assert payload.get("_exit_code", 0) == 4
    assert payload["error"] == "index_warmup_required"

    # The requested path is inside an indexed parent corpus, so the suggested
    # index/rerun corpus flips from the child to the parent.
    assert payload["suggested_index_args"]["corpus"] == str(parent)
    assert payload["suggested_retry_args"]["corpus"] == str(parent)

    # Scoped index args mirror the legacy `md index ... --dry-run` guidance:
    # parent corpus + translated child-relative path filters.
    assert payload["suggested_index_args"] == {
        "corpus": str(parent),
        "path_include": ["child corpus/**"],
        "path_exclude": ["child corpus/drafts/**"],
        "dry_run": True,
    }

    # Scoped retry args mirror the legacy `md overlaps ... --json` re-run line:
    # same parent corpus and same translated path scope.
    assert payload["suggested_retry_args"] == {
        "corpus": str(parent),
        "path_include": ["child corpus/**"],
        "path_exclude": ["child corpus/drafts/**"],
    }


def test_repeated_concepts_parent_guidance_includes_scoped_index_and_rerun(
    tmp_path: Path,
) -> None:
    parent, child = _nested_corpus(tmp_path)

    kwargs = _call_kwargs(child)
    payload = repeated_concepts(kwargs.pop("corpus"), **kwargs)

    assert payload.get("_exit_code", 0) == 4
    assert payload["error"] == "index_warmup_required"

    # The requested path is inside an indexed parent corpus, so the suggested
    # index/rerun corpus flips from the child to the parent.
    assert payload["suggested_index_args"]["corpus"] == str(parent)
    assert payload["suggested_retry_args"]["corpus"] == str(parent)

    # Scoped index args mirror the legacy `md index ... --dry-run` guidance:
    # parent corpus + translated child-relative path filters.
    assert payload["suggested_index_args"] == {
        "corpus": str(parent),
        "path_include": ["child corpus/**"],
        "path_exclude": ["child corpus/drafts/**"],
        "dry_run": True,
    }

    # Scoped retry args mirror the legacy `md repeated-concepts ... --json`
    # re-run line: same parent corpus and same translated path scope.
    assert payload["suggested_retry_args"] == {
        "corpus": str(parent),
        "path_include": ["child corpus/**"],
        "path_exclude": ["child corpus/drafts/**"],
    }
