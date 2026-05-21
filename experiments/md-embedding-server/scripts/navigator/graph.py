#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .markdown_io import MD_LINK_RE, WIKILINK_RE, collect_headings, parse_frontmatter

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


def safe_rel(path: Path, root: Path) -> Path:
    try:
        return path.resolve().relative_to(root)
    except ValueError:
        return path.resolve()


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
    has_frontmatter, lines, body = split_frontmatter(text)
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


def is_empty(value: object) -> bool:
    return value is None or value == "" or value == "TODO"


def graph_values(doc: Doc, field: str) -> list[str]:
    value = doc.frontmatter.get(field)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def is_wikilink(value: str) -> bool:
    return value.strip().startswith("[[") and value.strip().endswith("]]")


def parse_wikilink(raw: str) -> tuple[str, str | None]:
    inner = raw.strip()
    if inner.startswith("[[") and inner.endswith("]]"):
        inner = inner[2:-2]
    target = inner.split("|", 1)[0].strip()
    if "#" in target:
        path_part, anchor = target.split("#", 1)
        return path_part.strip(), anchor.strip()
    return target, None


def wikilinks_from_text(text: str) -> list[str]:
    return [match.group(1) for match in WIKILINK_RE.finditer(text) if match.group(1)]


def normalize_anchor(text: str) -> str:
    text = re.sub(r"\s+", "-", text.strip().lower())
    text = re.sub(r"[^\w\-а-яё]", "", text, flags=re.IGNORECASE)
    return text


def headings(body: str) -> set[str]:
    return {
        normalize_anchor(heading["text"])
        for heading in collect_headings(body.splitlines(), max_level=6)
    }


def target_candidates(target: str, source: Path, root: Path) -> list[Path]:
    target = target.strip()
    if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return []
    raw = Path(target)
    variants = [raw]
    if raw.suffix == "":
        variants.append(Path(str(raw) + ".md"))
    bases = [root]
    if not raw.is_absolute():
        bases.append(source.parent)
    candidates: list[Path] = []
    for base in bases:
        for variant in variants:
            path = variant if variant.is_absolute() else base / variant
            candidates.append(path.resolve())
    return candidates


def resolve_target(target: str, source: Path, root: Path) -> Path | None:
    for candidate in target_candidates(target, source, root):
        if candidate.exists():
            return candidate
    return None


def doc_index(docs: list[Doc], root: Path) -> dict[Path, Doc]:
    index: dict[Path, Doc] = {}
    for doc in docs:
        index[doc.path.resolve()] = doc
        index[(root / doc.rel).resolve()] = doc
    return index


def emit_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def finding_data(finding: Finding) -> dict[str, str]:
    return {
        "code": finding.code,
        "path": str(finding.path),
        "detail": finding.detail,
    }


def description_for(doc: Doc) -> str:
    if not doc.has_frontmatter:
        return "(no frontmatter)"
    value = doc.frontmatter.get("description")
    if is_empty(value):
        return "(no description)"
    return str(value)


def doc_data(doc: Doc) -> dict[str, Any]:
    return {
        "path": str(doc.rel),
        "description": description_for(doc),
        "has_frontmatter": doc.has_frontmatter,
    }


def resolve_graph_edge(raw_link: str, source_doc: Doc, index: dict[Path, Doc], root: Path) -> Edge:
    target_raw, anchor = parse_wikilink(raw_link)
    target_path = resolve_target(target_raw, source_doc.path, root)
    target_doc: Doc | None = None
    if target_path:
        target_doc = index.get(target_path.resolve())
        if target_doc is None:
            target_doc = load_doc(target_path, root)
            index[target_path.resolve()] = target_doc
    return Edge(
        source=source_doc,
        raw_link=raw_link,
        target=target_doc,
        target_raw=target_raw,
        anchor=anchor,
    )


def edge_data(edge: Edge) -> dict[str, Any]:
    data: dict[str, Any] = {
        "raw": edge.raw_link,
        "target": edge.target_raw,
        "anchor": edge.anchor,
        "path": None,
        "description": None,
        "status": "missing",
    }
    if edge.target is not None:
        data.update(
            {
                "path": str(edge.target.rel),
                "description": description_for(edge.target),
                "status": "ok",
            }
        )
    return data


def render_edge(edge: Edge) -> str:
    if edge.target is None:
        return f"- {edge.raw_link} -> MISSING_TARGET"
    return f"- {edge.raw_link} -> {edge.target.rel} | {description_for(edge.target)}"


def scan_doc(doc: Doc) -> list[Finding]:
    findings: list[Finding] = []
    if not doc.has_frontmatter:
        return [Finding("MISSING_FRONTMATTER", doc.rel, "add graph frontmatter with init")]
    for key in REQUIRED_FIELDS:
        if is_empty(doc.frontmatter.get(key)):
            findings.append(Finding(f"EMPTY_{key.upper().replace('-', '_')}", doc.rel, f"{key} is empty or TODO"))
    for key in GRAPH_FIELDS:
        value = doc.frontmatter.get(key)
        if value is None:
            findings.append(Finding("MISSING_GRAPH_FIELD", doc.rel, key))
        elif not isinstance(value, list):
            findings.append(Finding("GRAPH_FIELD_NOT_LIST", doc.rel, key))
        else:
            for item in value:
                if not is_wikilink(str(item)):
                    findings.append(Finding("GRAPH_LINK_NOT_WIKILINK", doc.rel, f"{key}: {item}"))
    for key in LEGACY_FIELDS:
        if key in doc.frontmatter:
            findings.append(Finding("LEGACY_FIELD", doc.rel, key))
    for key in doc.frontmatter:
        if key not in ALLOWED_FIELDS and key not in LEGACY_FIELDS:
            findings.append(Finding("UNKNOWN_FIELD", doc.rel, key))
    return findings


