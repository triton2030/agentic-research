"""Link parsing, target resolution, edge resolution and scan_doc primitives.

Sits between graph_core (I/O + classes) and graph_reports (analysis). Anything
that turns a raw wikilink/markdown-link string into a resolved Edge belongs
here.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .markdown_io import (
    collect_headings,
    markdown_links_from_text,
    markdown_lookup,
    resolve_markdown_target,
    split_link_target,
    wikilinks_with_anchors_from_text,
)

from .graph_core import (
    ALLOWED_FIELDS,
    Doc,
    Edge,
    Finding,
    GRAPH_FIELDS,
    LEGACY_FIELDS,
    REQUIRED_FIELDS,
    load_doc,
    safe_rel,
)


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
    inner = value.strip()
    return inner.startswith("[[") and inner.endswith("]]")


def parse_wikilink(raw: str) -> tuple[str, str | None]:
    inner = raw.strip()
    if inner.startswith("[[") and inner.endswith("]]"):
        inner = inner[2:-2]
    target = inner.split("|", 1)[0].strip().strip("<>").strip()
    if "#" in target:
        path_part, anchor = target.split("#", 1)
        return split_link_target(path_part), anchor.split("?", 1)[0].strip() or None
    return split_link_target(target), None


def wikilinks_from_text(text: str) -> list[str]:
    return [
        f"{target}#{anchor}" if anchor else target
        for target, anchor in wikilinks_with_anchors_from_text(text)
        if target or anchor
    ]


def normalize_anchor(text: str) -> str:
    text = re.sub(r"\s+", "-", text.strip().lower())
    text = re.sub(r"[^\w\-а-яё]", "", text, flags=re.IGNORECASE)
    return text


def headings(body: str) -> set[str]:
    return {
        normalize_anchor(heading["text"])
        for heading in collect_headings(body.splitlines(), max_level=6)
    }


@lru_cache(maxsize=64)
def _markdown_lookup_for_root(root: str) -> dict[str, list[Path]]:
    return markdown_lookup(Path(root))


def resolve_target(target: str, source: Path, root: Path) -> Path | None:
    return resolve_markdown_target(target, source, root, _markdown_lookup_for_root(str(root.resolve())))


def target_candidates(target: str, source: Path, root: Path) -> list[Path]:
    resolved = resolve_target(target, source, root)
    return [resolved] if resolved is not None else []


def markdown_links(body: str) -> list[str]:
    return markdown_links_from_text(body)


def resolve_markdown_link(target: str, source: Path, root: Path) -> Path | None:
    if target.strip().startswith("#"):
        return source
    return resolve_target(target, source, root)


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


def render_edge_data(item: dict[str, Any]) -> str:
    if item.get("status") == "missing":
        return f"- {item.get('raw', item.get('target'))} -> MISSING_TARGET"
    return f"- {item.get('raw', item.get('target'))} -> {item.get('path')} | {item.get('description')}"


def render_audit_link(raw_link: str, source_doc: Doc, index: dict[Path, Doc], root: Path) -> str:
    edge = resolve_graph_edge(raw_link, source_doc, index, root)
    return render_edge(edge)


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


def format_anchors(anchors: list[str | None]) -> str:
    if not anchors:
        return ""
    has_plain = any(a is None for a in anchors)
    named = [a for a in anchors if a is not None]
    parts = [f"#{a}" for a in named]
    if has_plain:
        parts.append("(file-level)")
    return " via " + ", ".join(parts) if parts else ""
