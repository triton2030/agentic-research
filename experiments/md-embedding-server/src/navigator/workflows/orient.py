from __future__ import annotations


def orient(
    corpus: str,
    *,
    top: int | None = None,
    max_heading_level: int | None = None,
    compact: bool = False,
) -> dict[str, object]:
    from navigator.api import importance, ls, status

    effective_top = 3 if compact else int(top or 10)
    effective_level = 1 if compact else int(max_heading_level or 2)
    status_payload = status(corpus)
    files_payload = ls(
        corpus,
        max_heading_level=effective_level,
        with_link_counts=not compact,
    )
    importance_payload = importance(corpus, top=effective_top)

    if compact:
        slim_status = {
            key: status_payload.get(key)
            for key in ("state", "model", "pending_chunks", "drift_count", "recommended_action")
            if key in status_payload
        }
        slim_files = [
            {
                "relative_path": item.get("relative_path"),
                "description": item.get("description"),
            }
            for item in files_payload.get("files", [])
        ]
        return {
            "workflow": "md_orient",
            "corpus": corpus,
            "compact": True,
            "status": slim_status,
            "files": {"files": slim_files, "file_count": len(slim_files)},
            "importance": importance_payload,
            "next": "Drop --compact for headings and link counts.",
        }

    return {
        "workflow": "md_orient",
        "corpus": corpus,
        "status": status_payload,
        "files": files_payload,
        "importance": importance_payload,
        "next": "Use md edit-context for one file, or md audit for semantic IA drift.",
    }