def cmd_scan(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    findings = [finding for doc in docs for finding in scan_doc(doc)]
    if args.json:
        emit_json(
            {
                "command": "scan",
                "targets": len(docs),
                "issues": [finding_data(finding) for finding in findings],
            }
        )
        return 1 if findings else 0
    print_summary("SCAN", len(docs), findings)
    return 1 if findings else 0


def cmd_init(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    json_output = getattr(args, "json", False)
    changed = 0
    modified: list[str] = []
    template = {
        "description": "TODO",
        "read-before-edit": [],
        "edit-after-edit": [],
    }
    for doc in docs:
        if doc.has_frontmatter:
            continue
        write_doc(doc, template, doc.body)
        changed += 1
        modified.append(str(doc.rel))
        if not json_output:
            print(f"INIT | {doc.rel}")
    if json_output:
        emit_json(
            {
                "command": "init",
                "targets": len(docs),
                "changed": changed,
                "unchanged": len(docs) - changed,
                "modified": modified,
            }
        )
        return 0
    print(f"SUMMARY | targets={len(docs)} changed={changed} unchanged={len(docs) - changed}")
    return 0


def strip_related_section(body: str) -> tuple[str, bool]:
    new_body, count = RELATED_SECTION_RE.subn("", body)
    if count == 0:
        return body, False
    new_body = new_body.rstrip() + ("\n" if body.endswith("\n") else "")
    return new_body, True


def cmd_strip(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    json_output = getattr(args, "json", False)
    changed = 0
    modified: list[str] = []
    changes: list[dict[str, Any]] = []
    for doc in docs:
        if not doc.has_frontmatter:
            if not args.also_related_section:
                continue
            new_body, section_removed = strip_related_section(doc.body)
            if not section_removed:
                continue
            doc.path.write_text(new_body, encoding="utf-8")
            changed += 1
            modified.append(str(doc.rel))
            changes.append(
                {
                    "path": str(doc.rel),
                    "removed_fields": [],
                    "related_section_removed": True,
                }
            )
            if not json_output:
                print(f"STRIP | {doc.rel} | (no frontmatter)+related-section")
            continue
        removed_fields = [key for key in doc.frontmatter if key not in ALLOWED_FIELDS]
        new_data = {
            key: value
            for key, value in doc.frontmatter.items()
            if key in ALLOWED_FIELDS
        }
        new_body = doc.body
        section_removed = False
        if args.also_related_section:
            new_body, section_removed = strip_related_section(doc.body)
        if new_data == doc.frontmatter and not section_removed:
            continue
        write_doc(doc, new_data, new_body)
        changed += 1
        modified.append(str(doc.rel))
        changes.append(
            {
                "path": str(doc.rel),
                "removed_fields": removed_fields,
                "related_section_removed": section_removed,
            }
        )
        marker = ",".join(removed_fields) or "(no legacy/unknown fields)"
        if section_removed:
            marker = f"{marker}+related-section"
        if not json_output:
            print(f"STRIP | {doc.rel} | {marker}")
    if json_output:
        emit_json(
            {
                "command": "strip",
                "targets": len(docs),
                "changed": changed,
                "unchanged": len(docs) - changed,
                "modified": modified,
                "changes": changes,
            }
        )
        return 0
    print(f"SUMMARY | targets={len(docs)} changed={changed} unchanged={len(docs) - changed}")
    return 0


def reverse_field_holders(target_doc: Doc, all_docs: list[Doc], root: Path, field: str) -> list[Doc]:
    target_path = target_doc.path.resolve()
    holders: list[Doc] = []
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        for raw_link in graph_values(doc, field):
            target_raw, _anchor = parse_wikilink(raw_link)
            resolved = resolve_target(target_raw, doc.path, root)
            if resolved and resolved.resolve() == target_path:
                holders.append(doc)
                break
    return holders


def reverse_edit_after_edit(target_doc: Doc, all_docs: list[Doc], root: Path) -> list[Doc]:
    return reverse_field_holders(target_doc, all_docs, root, "edit-after-edit")


def reverse_body_wikilink_holders(
    target_doc: Doc, all_docs: list[Doc], root: Path
) -> list[tuple[Doc, list[str | None]]]:
    target_path = target_doc.path.resolve()
    results: list[tuple[Doc, list[str | None]]] = []
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        anchors_used: list[str | None] = []
        for raw_link in wikilinks_from_text(doc.body):
            target_raw, anchor = parse_wikilink(raw_link)
            resolved = resolve_target(target_raw, doc.path, root)
            if resolved and resolved.resolve() == target_path:
                anchors_used.append(anchor)
        if anchors_used:
            results.append((doc, anchors_used))
    return results


def inbound_anchors_by_heading(
    target_doc: Doc, all_docs: list[Doc], root: Path
) -> dict[str, list[dict[str, Any]]]:
    target_path = target_doc.path.resolve()
    heading_lookup: dict[str, str] = {}
    for heading in collect_headings(target_doc.body.splitlines(), max_level=6):
        original = str(heading["text"]).strip()
        heading_lookup[normalize_anchor(original)] = original
    by_heading: dict[str, list[dict[str, Any]]] = {}
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        for raw_link in wikilinks_from_text(doc.body):
            target_raw, anchor = parse_wikilink(raw_link)
            if not anchor:
                continue
            resolved = resolve_target(target_raw, doc.path, root)
            if not resolved or resolved.resolve() != target_path:
                continue
            heading_text = heading_lookup.get(normalize_anchor(anchor))
            if heading_text is None:
                continue
            by_heading.setdefault(heading_text, []).append(
                {
                    "holder": str(safe_rel(doc.path, root)),
                    "description": description_for(doc),
                    "raw_anchor": anchor,
                }
            )
    return by_heading


def format_anchors(anchors: list[str | None]) -> str:
    if not anchors:
        return ""
    has_plain = any(a is None for a in anchors)
    named = [a for a in anchors if a is not None]
    parts = [f"#{a}" for a in named]
    if has_plain:
        parts.append("(file-level)")
    return " via " + ", ".join(parts) if parts else ""


def reverse_body_markdown_link_holders(target_doc: Doc, all_docs: list[Doc], root: Path) -> list[Doc]:
    target_path = target_doc.path.resolve()
    holders: list[Doc] = []
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        for target in markdown_links(doc.body):
            resolved = resolve_markdown_link(target, doc.path, root)
            if resolved and resolved.resolve() == target_path:
                holders.append(doc)
                break
    return holders


def render_audit_link(raw_link: str, source_doc: Doc, index: dict[Path, Doc], root: Path) -> str:
    edge = resolve_graph_edge(raw_link, source_doc, index, root)
    return render_edge(edge)


def edit_after_edit_cascade(doc: Doc, index: dict[Path, Doc], root: Path, max_depth: int) -> list[dict[str, Any]]:
    if max_depth < 1:
        return []
    cascade: list[dict[str, Any]] = []
    start = doc.path.resolve()
    queue: list[tuple[Doc, int, list[Path]]] = [(doc, 0, [start])]
    expanded: set[Path] = {start}
    while queue:
        current, depth, path_stack = queue.pop(0)
        if depth >= max_depth:
            continue
        next_depth = depth + 1
        for raw_link in graph_values(current, "edit-after-edit"):
            edge = resolve_graph_edge(raw_link, current, index, root)
            target_path = edge.target.path.resolve() if edge.target is not None else None
            is_cycle = target_path in path_stack if target_path else False
            item = edge_data(edge)
            item.update(
                {
                    "depth": next_depth,
                    "from": str(current.rel),
                    "cycle": is_cycle,
                }
            )
            cascade.append(item)
            if edge.target is None or target_path is None or is_cycle:
                continue
            if next_depth < max_depth and target_path not in expanded:
                expanded.add(target_path)
                queue.append((edge.target, next_depth, [*path_stack, target_path]))
    return cascade


def dependency_report(doc: Doc, all_docs: list[Doc], root: Path, depth: int) -> dict[str, Any]:
    index = doc_index(all_docs, root)
    index[doc.path.resolve()] = doc
    fields: dict[str, list[dict[str, Any]]] = {}
    for field in GRAPH_FIELDS:
        fields[field] = [
            edge_data(resolve_graph_edge(raw_link, doc, index, root))
            for raw_link in graph_values(doc, field)
        ]
    holders = reverse_edit_after_edit(doc, all_docs, root)
    return {
        "file": doc_data(doc),
        "fields": fields,
        "reverse_edit_after_edit": [doc_data(holder) for holder in holders],
        "edit_after_edit_cascade": edit_after_edit_cascade(doc, index, root, depth),
    }


def cmd_deps(args: argparse.Namespace) -> int:
    if args.depth < 1:
        raise SystemExit("--depth must be >= 1")
    root = repo_root()
    target_path = (root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    if not target_path.exists():
        raise SystemExit(f"Path not found: {args.path}")
    doc = load_doc(target_path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    report = dependency_report(doc, all_docs, root, args.depth)
    if args.json:
        emit_json({"command": "deps", "depth": args.depth, **report})
        return 0
    print(f"FILE | {doc.rel} | {description_for(doc)}")
    for field in GRAPH_FIELDS:
        values = report["fields"][field]
        print(f"\n{field} ({len(values)})")
        if not values:
            print("OK")
            continue
        for value in values:
            if value["status"] == "missing":
                print(f"- {value['raw']} -> MISSING_TARGET")
            else:
                print(f"- {value['raw']} -> {value['path']} | {value['description']}")
    holders = report["reverse_edit_after_edit"]
    print(f"\nreverse edit-after-edit ({len(holders)})")
    if not holders:
        print("OK")
    for holder in holders:
        print(f"- {holder['path']} | {holder['description']}")
    if args.depth > 1:
        cascade = report["edit_after_edit_cascade"]
        print(f"\nedit-after-edit cascade depth<={args.depth} ({len(cascade)})")
        if not cascade:
            print("OK")
        for item in cascade:
            marker = " | CYCLE" if item["cycle"] else ""
            if item["status"] == "missing":
                print(f"- depth {item['depth']}: {item['from']} -> MISSING_TARGET {item['raw']}{marker}")
            else:
                print(f"- depth {item['depth']}: {item['from']} -> {item['path']} | {item['description']}{marker}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    root = repo_root()
    target_path = (root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    if not target_path.exists():
        raise SystemExit(f"Path not found: {args.path}")
    doc = load_doc(target_path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    index = doc_index(all_docs, root)
    index[doc.path.resolve()] = doc
    if args.json:
        emit_json({"command": "audit", **dependency_report(doc, all_docs, root, 1)})
        return 0

    print(f"FILE | {doc.rel} | {description_for(doc)}")
    for field in GRAPH_FIELDS:
        values = graph_values(doc, field)
        print(f"\n{field} ({len(values)})")
        if not values:
            print("OK")
            continue
        for value in values:
            print(render_audit_link(value, doc, index, root))

    holders = reverse_edit_after_edit(doc, all_docs, root)
    print(f"\nreverse edit-after-edit ({len(holders)})")
    if not holders:
        print("OK")
        return 0
    for holder in holders:
        print(f"- {holder.rel} | {description_for(holder)}")
    return 0


def impact_report(doc: Doc, all_docs: list[Doc], root: Path, scan: str | None = None) -> dict[str, Any]:
    return {
        "file": doc_data(doc),
        "related_reading_command": navigator_read_related_command(str(doc.rel), scan=scan),
        "cascade_breaks": [
            doc_data(holder)
            for holder in reverse_field_holders(doc, all_docs, root, "edit-after-edit")
        ],
        "reference_breaks": [
            doc_data(holder)
            for holder in reverse_field_holders(doc, all_docs, root, "read-before-edit")
        ],
        "body_wikilink_refs": [
            {**doc_data(holder), "anchors": anchors}
            for holder, anchors in reverse_body_wikilink_holders(doc, all_docs, root)
        ],
        "body_markdown_refs": [
            doc_data(holder)
            for holder in reverse_body_markdown_link_holders(doc, all_docs, root)
        ],
    }


def cmd_impact(args: argparse.Namespace) -> int:
    root = repo_root()
    doc = load_target_doc(args.path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    report = impact_report(doc, all_docs, root, args.scan)
    if args.json:
        emit_json({"command": "impact", **report})
        return 0

    print(f"IMPACT | {report['file']['path']} | {report['file']['description']}")
    sections = (
        ("cascade breaks (reverse edit-after-edit)", report["cascade_breaks"]),
        ("reference breaks (reverse read-before-edit)", report["reference_breaks"]),
        ("body wikilink references", report["body_wikilink_refs"]),
        ("body markdown link references", report["body_markdown_refs"]),
    )
    for label, rows in sections:
        print(f"\n{label} ({len(rows)})")
        if not rows:
            print("OK")
            continue
        for row in rows:
            anchor_suffix = format_anchors(row.get("anchors", [])) if "anchors" in row else ""
            print(f"- {row['path']}{anchor_suffix} | {row['description']}")
    print("\nrelated reading")
    print(report["related_reading_command"])
    return 0


def check_graph(docs: list[Doc], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    index = doc_index(docs, root)
    for doc in docs:
        if not doc.has_frontmatter:
            continue
        for field in GRAPH_FIELDS:
            for raw_link in graph_values(doc, field):
                target_raw, anchor = parse_wikilink(raw_link)
                target_path = resolve_target(target_raw, doc.path, root)
                if not target_path:
                    findings.append(Finding("MISSING_TARGET", doc.rel, f"{field}: {raw_link}"))
                    continue
                target_doc = index.get(target_path.resolve())
                if target_doc is None:
                    target_doc = load_doc(target_path, root)
                    index[target_path.resolve()] = target_doc
                if anchor and normalize_anchor(anchor) not in headings(target_doc.body):
                    findings.append(Finding("MISSING_ANCHOR", doc.rel, f"{raw_link}"))
        for raw_link in wikilinks_from_text(doc.body):
            target_raw, anchor = parse_wikilink(raw_link)
            target_path = resolve_target(target_raw, doc.path, root)
            if not target_path:
                findings.append(Finding("BROKEN_WIKILINK", doc.rel, raw_link))
                continue
            if anchor:
                target_doc = index.get(target_path.resolve()) or load_doc(target_path, root)
                if normalize_anchor(anchor) not in headings(target_doc.body):
                    findings.append(Finding("MISSING_ANCHOR", doc.rel, raw_link))
        for markdown_target in markdown_links(doc.body):
            target_path = resolve_markdown_link(markdown_target, doc.path, root)
            if target_path is None:
                findings.append(Finding("BROKEN_MARKDOWN_LINK", doc.rel, markdown_target))
        if RELATED_SECTION_RE.search(doc.body):
            findings.append(Finding("RELATED_SECTION_PRESENT", doc.rel, "remove with strip --also-related-section"))
    return findings


def markdown_links(body: str) -> list[str]:
    results: list[str] = []
    for match in MD_LINK_RE.finditer(body):
        target = match.group(1).strip()
        if not target or target.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        results.append(target)
    return results


def resolve_markdown_link(target: str, source: Path, root: Path) -> Path | None:
    path_part = target.split("#", 1)[0].strip()
    if not path_part:
        return source
    candidates = target_candidates(path_part, source, root)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def cmd_check(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    findings = check_graph(docs, root)
    if args.json:
        emit_json(
            {
                "command": "check",
                "targets": len(docs),
                "issues": [finding_data(finding) for finding in findings],
            }
        )
        return 1 if findings else 0
    print_summary("CHECK", len(docs), findings)
    return 1 if findings else 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    command_name = getattr(args, "command", "doctor")
    findings = [finding for doc in docs for finding in scan_doc(doc)]
    findings.extend(check_graph(docs, root))
    groups = {
        "critical": {"MISSING_TARGET", "BROKEN_WIKILINK", "BROKEN_MARKDOWN_LINK", "MISSING_FRONTMATTER"},
        "cleanup": {
            "LEGACY_FIELD",
            "UNKNOWN_FIELD",
            "GRAPH_FIELD_NOT_LIST",
            "GRAPH_LINK_NOT_WIKILINK",
            "RELATED_SECTION_PRESENT",
        },
        "optional": {"EMPTY_DESCRIPTION", "MISSING_GRAPH_FIELD", "MISSING_ANCHOR"},
    }
    grouped = {
        label: [finding for finding in findings if finding.code in codes]
        for label, codes in groups.items()
    }
    if args.json:
        emit_json(
            {
                "command": command_name,
                "targets": len(docs),
                "issues": [finding_data(finding) for finding in findings],
                "groups": {
                    label: [finding_data(finding) for finding in selected]
                    for label, selected in grouped.items()
                },
            }
        )
        return 1 if findings else 0
    print(f"{command_name.upper()} | targets={len(docs)} issues={len(findings)}")
    for label, selected in grouped.items():
        print(f"\n{label.upper()} ({len(selected)})")
        if not selected:
            print("OK")
            continue
        for finding in selected:
            print(finding.render())
    return 1 if findings else 0


def health_report(docs: list[Doc], root: Path) -> dict[str, Any]:
    total = len(docs)
    with_description = 0
    missing_description = 0
    description_todo = 0
    no_frontmatter = 0
    broken_graph_links = 0
    incoming: dict[Path, int] = {}
    outgoing: dict[Path, int] = {}

    for doc in docs:
        if not doc.has_frontmatter:
            no_frontmatter += 1
        description = doc.frontmatter.get("description") if doc.has_frontmatter else None
        if is_empty(description):
            missing_description += 1
            if str(description).strip() == "TODO":
                description_todo += 1
        else:
            with_description += 1

        for field in GRAPH_FIELDS:
            for raw_link in graph_values(doc, field):
                target_raw, _anchor = parse_wikilink(raw_link)
                target_path = resolve_target(target_raw, doc.path, root)
                if target_path is None:
                    broken_graph_links += 1
                    continue
                source_path = doc.path.resolve()
                resolved_target = target_path.resolve()
                outgoing[source_path] = outgoing.get(source_path, 0) + 1
                incoming[resolved_target] = incoming.get(resolved_target, 0) + 1

    orphans = [
        doc_data(doc)
        for doc in docs
        if incoming.get(doc.path.resolve(), 0) == 0 and outgoing.get(doc.path.resolve(), 0) == 0
    ]
    hubs: list[dict[str, Any]] = []
    for path, count in sorted(incoming.items(), key=lambda item: (-item[1], str(safe_rel(item[0], root))))[:10]:
        try:
            doc = load_doc(path, root)
            hubs.append({"incoming": count, **doc_data(doc)})
        except OSError:
            hubs.append(
                {
                    "incoming": count,
                    "path": str(safe_rel(path, root)),
                    "description": "(unreadable)",
                    "has_frontmatter": False,
                }
            )

    cycles = [[doc_data(item) for item in cycle] for cycle in find_edit_after_edit_cycles(docs, root)]
    percent = round(100 * with_description / total) if total else 0
    return {
        "targets": total,
        "description_coverage": {
            "with_description": with_description,
            "missing": missing_description,
            "todo": description_todo,
            "no_frontmatter": no_frontmatter,
            "percent": percent,
        },
        "broken_graph_links": broken_graph_links,
        "orphans": orphans,
        "hubs": hubs,
        "cycles": cycles,
    }


def cmd_health(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    report = health_report(docs, root)
    if args.json:
        emit_json({"command": "health", **report})
        return 0

    coverage = report["description_coverage"]
    print(f"HEALTH | targets={report['targets']}")
    print(
        "description coverage: "
        f"{coverage['with_description']}/{report['targets']} ({coverage['percent']}%)"
    )
    print(f"missing descriptions: {coverage['missing']}")
    print(f"description TODO: {coverage['todo']}")
    print(f"no frontmatter: {coverage['no_frontmatter']}")
    print(f"broken graph links: {report['broken_graph_links']}")
    print(f"cycles in edit-after-edit: {len(report['cycles'])}")

    print(f"\norphans (no in/out graph edges) ({len(report['orphans'])})")
    if not report["orphans"]:
        print("OK")
    for row in report["orphans"]:
        print(f"- {row['path']} | {row['description']}")

    print(f"\ntop hubs (incoming graph edges) ({len(report['hubs'])})")
    if not report["hubs"]:
        print("OK")
    for row in report["hubs"]:
        print(f"- {row['incoming']} <- {row['path']} | {row['description']}")

    return 0


def edit_after_edit_adjacency(docs: list[Doc], root: Path) -> dict[Path, list[Edge]]:
    index = doc_index(docs, root)
    scope = {doc.path.resolve() for doc in docs}
    adjacency: dict[Path, list[Edge]] = {}
    for doc in docs:
        edges: list[Edge] = []
        for raw_link in graph_values(doc, "edit-after-edit"):
            edge = resolve_graph_edge(raw_link, doc, index, root)
            if edge.target is not None and edge.target.path.resolve() in scope:
                edges.append(edge)
        adjacency[doc.path.resolve()] = edges
    return adjacency


def canonical_cycle(paths: list[Path], index: dict[Path, Doc]) -> tuple[str, ...]:
    labels = [str(index[path].rel) for path in paths]
    body = labels[:-1]
    if not body:
        return tuple(labels)
    rotations = [body[index:] + body[:index] for index in range(len(body))]
    best = min(rotations)
    return tuple([*best, best[0]])


def find_edit_after_edit_cycles(docs: list[Doc], root: Path) -> list[list[Doc]]:
    index = doc_index(docs, root)
    docs_by_rel = {str(doc.rel): doc for doc in docs}
    adjacency = edit_after_edit_adjacency(docs, root)
    found: dict[tuple[str, ...], list[Doc]] = {}

    def visit(node: Path, stack: list[Path], active: set[Path]) -> None:
        active.add(node)
        stack.append(node)
        for edge in adjacency.get(node, []):
            if edge.target is None:
                continue
            target_path = edge.target.path.resolve()
            if target_path in active:
                start = stack.index(target_path)
                cycle_paths = [*stack[start:], target_path]
                key = canonical_cycle(cycle_paths, index)
                found[key] = [docs_by_rel[label] for label in key]
            elif target_path not in stack:
                visit(target_path, stack, active)
        stack.pop()
        active.remove(node)

    for doc in docs:
        visit(doc.path.resolve(), [], set())
    return [found[key] for key in sorted(found)]


def cmd_cycles(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    cycles = find_edit_after_edit_cycles(docs, root)
    if args.json:
        emit_json(
            {
                "command": "cycles",
                "targets": len(docs),
                "cycles": [
                    [doc_data(doc) for doc in cycle]
                    for cycle in cycles
                ],
            }
        )
        return 1 if cycles else 0
    print(f"CYCLES | targets={len(docs)} cycles={len(cycles)}")
    if not cycles:
        print("OK")
        return 0
    for cycle in cycles:
        print("- " + " -> ".join(str(doc.rel) for doc in cycle))
    return 1


PREFLIGHT_BLOCKERS = {
    "MISSING_TARGET",
    "BROKEN_WIKILINK",
    "BROKEN_MARKDOWN_LINK",
    "MISSING_FRONTMATTER",
    "GRAPH_FIELD_NOT_LIST",
    "GRAPH_LINK_NOT_WIKILINK",
}


def cycles_for_doc(doc: Doc, docs: list[Doc], root: Path) -> list[list[Doc]]:
    target = doc.path.resolve()
    return [
        cycle
        for cycle in find_edit_after_edit_cycles(docs, root)
        if any(item.path.resolve() == target for item in cycle)
    ]


def preflight_deferred_notes(doc: Doc) -> list[str]:
    notes = [
        "Semantic completeness is not machine-proven; classify candidate edges in the owning skill.",
    ]
    if not doc.has_frontmatter:
        notes.append("No graph frontmatter: read/update obligations are unknown.")
    elif not graph_values(doc, "edit-after-edit"):
        notes.append("No edit-after-edit edges declared; treat this as a positive claim only after semantic audit.")
    return notes


def preflight_report(
    doc: Doc,
    all_docs: list[Doc],
    root: Path,
    depth: int,
    scan: str | None = None,
) -> dict[str, Any]:
    deps = dependency_report(doc, all_docs, root, depth)
    findings = [*scan_doc(doc), *check_graph([doc], root)]
    cycles = cycles_for_doc(doc, all_docs, root)
    check_only_references = {
        "reverse_edit_after_edit": deps["reverse_edit_after_edit"],
        "reverse_read_before_edit": [
            doc_data(holder)
            for holder in reverse_field_holders(doc, all_docs, root, "read-before-edit")
        ],
        "body_wikilinks": [
            {**doc_data(holder), "anchors": anchors}
            for holder, anchors in reverse_body_wikilink_holders(doc, all_docs, root)
        ],
        "body_markdown_links": [
            doc_data(holder)
            for holder in reverse_body_markdown_link_holders(doc, all_docs, root)
        ],
    }
    anchor_drift = inbound_anchors_by_heading(doc, all_docs, root)
    return {
        "file": doc_data(doc),
        "related_reading_command": navigator_read_related_command(str(doc.rel), scan=scan),
        "must_read": deps["fields"]["read-before-edit"],
        "must_update": deps["fields"]["edit-after-edit"],
        "update_cascade": deps["edit_after_edit_cascade"],
        "reverse_holders": deps["reverse_edit_after_edit"],
        "check_only_references": check_only_references,
        "check_only": [finding_data(finding) for finding in findings],
        "cycles": [[doc_data(item) for item in cycle] for cycle in cycles],
        "anchor_drift_risk": anchor_drift,
        "deferred": preflight_deferred_notes(doc),
    }


def report_has_blockers(report: dict[str, Any]) -> bool:
    issue_codes = {item["code"] for item in report.get("check_only", [])}
    return bool(issue_codes & PREFLIGHT_BLOCKERS) or bool(report.get("cycles"))


def render_edge_data(item: dict[str, Any]) -> str:
    if item.get("status") == "missing":
        return f"- {item.get('raw', item.get('target'))} -> MISSING_TARGET"
    return f"- {item.get('raw', item.get('target'))} -> {item.get('path')} | {item.get('description')}"


def navigator_read_related_command(path: str, token_budget: int = 3000, scan: str | None = None) -> str:
    scan_arg = f" --scan {shlex.quote(scan)}" if scan else ""
    return (
        f"uv run --script {shlex.quote(NAVIGATOR_SCRIPT)} read-related {shlex.quote(path)}"
        f"{scan_arg} --token-budget {token_budget}"
    )


def render_preflight_report(report: dict[str, Any], title: str = "PREFLIGHT") -> str:
    lines = [f"{title} | {report['file']['path']} | {report['file']['description']}"]

    lines.append(f"\nmust-read ({len(report['must_read'])})")
    lines.extend(render_edge_data(item) for item in report["must_read"])
    if not report["must_read"]:
        lines.append("OK")

    lines.append(f"\nmust-update ({len(report['must_update'])})")
    lines.extend(render_edge_data(item) for item in report["must_update"])
    if not report["must_update"]:
        lines.append("OK")

    cascade = report["update_cascade"]
    lines.append(f"\nupdate-cascade ({len(cascade)})")
    if not cascade:
        lines.append("OK")
    for item in cascade:
        marker = " | CYCLE" if item.get("cycle") else ""
        if item.get("status") == "missing":
            lines.append(f"- depth {item['depth']}: {item['from']} -> MISSING_TARGET {item['raw']}{marker}")
        else:
            lines.append(f"- depth {item['depth']}: {item['from']} -> {item['path']} | {item['description']}{marker}")

    holders = report["reverse_holders"]
    lines.append(f"\ncheck-only reverse edit-after-edit ({len(holders)})")
    if not holders:
        lines.append("OK")
    for holder in holders:
        lines.append(f"- {holder['path']} | {holder['description']}")

    references = report.get("check_only_references", {})
    reference_sections = (
        ("reverse read-before-edit", references.get("reverse_read_before_edit", [])),
        ("body wikilinks", references.get("body_wikilinks", [])),
        ("body markdown links", references.get("body_markdown_links", [])),
    )
    total_references = sum(len(rows) for _label, rows in reference_sections)
    lines.append(f"\ncheck-only references ({total_references})")
    if not total_references:
        lines.append("OK")
    for label, rows in reference_sections:
        for row in rows:
            anchor_suffix = format_anchors(row.get("anchors", [])) if "anchors" in row else ""
            lines.append(f"- {label}: {row['path']}{anchor_suffix} | {row['description']}")

    drift = report.get("anchor_drift_risk") or {}
    total_anchored = sum(len(holders) for holders in drift.values())
    lines.append(f"\nanchor-drift risk ({len(drift)} headings, {total_anchored} inbound)")
    if not drift:
        lines.append("OK")
    for heading, holders in drift.items():
        lines.append(f"- ## {heading} ({len(holders)} inbound, rename = silent break)")
        for holder in holders[:3]:
            lines.append(f"  - {holder['holder']} | {holder['description']}")
        if len(holders) > 3:
            lines.append(f"  - ... (+{len(holders) - 3} more)")

    checks = report["check_only"]
    lines.append(f"\ncheck-only issues ({len(checks)})")
    if not checks:
        lines.append("OK")
    for issue in checks:
        lines.append(f"- {issue['code']} | {issue['path']} | {issue['detail']}")

    cycles = report["cycles"]
    lines.append(f"\ncycles ({len(cycles)})")
    if not cycles:
        lines.append("OK")
    for cycle in cycles:
        lines.append("- " + " -> ".join(item["path"] for item in cycle))

    lines.append(f"\ndeferred ({len(report['deferred'])})")
    for note in report["deferred"]:
        lines.append(f"- {note}")

    lines.append("\nrelated reading")
    lines.append(report["related_reading_command"])

    return "\n".join(lines)


def load_target_doc(path_value: str, root: Path) -> Doc:
    target_path = (root / path_value).resolve() if not Path(path_value).is_absolute() else Path(path_value).resolve()
    if not target_path.exists():
        raise SystemExit(f"Path not found: {path_value}")
    return load_doc(target_path, root)


def cmd_preflight(args: argparse.Namespace) -> int:
    if args.depth < 1:
        raise SystemExit("--depth must be >= 1")
    root = repo_root()
    doc = load_target_doc(args.path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    report = preflight_report(doc, all_docs, root, args.depth, args.scan)
    if args.json:
        emit_json({"command": "preflight", "depth": args.depth, **report})
    else:
        print(render_preflight_report(report))
    return 1 if report_has_blockers(report) else 0


def changed_markdown_paths(root: Path, args: argparse.Namespace) -> list[Path]:
    if args.staged:
        command = ["git", "diff", "--cached", "--name-only", "--"]
    else:
        ref = args.since or args.base or "HEAD"
        command = ["git", "diff", "--name-only", ref, "--"]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "git diff failed")
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = (root / line.strip()).resolve()
        if path.suffix.lower() == ".md":
            paths.append(path)
    return paths


def cmd_changed(args: argparse.Namespace) -> int:
    if args.depth < 1:
        raise SystemExit("--depth must be >= 1")
    if args.base and args.since:
        raise SystemExit("Use either --base or --since, not both.")
    if args.staged and (args.base or args.since):
        raise SystemExit("Use --staged without --base or --since.")
    root = repo_root()
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    reports: list[dict[str, Any]] = []
    deleted: list[str] = []
    for path in changed_markdown_paths(root, args):
        if not path.exists():
            deleted.append(str(safe_rel(path, root)))
            continue
        reports.append(preflight_report(load_doc(path, root), all_docs, root, args.depth, args.scan))

    if args.json:
        emit_json(
            {
                "command": "changed",
                "since": "STAGED" if args.staged else (args.since or args.base or "HEAD"),
                "depth": args.depth,
                "reports": reports,
                "deleted": deleted,
            }
        )
    else:
        since = "STAGED" if args.staged else (args.since or args.base or "HEAD")
        print(f"CHANGED | since={since} markdown_files={len(reports)} deleted={len(deleted)}")
        for path in deleted:
            print(f"\nDELETED | {path} | downstream unknown; search references before finalizing")
        for report in reports:
            print()
            print(render_preflight_report(report, title="CHANGED-FILE"))
    return 1 if any(report_has_blockers(report) for report in reports) or deleted else 0


def print_summary(name: str, targets: int, findings: list[Finding]) -> None:
    print(f"{name} | targets={targets} issues={len(findings)}")
    if not findings:
        print("OK")
        return
    for finding in findings:
        print(finding.render())


def add_path_filter_args(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument(
        "--path-include",
        action="append",
        default=[],
        metavar="GLOB",
        help="Include paths matching GLOB (fnmatch, relative to root). Repeatable.",
    )
    cmd.add_argument(
        "--path-exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Exclude paths matching GLOB (fnmatch, relative to root). Repeatable.",
    )
    cmd.add_argument(
        "--no-default-excludes",
        action="store_true",
        help="Disable built-in hidden-directory skip (.git, .venv, .md-navigator, ...).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable Markdown frontmatter graph helper.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func, help_text in (
        ("scan", cmd_scan, "Find frontmatter schema issues."),
        ("init", cmd_init, "Add graph frontmatter template where missing."),
        ("check", cmd_check, "Validate graph links."),
        ("doctor", cmd_doctor, "Group graph findings by severity."),
        ("health", cmd_health, "Summarize graph description coverage, links, hubs, orphans, and cycles."),
        ("cycles", cmd_cycles, "Find edit-after-edit cycles."),
    ):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("paths", nargs="*", help="Markdown files or directories. Defaults to current directory.")
        cmd.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
        add_path_filter_args(cmd)
        cmd.set_defaults(func=func)

    strip = sub.add_parser("strip", help="Remove legacy graph fields and optionally related-docs sections.")
    strip.add_argument("paths", nargs="*", help="Markdown files or directories. Defaults to current directory.")
    strip.add_argument(
        "--also-related-section",
        action="store_true",
        help="Also remove '## Связанные документы' / '## Related documents' sections from body.",
    )
    strip.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(strip)
    strip.set_defaults(func=cmd_strip)

    deps = sub.add_parser(
        "deps",
        help="Show graph fields and reverse edit-after-edit holders for one Markdown file.",
    )
    deps.add_argument("path", help="Markdown file path.")
    deps.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan (default: repo root).",
    )
    deps.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Maximum edit-after-edit cascade depth to show (default: 1).",
    )
    deps.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(deps)
    deps.set_defaults(func=cmd_deps)

    audit = sub.add_parser(
        "audit",
        help="Show one Markdown file, its description, and graph links with linked descriptions.",
    )
    audit.add_argument("path", help="Markdown file path.")
    audit.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan and cached descriptions (default: repo root).",
    )
    audit.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(audit)
    audit.set_defaults(func=cmd_audit)

    impact = sub.add_parser(
        "impact",
        help="Show what breaks if a Markdown file is deleted or renamed.",
    )
    impact.add_argument("path", help="Markdown file path.")
    impact.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan (default: repo root).",
    )
    impact.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(impact)
    impact.set_defaults(func=cmd_impact)

    preflight = sub.add_parser(
        "preflight",
        help="One pre-edit safety report for a Markdown graph file.",
    )
    preflight.add_argument("path", help="Markdown file path.")
    preflight.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan and cycle checks (default: repo root).",
    )
    preflight.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum edit-after-edit cascade depth to show (default: 2).",
    )
    preflight.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(preflight)
    preflight.set_defaults(func=cmd_preflight)

    changed = sub.add_parser(
        "changed",
        help="Report Markdown graph downstream checks for files touched by git diff.",
    )
    changed.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan and cycle checks (default: repo root).",
    )
    changed.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum edit-after-edit cascade depth to show (default: 2).",
    )
    changed.add_argument(
        "--base",
        default=None,
        help="Compare against a git base ref. Prefer --since in new workflows.",
    )
    changed.add_argument(
        "--since",
        default=None,
        help="Git ref to diff against (default: HEAD, including staged and unstaged changes).",
    )
    changed.add_argument(
        "--staged",
        action="store_true",
        help="Use staged changes from git diff --cached.",
    )
    changed.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(changed)
    changed.set_defaults(func=cmd_changed)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
