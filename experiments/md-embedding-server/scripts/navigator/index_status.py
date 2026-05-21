"""Index status reporting (`status` command + corpus discovery).

Read-only. Uses `ensure_index(dry_run=True)` from `index_build` to compute
delta stats without writing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .cli_common import (
    add_cache_arg,
    add_embedding_args,
    add_max_heading_level_arg,
)
from .index_build import DEFAULT_MAX_AUTO_EMBED, _chunks_for_item, ensure_index
from .index_meta import (
    _index_dir_for_corpus,
    _open_index_readonly,
    resolve_embed_model_for_corpus,
)
from .filters import (
    add_path_filter_args,
    apply_path_filters_to_map,
    normalize_path_filter_patterns,
)


def register_status(sub) -> None:
    p = sub.add_parser(
        "status",
        help=(
            "Report freshness of the on-disk index for a corpus without "
            "touching it. Counts pending added / removed sections, classifies "
            "FRESH / HEALTHY / NEEDS WARMUP / NO INDEX. No HTTP calls, no DB writes."
        ),
    )
    p.add_argument("path", help="Folder or Markdown file to check.")
    add_max_heading_level_arg(p)
    add_embedding_args(p)
    add_cache_arg(p)
    add_path_filter_args(p, command_name="status")
    p.add_argument(
        "--max-auto-embed",
        type=int,
        default=DEFAULT_MAX_AUTO_EMBED,
        help=(
            f"Cap below which `search` / `overlaps` auto-embed inline. "
            f"Above this, status reports NEEDS WARMUP (default: {DEFAULT_MAX_AUTO_EMBED})."
        ),
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human text. Used by the MCP envelope.",
    )
    p.set_defaults(func=lambda args: cmd_status(args))


def _state_payload(state: str, corpus_root: Path) -> dict[str, Any]:
    """Map state code → {recommended_action} dict for JSON output.
    Action is structured: {tool, args, reason}. Skips when no follow-up needed."""
    if state == "FRESH":
        return {"recommended_action": None}
    if state == "HEALTHY":
        return {
            "recommended_action": {
                "tool": "md_index",
                "args": {"corpus": str(corpus_root), "confirm": True},
                "reason": "Optional eager warmup; search will auto-embed the small delta otherwise.",
            }
        }
    if state in ("NEEDS_WARMUP", "NEEDS_REBUILD", "NO_INDEX"):
        return {
            "recommended_action": {
                "tool": "md_index",
                "args": {"corpus": str(corpus_root), "confirm": True},
                "reason": {
                    "NEEDS_WARMUP": "Pending delta exceeds auto-embed cap; index before search.",
                    "NEEDS_REBUILD": "Index metadata/schema mismatch; rebuild required.",
                    "NO_INDEX": "Index does not exist; warm it before search.",
                }[state],
            }
        }
    return {"recommended_action": None}


def find_corpus_root_for(anchor: Path) -> Path | None:
    """Walk upward from `anchor` looking for `.md-navigator/index.sqlite`.
    Returns the corpus root that owns the index, or None."""
    for parent in [anchor.parent, *anchor.parent.parents]:
        if (parent / ".md-navigator" / "index.sqlite").exists():
            return parent
    return None


def cmd_status(args) -> int:
    """Report freshness of the on-disk index for a corpus without touching it.
    Counts pending added/removed sections vs the current Markdown tree,
    classifies overall state (FRESH / HEALTHY / NEEDS_WARMUP / NEEDS_REBUILD
    / NO_INDEX), and recommends a next action.

    Cheap operation — runs `ensure_index(..., dry_run=True)` which skips the
    embedding probe, the prune and the embed loop. No HTTP calls, no DB writes.
    Use before `search` on a corpus you have been editing.

    Supports `--json` for machine consumption (used by the MCP envelope to fill
    corpus_state on every reply)."""
    from .folder_map import build_map
    from .sections import build_items_from_map

    emit_json = bool(getattr(args, "json", False))

    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        msg = f"Path does not exist: {corpus_root}"
        if emit_json:
            import json
            print(json.dumps({"command": "status", "error": msg, "state": "ERROR"}, ensure_ascii=False, indent=2))
        else:
            print(msg, file=sys.stderr)
        return 2

    cache_root = (
        Path(args.cache_dir).expanduser() if getattr(args, "cache_dir", None) else None
    )
    args.embed_model = resolve_embed_model_for_corpus(
        corpus_root, args.embed_model, cache_root=cache_root
    )
    index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = index_dir / "index.sqlite"

    include_patterns = normalize_path_filter_patterns(
        getattr(args, "path_include", None),
        corpus_root,
    )
    exclude_patterns = normalize_path_filter_patterns(
        getattr(args, "path_exclude", None),
        corpus_root,
    )

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=False)
    if not map_data["files"]:
        msg = f"No Markdown files under {corpus_root}"
        if emit_json:
            import json
            print(json.dumps({"command": "status", "corpus": str(corpus_root), "error": msg, "state": "EMPTY"}, ensure_ascii=False, indent=2))
        else:
            print(msg, file=sys.stderr)
        return 1
    scoped_map_data = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    if not scoped_map_data["files"]:
        msg = f"Path filters matched no Markdown files under {corpus_root}"
        if emit_json:
            import json
            print(json.dumps({"command": "status", "corpus": str(corpus_root), "error": msg, "state": "EMPTY"}, ensure_ascii=False, indent=2))
        else:
            print(msg, file=sys.stderr)
        return 1

    max_auto_embed = (
        None
        if getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED) == 0
        else int(getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED))
    )

    # === NO INDEX branch ===
    if not db_path.exists():
        scopes_payload: list[dict[str, Any]] = []
        total_added = 0
        total_chunks = 0
        for scope in ("sections", "descriptions"):
            items = build_items_from_map(scoped_map_data, scope=scope)
            if not items:
                continue
            pending = sum(len(_chunks_for_item(item)) for item in items)
            total_added += len(items)
            total_chunks += pending
            scopes_payload.append({
                "scope": scope,
                "added_sections": len(items),
                "removed_sections": 0,
                "reused": 0,
                "pending_chunks": pending,
                "total_sections_in_scope": 0,
            })

        state = "NO_INDEX"
        if emit_json:
            import json
            payload = {
                "command": "status",
                "corpus": str(corpus_root),
                "index_path": str(db_path),
                "index_exists": False,
                "last_touched": None,
                "model": args.embed_model,
                "path_scope": {"include": include_patterns or None, "exclude": exclude_patterns or None},
                "scopes": scopes_payload,
                "added_sections": total_added,
                "removed_sections": 0,
                "pending_chunks": total_chunks,
                "drift_count": 0,
                "metadata_mismatch": False,
                "delta_too_large": False,
                "max_auto_embed": getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED),
                "state": state,
                **_state_payload(state, corpus_root),
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        print(f"Corpus: {corpus_root}")
        print(f"Index:  {db_path}")
        if include_patterns or exclude_patterns:
            print(f"Path scope: include={include_patterns or '∅'} exclude={exclude_patterns or '∅'}")
        for sp in scopes_payload:
            print(
                f"[{sp['scope']}] added={sp['added_sections']} removed=0 reused=0 "
                f"pending_chunks={sp['pending_chunks']} total=0"
            )
        print(f"Status: NO INDEX — {total_added} sections / {total_chunks} chunks would be embedded.")
        print(f"  Run: md_navigator.py index '{corpus_root}'")
        return 0

    # === Existing index branch ===
    import datetime
    mtime = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)

    totals: dict[str, Any] = {
        "added_sections": 0,
        "removed_sections": 0,
        "reused": 0,
        "pending_chunks": 0,
        "in_scope": 0,
        "delta_too_large": False,
        "metadata_mismatch": False,
    }
    scopes_payload = []
    for scope in ("sections", "descriptions"):
        items = build_items_from_map(scoped_map_data, scope=scope)
        if not items:
            continue
        try:
            _, stats = ensure_index(
                corpus_root,
                scope,
                items,
                args.embed_model,
                embedding_api_url=args.embedding_api_url,
                embedding_timeout=args.embedding_timeout,
                cache_root=cache_root,
                max_auto_embed=max_auto_embed,
                dry_run=True,
                path_include=include_patterns,
                path_exclude=exclude_patterns,
            )
        except ModuleNotFoundError as exc:
            msg = f"Missing Python dependency: {exc}"
            if emit_json:
                import json
                print(json.dumps({"command": "status", "corpus": str(corpus_root), "error": msg, "state": "DEPENDENCY_ERROR"}, ensure_ascii=False, indent=2))
            else:
                print(
                    f"{msg}.\n"
                    f"  Run via the uv shebang or `uv run --script md_navigator.py status ...`",
                    file=sys.stderr,
                )
            return 3
        scopes_payload.append({
            "scope": scope,
            "added_sections": stats["added_sections"],
            "removed_sections": stats["removed_sections"],
            "reused": stats["reused"],
            "pending_chunks": stats["pending_chunks"],
            "total_sections_in_scope": stats["total_sections_in_scope"],
            "metadata_mismatch": stats.get("metadata_mismatch", False),
            "delta_too_large": stats.get("delta_too_large", False),
        })
        totals["added_sections"] += stats["added_sections"]
        totals["removed_sections"] += stats["removed_sections"]
        totals["reused"] += stats["reused"]
        totals["pending_chunks"] += stats["pending_chunks"]
        totals["in_scope"] += stats["total_sections_in_scope"]
        if stats.get("delta_too_large"):
            totals["delta_too_large"] = True
        if stats.get("metadata_mismatch"):
            totals["metadata_mismatch"] = True

    pending = totals["pending_chunks"]
    removed = totals["removed_sections"]
    added = totals["added_sections"]

    # ID drift check: positional file_id stored at index time stays put while
    # corpus reorders shift the fresh-map positional id. Content-hash diff
    # doesn't see this — same body at same line keeps the same row. Without
    # the check, `status` says FRESH but a downstream `pick` resolving stale
    # ids against a fresh map pulls the wrong file. search.cmd_search now
    # remaps to fresh ids, so drift is benign there; this stays as visible
    # signal so other consumers and humans know to reindex for clean state.
    import sqlite3

    fresh_file_id_by_path = {f["relative_path"]: f["id"] for f in scoped_map_data["files"]}
    drift_count = 0
    try:
        conn_ro = _open_index_readonly(corpus_root, cache_root=cache_root)
        try:
            rows = conn_ro.execute(
                "SELECT DISTINCT relative_path, file_id FROM sections"
            ).fetchall()
        finally:
            conn_ro.close()
        for path, idx_fid in rows:
            fresh_fid = fresh_file_id_by_path.get(path)
            if fresh_fid is not None and int(fresh_fid) != int(idx_fid):
                drift_count += 1
    except (FileNotFoundError, sqlite3.OperationalError):
        pass

    if totals["metadata_mismatch"]:
        state = "NEEDS_REBUILD"
    elif added == 0 and removed == 0:
        state = "FRESH"
    elif totals["delta_too_large"]:
        state = "NEEDS_WARMUP"
    else:
        state = "HEALTHY"

    if emit_json:
        import json
        payload = {
            "command": "status",
            "corpus": str(corpus_root),
            "index_path": str(db_path),
            "index_exists": True,
            "last_touched": mtime.isoformat(timespec="seconds"),
            "model": args.embed_model,
            "path_scope": {"include": include_patterns or None, "exclude": exclude_patterns or None},
            "scopes": scopes_payload,
            "added_sections": added,
            "removed_sections": removed,
            "pending_chunks": pending,
            "drift_count": drift_count,
            "metadata_mismatch": totals["metadata_mismatch"],
            "delta_too_large": totals["delta_too_large"],
            "max_auto_embed": max_auto_embed,
            "state": state,
            **_state_payload(state, corpus_root),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"Corpus: {corpus_root}")
    print(f"Index:  {db_path}")
    if include_patterns or exclude_patterns:
        print(f"Path scope: include={include_patterns or '∅'} exclude={exclude_patterns or '∅'}")
    print(f"Last touched: {mtime.isoformat(timespec='seconds')}")
    for sp in scopes_payload:
        print(
            f"[{sp['scope']}] added={sp['added_sections']} "
            f"removed={sp['removed_sections']} "
            f"reused={sp['reused']} "
            f"pending_chunks={sp['pending_chunks']} "
            f"total={sp['total_sections_in_scope']}"
            f"{' metadata=MISMATCH' if sp.get('metadata_mismatch') else ''}"
        )

    if state == "NEEDS_REBUILD":
        print(
            "Status: NEEDS REBUILD — index metadata/schema does not match the "
            "current model, API URL, or schema version."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
    elif state == "FRESH":
        print("Status: FRESH — no pending changes; `search` is instant.")
    elif state == "NEEDS_WARMUP":
        print(
            f"Status: NEEDS WARMUP — {added} new sections / {pending} chunks "
            f"pending (cap {max_auto_embed})."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
    else:  # HEALTHY
        print(
            f"Status: HEALTHY — {added} new / {removed} removed sections, "
            f"{pending} chunks pending. `search` will auto-handle the delta."
        )
        print(
            f"  Optional: md_navigator.py index '{corpus_root}'  "
            f"(eagerly warm the index instead of paying inside search)"
        )
    if drift_count:
        print(
            f"  ID drift: {drift_count} files have shifted positional ids "
            f"since indexed. `search` auto-remaps to fresh ids; `index` "
            f"prunes the stale rows."
        )
    return 0
