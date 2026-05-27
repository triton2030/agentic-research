from __future__ import annotations


def orient(
    corpus: str,
    *,
    top: int | None = None,
    max_heading_level: int | None = None,
    compact: bool = False,
    expanded: bool = False,
) -> dict[str, object]:
    from navigator.api import importance, ls, status

    effective_top = int(top or (10 if expanded else 3))
    effective_level = int(max_heading_level or (2 if expanded else 1))
    status_payload = status(corpus)
    files_payload = ls(
        corpus,
        max_heading_level=effective_level,
        with_link_counts=expanded,
    )
    importance_payload = importance(corpus, top=effective_top)

    if not expanded:
        slim_status = {
            key: status_payload.get(key)
            for key in ("state", "model", "pending_chunks", "drift_count", "recommended_action")
            if key in status_payload
        }
        slim_files = [
            {
                "relative_path": item.get("relative_path"),
                "description": item.get("description"),
                "title": item.get("title"),
                "heading_count": item.get("heading_count"),
                "read_next": [
                    {
                        "tool": "md_edit_context",
                        "args": {"path": item.get("path"), "scan": corpus},
                        "reason": "Inspect graph obligations and related context for this file.",
                    }
                ],
            }
            for item in files_payload.get("files", [])
        ]
        return {
            "workflow": "md_orient",
            "corpus": corpus,
            "expanded": False,
            "map_only": True,
            "content_included": False,
            "status": slim_status,
            "files": {"files": slim_files, "file_count": len(slim_files)},
            "importance": importance_payload,
            "read_next": [
                {
                    "tool": "md_orient",
                    "args": {"corpus": corpus, "expanded": True},
                    "reason": "Return headings and link counts for the full orientation packet.",
                }
            ],
            "next": "Choose 1-3 files, then use md edit-context or md extract for selected targets.",
        }

    return {
        "workflow": "md_orient",
        "corpus": corpus,
        "expanded": True,
        "map_only": False,
        "content_included": False,
        "status": status_payload,
        "files": files_payload,
        "importance": importance_payload,
        "next": "Use md edit-context for one file, or md audit for semantic IA drift.",
    }
