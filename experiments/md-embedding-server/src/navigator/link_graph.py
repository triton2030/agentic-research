from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import networkx as nx

from .markdown_io import (
    GRAPH_LINK_KEYS,
    iter_markdown,
    markdown_links_with_anchors_from_text,
    markdown_lookup,
    normalize_frontmatter_links,
    parse_frontmatter,
    relative_path,
    resolve_markdown_target,
    wikilinks_with_anchors_from_text,
)


def _node_attrs(path: Path, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter = parse_frontmatter(text.splitlines())
    return {
        "path": str(path.resolve()),
        "relative_path": relative_path(path.resolve(), root),
        "description": frontmatter.get("description", ""),
    }


@dataclass(frozen=True)
class ExplicitLinkEdge:
    target: Path
    edge_type: str
    raw: str
    anchor: str | None


def iter_explicit_link_edges(
    path: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]] | None = None,
) -> Iterator[ExplicitLinkEdge]:
    source = path.resolve()
    root = scan_root.resolve()
    target_lookup = lookup if lookup is not None else markdown_lookup(root)
    text = source.read_text(encoding="utf-8", errors="replace")
    frontmatter = parse_frontmatter(text.splitlines())

    for key in GRAPH_LINK_KEYS:
        for target in normalize_frontmatter_links(frontmatter.get(key)):
            resolved = resolve_markdown_target(target, source, root, target_lookup)
            if resolved:
                yield ExplicitLinkEdge(resolved.resolve(), key, target, None)

    for target, anchor in wikilinks_with_anchors_from_text(text):
        resolved = resolve_markdown_target(target, source, root, target_lookup)
        if resolved:
            yield ExplicitLinkEdge(resolved.resolve(), "wikilink", target, anchor)

    for target, anchor in markdown_links_with_anchors_from_text(text):
        resolved = resolve_markdown_target(target, source, root, target_lookup)
        if resolved:
            yield ExplicitLinkEdge(resolved.resolve(), "markdown-link", target, anchor)


def build_link_graph(root: Path) -> nx.MultiDiGraph:
    """Build a Markdown file graph from frontmatter, wikilinks, and Markdown links."""
    scan_root = root.resolve()
    graph: nx.MultiDiGraph = nx.MultiDiGraph()
    files = iter_markdown(scan_root)
    lookup = markdown_lookup(scan_root)

    for path in files:
        resolved = path.resolve()
        graph.add_node(resolved, **_node_attrs(resolved, scan_root))

    for path in files:
        source = path.resolve()
        for edge in iter_explicit_link_edges(source, scan_root, lookup):
            graph.add_edge(source, edge.target, type=edge.edge_type, raw=edge.raw, anchor=edge.anchor)

    return graph


def link_counts(root: Path) -> dict[Path, dict[str, int]]:
    graph = build_link_graph(root)
    counts: dict[Path, dict[str, int]] = {}
    for node in graph.nodes:
        counts[Path(node).resolve()] = {
            "in_degree": len(graph.in_edges(node)),
            "out_degree": len(graph.out_edges(node)),
        }
    return counts
