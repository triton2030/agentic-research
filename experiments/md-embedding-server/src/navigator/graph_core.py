"""Graph I/O primitives: Doc/Finding/Edge classes, frontmatter loaders, path traversal.

This module owns the lowest layer of the graph backend: how files become Doc
objects, how findings are reported, how Edge structures are shaped. Higher
layers (link resolution, report builders, CLI) import from here.
"""

from __future__ import annotations

import fnmatch
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .markdown_io import DEFAULT_EXCLUDED_PARTS, parse_frontmatter

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise ImportError(
        "PyYAML is required: python3 -m pip install pyyaml"
    ) from exc


class PathNotFound(Exception):
    """A requested Markdown path/scan target does not exist on disk.

    Raised by the loaders below instead of ``SystemExit`` so the CLI runner's
    exception fence (``md_cli.handlers._generic._call``) can turn it into a
    normal error envelope. Carries the original path value for the payload.
    """

    def __init__(self, path_value: str) -> None:
        self.path_value = path_value
        super().__init__(f"Path not found: {path_value}")


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


@dataclass(frozen=True)
class DocWrite:
    doc: Doc
    text: str

    @classmethod
    def from_frontmatter(cls, doc: Doc, frontmatter: dict, body: str) -> DocWrite:
        return cls(doc=doc, text=_doc_text(frontmatter, body))

    @classmethod
    def from_text(cls, doc: Doc, text: str) -> DocWrite:
        return cls(doc=doc, text=text)


@dataclass
class GraphArgs:
    """Explicit load filters for the graph backend.

    Replaces the fabricated ``argparse.Namespace`` the api layer used to build
    just to carry path filters into :func:`load_docs`. No parser, no CLI shape —
    only the four fields ``load_docs`` actually reads.
    """

    paths: list[str] = field(default_factory=lambda: ["."])
    path_include: list[str] = field(default_factory=list)
    path_exclude: list[str] = field(default_factory=list)
    no_default_excludes: bool = False


def repo_root() -> Path:
    return Path.cwd().resolve()


def _resolve_invocation_path(path_value: str, root: Path) -> Path:
    raw = Path(path_value).expanduser()
    if raw.is_absolute():
        return raw.resolve()
    cwd_candidate = (Path.cwd() / raw).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    return (root / raw).resolve()


def _scan_anchor(scan_path: Path) -> Path:
    if scan_path.exists() and scan_path.is_file():
        return scan_path.parent
    return scan_path


def root_for_scan(scan: str | None) -> Path:
    cwd = repo_root()
    if not scan:
        return cwd
    scan_path = _resolve_invocation_path(scan, cwd)
    scan_anchor = _scan_anchor(scan_path)
    try:
        scan_anchor.relative_to(cwd)
        return cwd
    except ValueError:
        return scan_anchor


def scan_scope_path(scan: str | None, root: Path) -> Path:
    if not scan:
        return root
    return _resolve_invocation_path(scan, root)


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
        if not DEFAULT_EXCLUDED_PARTS.isdisjoint(rel.parts):
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
            raise PathNotFound(raw)
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


def load_docs(paths: Iterable[str], root: Path, args: GraphArgs | None = None) -> list[Doc]:
    include = list(args.path_include) if args else []
    exclude = list(args.path_exclude) if args else []
    use_defaults = not (args.no_default_excludes if args else False)
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
    _atomic_replace_text(doc.path, _doc_text(frontmatter, body_text))


def _doc_text(frontmatter: dict, body: str) -> str:
    new_text = f"---\n{dump_frontmatter(frontmatter)}\n---\n"
    if body:
        new_text += body if body.startswith("\n") else body
    return new_text


def _atomic_replace_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        tmp_path = Path(handle.name)
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)


def write_doc_plan(plan: Iterable[DocWrite]) -> None:
    entries = list(plan)
    originals = {entry.doc.path: entry.doc.path.read_text(encoding="utf-8") for entry in entries}
    staged: list[tuple[Path, Path]] = []
    try:
        for entry in entries:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=entry.doc.path.parent,
                prefix=f".{entry.doc.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                tmp_path = Path(handle.name)
                handle.write(entry.text)
                handle.flush()
                os.fsync(handle.fileno())
                staged.append((tmp_path, entry.doc.path))
        for tmp_path, target in staged:
            os.replace(tmp_path, target)
    except Exception:
        for tmp_path, _target in staged:
            tmp_path.unlink(missing_ok=True)
        for path, text in originals.items():
            _atomic_replace_text(path, text)
        raise


def strip_related_section(body: str) -> tuple[str, bool]:
    new_body, count = RELATED_SECTION_RE.subn("", body)
    if count == 0:
        return body, False
    new_body = new_body.rstrip() + ("\n" if body.endswith("\n") else "")
    return new_body, True


def load_target_doc(path_value: str, root: Path) -> Doc:
    target_path = _resolve_invocation_path(path_value, root)
    if not target_path.exists():
        raise PathNotFound(path_value)
    return load_doc(target_path, root)
