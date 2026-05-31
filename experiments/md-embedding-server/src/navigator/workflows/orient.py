from __future__ import annotations

from typing import Any


def _why(row: dict[str, Any]) -> str:
    """One-line rationale for a start_here pick: link-hub strength + description."""
    desc = (row.get("description") or "").strip()
    in_degree = row.get("in_degree")
    bits: list[str] = []
    if isinstance(in_degree, int) and in_degree > 0:
        bits.append(f"hub: {in_degree} inbound")
    if desc:
        bits.append(desc if len(desc) <= 80 else desc[:77] + "…")
    return " — ".join(bits) if bits else "central by link graph"


def orient(
    corpus: str,
    *,
    top: int | None = None,
    max_heading_level: int | None = None,
    compact: bool = False,
    expanded: bool = False,
) -> dict[str, object]:
    from navigator.api import importance, ls, status
    from navigator.folder_map import fold_by_folder

    effective_top = int(top or (10 if expanded else 3))
    effective_level = int(max_heading_level or (2 if expanded else 1))
    status_payload = status(corpus)
    files_payload = ls(
        corpus,
        max_heading_level=effective_level,
        with_link_counts=expanded,
        expanded=True,
    )
    importance_payload = importance(corpus, top=effective_top)

    slim_status = {
        key: status_payload.get(key)
        for key in ("state", "model", "pending_chunks", "drift_count", "recommended_action")
        if key in status_payload
    }

    if not expanded:
        files = files_payload.get("files", [])
        start_here = [
            {
                "relative_path": row.get("relative_path"),
                "pagerank": round(float(row.get("pagerank", 0.0)), 4),
                "in_degree": row.get("in_degree"),
                "why": _why(row),
            }
            for row in importance_payload.get("files", [])[:3]
        ]
        shape = {
            "file_count": files_payload.get("file_count", len(files)),
            "description_gaps": files_payload.get("description_gap_count", 0),
            "folders": fold_by_folder(files),
        }
        return {
            "workflow": "md_orient",
            "corpus": corpus,
            "expanded": False,
            "status": slim_status,
            "start_here": start_here,
            "shape": shape,
            "read_next": [
                {
                    "tool": "md_orient",
                    "args": {"corpus": corpus, "expanded": True},
                    "reason": "Full flat file list with headings and link counts.",
                }
            ],
            "next": "Pick a start_here file → md edit-context or md search-read for that target.",
        }

    return {
        "workflow": "md_orient",
        "corpus": corpus,
        "expanded": True,
        "status": status_payload,
        "files": files_payload,
        "importance": importance_payload,
        "next": "Use md edit-context for one file, or md audit for semantic IA drift.",
    }
