from __future__ import annotations


def _graph_blockers(preflight_payload: dict[str, object]) -> dict[str, object]:
    blocker_codes = {
        "MISSING_TARGET",
        "BROKEN_WIKILINK",
        "BROKEN_MARKDOWN_LINK",
        "MISSING_FRONTMATTER",
        "GRAPH_FIELD_NOT_LIST",
        "GRAPH_LINK_NOT_WIKILINK",
    }
    check_only_raw = preflight_payload.get("check_only")
    check_only = check_only_raw if isinstance(check_only_raw, list) else []
    issue_codes = {item.get("code") for item in check_only if isinstance(item, dict)}
    return {
        "has_blockers": bool(
            preflight_payload.get("has_blockers")
            or preflight_payload.get("cycles")
            or (issue_codes & blocker_codes)
        ),
        "check_only": check_only,
        "cycles": preflight_payload.get("cycles") or [],
        "anchor_drift_risk": preflight_payload.get("anchor_drift_risk") or {},
        "must_update": preflight_payload.get("must_update") or [],
        "update_cascade": preflight_payload.get("update_cascade") or [],
        "dependent_cascade": preflight_payload.get("dependent_cascade") or [],
    }


def edit_context(
    path: str,
    *,
    mode: str | None = None,
    expanded: bool = False,
    scan: str | None = None,
    depth: int | None = None,
    query: str | None = None,
    corpus: str | None = None,
) -> dict[str, object]:
    from navigator.api import preflight, read_related, search

    selected_mode = "strict" if mode == "strict" else ("full" if expanded or mode == "full" else "preview")
    preflight_payload = preflight(path, scan=scan, depth=depth)
    preflight_exit = int(preflight_payload.get("_exit_code", 0) or 0)
    if preflight_exit >= 2:
        return {
            "workflow": "md_edit_context",
            "mode": selected_mode,
            "path": path,
            "error": "preflight_failed",
            "preflight": preflight_payload,
            "_exit_code": preflight_exit,
        }
    if selected_mode == "strict":
        return {
            "workflow": "md_edit_context",
            "mode": "strict",
            "path": path,
            "blockers": _graph_blockers(preflight_payload),
        }

    related = read_related(
        paths=[path],
        scan=scan or ".",
        mode=selected_mode,
        expanded=selected_mode == "full",
        anchor_aware=True,
        token_budget=1200 if selected_mode == "preview" else 6000,
    )
    search_payload = None
    if selected_mode == "full" and query:
        search_payload = search(corpus or scan or ".", query, limit=8)
    return {
        "workflow": "md_edit_context",
        "mode": selected_mode,
        "expanded": selected_mode == "full",
        "map_only": selected_mode != "full",
        "content_included": selected_mode == "full",
        "path": path,
        "preflight": preflight_payload,
        "related": related,
        "search": search_payload,
        "usage_note": "Graph rows are obligations; related/search rows are context candidates.",
    }
