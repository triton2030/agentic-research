"""Graph I/O primitives: Doc/Finding/Edge classes, frontmatter loaders, path traversal.

This module owns the lowest layer of the graph backend: how files become Doc
objects, how findings are reported, how Edge structures are shaped. Higher
layers (link resolution, report builders, CLI) import from here.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .markdown_io import parse_frontmatter

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("PyYAML is required: python3 -m pip install pyyaml", file=sys.stderr)
    sys.exit(2)


GRAPH_FIELDS = ("read-before-edit", "edit-after-edit")
REQUIRED_FIELDS = ("description",)
LEGACY_FIELDS = (
    "owner",
    "parents",
    "children",
    "siblings",
    "status",
    "source_of_truth",
    "updated_at",
    "depends_on",
)
ALLOWED_FIELDS = {"description", "read-before-edit", "edit-after-edit"}
RELATED_SECTION_RE = re.compile(
    r"(?ms)^##\s+(?:Связанные документы|Related documents)\s*\n.*?(?=^#{1,2}\s|\Z)"
)
NAVIGATOR_SCRIPT = str(
    Path(__file__).resolve().parent.parent / "md_navigator.py"
)


@dataclass
class Doc:
    path: Path
    rel: Path
    has_frontmatter: bool
    frontmatter: dict
    body: str


@dataclass
class Finding:
    code: str
    path: Path
    detail: str

    def render(self) -> str:
        return f"{self.code} | {self.path} | {self.detail}"


@dataclass
class Edge:
    source: Doc
    raw_link: str
    target: Doc | None
    target_raw: str
    anchor: str | None


def repo_root() -> Path:
    return Path.cwd().resolve()


def safe_rel(path: Path, root: Path) -> Path:
    try:
        return path.resolve().relative_to(root)
    except ValueError:
        return path.resolve()


def _path_passes(
    item: Path,
    root: Path,
    include: list[str],
    exclude: list[str],
    use_default_excludes: bool,
) -> bool:
    rel = safe_rel(item, root)
    rel_str = str(rel)
    if use_default_excludes:
        for part in rel.parts[:-1]:
            if part.startswith(".") and part not in (".", ".."):
                return False
    if exclude:
        for pattern in exclude:
            if fnmatch.fnmatchcase(rel_str, pattern):
                return False
    if include:
        for pattern in include:
            if fnmatch.fnmatchcase(rel_str, pattern):
                return True
        return False
    return True


def iter_markdown(
    paths: Iterable[str],
    root: Path,
    include: Iterable[str] = (),
    exclude: Iterable[str] = (),
    use_default_excludes: bool = True,
) -> list[Path]:
    raw_paths = list(paths) or ["."]
    include_patterns = list(include)
    exclude_patterns = list(exclude)
    found: dict[Path, None] = {}
    for raw in raw_paths:
        path = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
        if not path.exists():
            raise SystemExit(f"Path not found: {raw}")
        if path.is_file():
            if path.suffix.lower() == ".md":
                if _path_passes(path, root, include_patterns, exclude_patterns, use_default_excludes):
                    found[path] = None
            continue
        for item in path.rglob("*.md"):
            if not _path_passes(item, root, include_patterns, exclude_patterns, use_default_excludes):
                continue
            found[item.resolve()] = None
    return sorted(found, key=lambda p: str(safe_rel(p, root)))


def split_frontmatter(text: str) -> tuple[bool, list[str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False, [], text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body = "\n".join(lines[index + 1 :])
            if text.endswith("\n"):
                body += "\n"
            return True, lines[1:index], body
    return False, [], text


def load_doc(path: Path, root: Path) -> Doc:
    text = path.read_text(encoding="utf-8")
    has_frontmatter, _lines, body = split_frontmatter(text)
    frontmatter: dict = parse_frontmatter(text.splitlines()) if has_frontmatter else {}
    return Doc(path=path, rel=safe_rel(path, root), has_frontmatter=has_frontmatter, frontmatter=frontmatter, body=body)


def load_docs(paths: Iterable[str], root: Path, args: argparse.Namespace | None = None) -> list[Doc]:
    include = getattr(args, "path_include", None) or []
    exclude = getattr(args, "path_exclude", None) or []
    use_defaults = not getattr(args, "no_default_excludes", False)
    return [
        load_doc(path, root)
        for path in iter_markdown(
            paths, root, include=include, exclude=exclude, use_default_excludes=use_defaults,
        )
    ]


def dump_frontmatter(data: dict) -> str:
    ordered: dict = {"description": data.get("description", "")}
    for key in GRAPH_FIELDS:
        ordered[key] = data.get(key) or []
    for key, value in data.items():
        if key not in ordered and key not in LEGACY_FIELDS:
            ordered[key] = value
    return yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False).strip()


def write_doc(doc: Doc, frontmatter: dict, body: str | None = None) -> None:
    body_text = doc.body if body is None else body
    new_text = f"---\n{dump_frontmatter(frontmatter)}\n---\n"
    if body_text:
        new_text += body_text if body_text.startswith("\n") else body_text
    doc.path.write_text(new_text, encoding="utf-8")


def load_target_doc(path_value: str, root: Path) -> Doc:
    target_path = (root / path_value).resolve() if not Path(path_value).is_absolute() else Path(path_value).resolve()
    if not target_path.exists():
        raise SystemExit(f"Path not found: {path_value}")
    return load_doc(target_path, root)
