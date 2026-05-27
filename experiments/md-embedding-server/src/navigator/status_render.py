"""Human rendering for status payloads."""

from __future__ import annotations

from typing import Any

from navigator.index_guidance import index_dry_run_command


def render_status(payload: dict[str, Any]) -> str:
    if payload.get("error"):
        return str(payload["error"])

    lines = [
        f"Corpus: {payload['corpus']}",
        f"Index:  {payload['index_path']}",
    ]
    scope = payload.get("path_scope") or {}
    include = scope.get("include")
    exclude = scope.get("exclude")
    dry_run_cmd = _recommended_index_dry_run(payload)
    if include or exclude:
        lines.append(f"Path scope: include={include or '∅'} exclude={exclude or '∅'}")
    if payload.get("last_touched"):
        lines.append(f"Last touched: {payload['last_touched']}")

    for scope_payload in payload.get("scopes", []):
        lines.append(
            f"[{scope_payload['scope']}] "
            f"added={scope_payload['added_sections']} "
            f"removed={scope_payload['removed_sections']} "
            f"reused={scope_payload['reused']} "
            f"pending_chunks={scope_payload['pending_chunks']} "
            f"total={scope_payload['total_sections_in_scope']}"
            f"{' metadata=MISMATCH' if scope_payload.get('metadata_mismatch') else ''}"
        )
        for item in scope_payload.get("pending_files", []):
            lines.append(
                f"  pending: {item['relative_path']} "
                f"(sections={item['added_sections']}, chunks={item['pending_chunks']})"
            )
        for item in scope_payload.get("removed_files", []):
            lines.append(
                f"  stale: {item['relative_path']} "
                f"(sections={item['removed_sections']})"
            )

    state = payload.get("state")
    if state == "NO_INDEX":
        lines.append(
            f"Status: NO INDEX — {payload['added_sections']} sections / "
            f"{payload['pending_chunks']} chunks would be embedded."
        )
        lines.append(f"  Next: {dry_run_cmd}")
    elif state == "NEEDS_REBUILD":
        lines.append(
            "Status: NEEDS REBUILD — index metadata/schema does not match the "
            "current model, API URL, or schema version."
        )
        lines.append(f"  Next: {dry_run_cmd}")
    elif state == "FRESH":
        lines.append("Status: FRESH — no pending changes; `search` is instant.")
    elif state == "NEEDS_WARMUP":
        lines.append(
            f"Status: NEEDS WARMUP — {payload['added_sections']} new sections / "
            f"{payload['pending_chunks']} chunks pending (cap {payload['max_auto_embed']})."
        )
        lines.append(f"  Next: {dry_run_cmd}")
    elif state == "HEALTHY":
        lines.append(
            f"Status: HEALTHY — {payload['added_sections']} new / "
            f"{payload['removed_sections']} removed sections, "
            f"{payload['pending_chunks']} chunks pending. `search` will auto-handle the delta."
        )
        lines.append(
            f"  Optional: {dry_run_cmd}  "
            "(preview cost before eager warmup)"
        )
    else:
        lines.append(f"Status: {state}")

    drift_count = int(payload.get("drift_count") or 0)
    if drift_count:
        lines.append(
            f"  ID drift: {drift_count} files have shifted positional ids since indexed. "
            "`search` auto-remaps to fresh ids; `index` prunes the stale rows."
        )
    return "\n".join(lines)


def _recommended_index_dry_run(payload: dict[str, Any]) -> str:
    action = payload.get("recommended_action")
    if isinstance(action, dict) and action.get("tool") == "md_index":
        args = action.get("args")
        if isinstance(args, dict):
            corpus = args.get("corpus")
            path_include = args.get("path_include")
            path_exclude = args.get("path_exclude")
            return index_dry_run_command(
                corpus if isinstance(corpus, str) else payload["corpus"],
                path_include=path_include if isinstance(path_include, list) else None,
                path_exclude=path_exclude if isinstance(path_exclude, list) else None,
            )
    scope = payload.get("path_scope") or {}
    path_include = scope.get("include")
    path_exclude = scope.get("exclude")
    return index_dry_run_command(
        payload["corpus"],
        path_include=path_include if isinstance(path_include, list) else None,
        path_exclude=path_exclude if isinstance(path_exclude, list) else None,
    )
