from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


def section_blast_radius(
    path: str,
    corpus: str,
    query: str,
    *,
    heading_id: str | None = None,
    scan: str | None = None,
    depth: int | None = None,
    limit: int | None = None,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> dict[str, object]:
    if not query or not query.strip():
        return {"error": "query_required", "_exit_code": 2}

    from navigator.api import preflight, search

    with ThreadPoolExecutor(max_workers=2) as pool:
        graph_future = pool.submit(preflight, path, scan=scan, depth=depth)
        semantic_future = pool.submit(
            search,
            corpus,
            query,
            limit=limit or 8,
            path_include=path_include,
            path_exclude=path_exclude,
        )
        graph_payload = graph_future.result()
        semantic_payload = semantic_future.result()

    return {
        "workflow": "md_section_blast_radius",
        "path": path,
        "heading_id": heading_id,
        "query": query,
        "graph": graph_payload,
        "semantic": semantic_payload,
        "usage_note": "Graph is hard contract impact; semantic is a manual-review radius.",
    }
