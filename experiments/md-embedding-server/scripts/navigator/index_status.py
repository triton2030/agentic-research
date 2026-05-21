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
    p.set_defaults(func=lambda args: cmd_status(args))


def find_corpus_root_for(anchor: Path) -> Path | None:
    """Walk upward from `anchor` looking for `.md-navigator/index.sqlite`.
    Returns the corpus root that owns the index, or None."""
    for parent in [anchor.parent, *anchor.parent.parents]:
        if (parent / ".md-navigator" / "index.sqlite").exists():
            return parent
    return None


def cmd_status(args) -> int:
    """Print the freshness of the on-disk index for a corpus without
    touching it. Counts pending added / removed sections vs the current
    Markdown tree, classifies overall state, and recommends a next action.

    Cheap operation — runs `ensure_index(..., dry_run=True)` which skips
    the embedding probe, the prune, and the embed loop. No HTTP calls.
    No DB writes. Use it before `search` on a corpus you have been
    editing, to know whether `index` is needed first."""
    from .folder_map import build_map
    from .sections import build_items_from_map

    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    cache_root = (
        Path(args.cache_dir).expanduser() if getattr(args, "cache_dir", None) else None
    )
    args.embed_model = resolve_embed_model_for_corpus(
        corpus_root, args.embed_model, cache_root=cache_root
    )
    index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = index_dir / "index.sqlite"

    print(f"Corpus: {corpus_root}")
    print(f"Index:  {db_path}")

    include_patterns = normalize_path_filter_patterns(
        getattr(args, "path_include", None),
        corpus_root,
    )
    exclude_patterns = normalize_path_filter_patterns(
        getattr(args, "path_exclude", None),
        corpus_root,
    )
    if include_patterns or exclude_patterns:
        print(f"Path scope: include={include_patterns or '∅'} exclude={exclude_patterns or '∅'}")

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=False)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1
    scoped_map_data = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    if not scoped_map_data["files"]:
        print(
            f"Path filters matched no Markdown files under {corpus_root}",
            file=sys.stderr,
        )
        return 1

    if not db_path.exists():
        total_added = 0
        total_chunks = 0
        for scope in ("sections", "descriptions"):
            items = build_items_from_map(scoped_map_data, scope=scope)
            if not items:
                continue
            pending = sum(len(_chunks_for_item(item)) for item in items)
            total_added += len(items)
            total_chunks += pending
            print(
                f"[{scope}] added={len(items)} removed=0 reused=0 "
                f"pending_chunks={pending} total=0"
            )
        print(
            f"Status: NO INDEX — {total_added} sections / {total_chunks} chunks "
            "would be embedded."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
        return 0

    import datetime

    mtime = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)
    print(f"Last touched: {mtime.isoformat(timespec='seconds')}")

    max_auto_embed = (
        None
        if getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED) == 0
        else int(getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED))
    )

    totals: dict[str, Any] = {
        "added_sections": 0,
        "removed_sections": 0,
        "reused": 0,
        "pending_chunks": 0,
        "in_scope": 0,
        "delta_too_large": False,
        "metadata_mismatch": False,
    }
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
            print(
                f"Missing Python dependency: {exc}.\n"
                f"  Run via the uv shebang or `uv run --script md_navigator.py status ...`",
                file=sys.stderr,
            )
            return 3
        print(
            f"[{scope}] added={stats['added_sections']} "
            f"removed={stats['removed_sections']} "
            f"reused={stats['reused']} "
            f"pending_chunks={stats['pending_chunks']} "
            f"total={stats['total_sections_in_scope']}"
            f"{' metadata=MISMATCH' if stats.get('metadata_mismatch') else ''}"
        )
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
        print(
            "Status: NEEDS REBUILD — index metadata/schema does not match the "
            "current model, API URL, or schema version."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
    elif added == 0 and removed == 0:
        print("Status: FRESH — no pending changes; `search` is instant.")
    elif totals["delta_too_large"]:
        print(
            f"Status: NEEDS WARMUP — {added} new sections / {pending} chunks "
            f"pending (cap {max_auto_embed})."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
    else:
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
