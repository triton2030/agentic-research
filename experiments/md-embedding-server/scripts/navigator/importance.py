from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx

from .link_graph import build_link_graph


def importance_rows(corpus: Path, top: int = 10, sort_by: str = "pagerank") -> list[dict[str, Any]]:
    graph = build_link_graph(corpus)
    if graph.number_of_nodes() == 0:
        return []

    simple = nx.DiGraph()
    for node, attrs in graph.nodes(data=True):
        simple.add_node(node, **attrs)
    for source, target in graph.edges():
        if simple.has_edge(source, target):
            simple[source][target]["weight"] += 1
        else:
            simple.add_edge(source, target, weight=1)

    try:
        pagerank = nx.pagerank(simple, weight="weight")
    except Exception:
        pagerank = {node: 1.0 / max(1, simple.number_of_nodes()) for node in simple.nodes}
    centrality = nx.degree_centrality(simple)

    rows: list[dict[str, Any]] = []
    for node, attrs in simple.nodes(data=True):
        rows.append(
            {
                "path": attrs.get("path", str(node)),
                "relative_path": attrs.get("relative_path", str(node)),
                "description": attrs.get("description", ""),
                "in_degree": int(simple.in_degree(node)),
                "out_degree": int(simple.out_degree(node)),
                "pagerank": float(pagerank.get(node, 0.0)),
                "centrality": float(centrality.get(node, 0.0)),
            }
        )

    if sort_by not in {"pagerank", "in_degree", "out_degree", "centrality"}:
        sort_by = "pagerank"
    rows.sort(key=lambda row: (-row[sort_by], row["relative_path"]))
    return rows[:top]


def render_importance(rows: list[dict[str, Any]], sort_by: str) -> str:
    lines = [f"# Markdown importance — sort: {sort_by}", ""]
    if not rows:
        lines.append("(no Markdown files found)")
        return "\n".join(lines).rstrip() + "\n"
    for index, row in enumerate(rows, start=1):
        desc = row.get("description") or "TODO description"
        lines.append(
            f"{index}. {row['relative_path']} | pagerank={row['pagerank']:.4f} "
            f"| centrality={row['centrality']:.4f} "
            f"| in={row['in_degree']} out={row['out_degree']} | {desc}"
        )
    return "\n".join(lines).rstrip() + "\n"
