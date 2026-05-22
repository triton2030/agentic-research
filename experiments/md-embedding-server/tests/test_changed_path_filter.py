"""Regression: `md changed --path-include / --path-exclude` must narrow the
report set, not silently no-op.

Origin: `_ops/findings/2026-05-22-gpt-5-5-anonymou.md` (entries 13:47, 13:51,
22:44) — git-diff list went straight into preflight reports, bypassing the
filter contract that `load_docs` already honoured.
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from navigator.graph_reports import changed_markdown_paths


class _FakeProc:
    def __init__(self, stdout: str) -> None:
        self.returncode = 0
        self.stdout = stdout
        self.stderr = ""


def _stub_git_diff(stdout: str, monkeypatch) -> None:
    monkeypatch.setattr(
        "navigator.graph_reports.subprocess.run",
        lambda *args, **kwargs: _FakeProc(stdout),
    )


def _touch(root: Path, rel: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# x\n", encoding="utf-8")


def _args(**overrides) -> Namespace:
    base = dict(
        staged=False,
        since=None,
        base=None,
        path_include=[],
        path_exclude=[],
        no_default_excludes=False,
    )
    base.update(overrides)
    return Namespace(**base)


def test_no_filter_returns_all_md_paths(tmp_path: Path, monkeypatch) -> None:
    _touch(tmp_path, "a.md")
    _touch(tmp_path, "b/sub.md")
    _touch(tmp_path, "c/keep.md")
    _stub_git_diff("a.md\nb/sub.md\nc/keep.md\n", monkeypatch)
    result = changed_markdown_paths(tmp_path, _args())
    assert sorted(p.name for p in result) == ["a.md", "keep.md", "sub.md"]


def test_path_include_narrows_to_subtree(tmp_path: Path, monkeypatch) -> None:
    _touch(tmp_path, "a.md")
    _touch(tmp_path, "c/keep.md")
    _touch(tmp_path, "c/inner/deep.md")
    _stub_git_diff("a.md\nc/keep.md\nc/inner/deep.md\n", monkeypatch)
    result = changed_markdown_paths(tmp_path, _args(path_include=["c/*"]))
    rels = sorted(str(p.relative_to(tmp_path)) for p in result)
    assert rels == ["c/inner/deep.md", "c/keep.md"]


def test_path_exclude_drops_subtree(tmp_path: Path, monkeypatch) -> None:
    _touch(tmp_path, "a.md")
    _touch(tmp_path, "drafts/scratch.md")
    _stub_git_diff("a.md\ndrafts/scratch.md\n", monkeypatch)
    result = changed_markdown_paths(tmp_path, _args(path_exclude=["drafts/*"]))
    rels = sorted(str(p.relative_to(tmp_path)) for p in result)
    assert rels == ["a.md"]


def test_default_excludes_skip_dot_dirs(tmp_path: Path, monkeypatch) -> None:
    _touch(tmp_path, "a.md")
    _touch(tmp_path, ".git/info.md")
    _stub_git_diff("a.md\n.git/info.md\n", monkeypatch)
    result = changed_markdown_paths(tmp_path, _args())
    rels = sorted(str(p.relative_to(tmp_path)) for p in result)
    assert rels == ["a.md"]


def test_no_default_excludes_lets_dot_dirs_through(
    tmp_path: Path, monkeypatch
) -> None:
    _touch(tmp_path, ".github/notes.md")
    _stub_git_diff(".github/notes.md\n", monkeypatch)
    result = changed_markdown_paths(
        tmp_path, _args(no_default_excludes=True)
    )
    rels = sorted(str(p.relative_to(tmp_path)) for p in result)
    assert rels == [".github/notes.md"]
