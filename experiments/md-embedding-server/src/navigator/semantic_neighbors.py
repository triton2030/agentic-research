from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .api_utils import _exit, _read_next
from .index_meta import _open_index_readonly
from .index_readiness import IndexReadinessKind, classify_index_readiness


DEFAULT_LIMIT = 8
DEFAULT_EXPANDED_TOKEN_BUDGET = 3000


def semantic_neighbors(
    target: str,
    corpus: str,
    *,
    limit: int | None = None,
    expanded: bool = False,
    token_budget: int | None = None,
    cache_dir: str | None = None,
) -> dict[str, Any]:
    corpus_root = Path(corpus).expanduser().resolve()
    target_path = Path(target).expanduser().resolve()
    selected_limit = max(1, min(int(limit or DEFAULT_LIMIT), 50))
    cache_root = Path(cache_dir).expanduser() if cache_dir else None

    validation_error = _validate_target(target_path, corpus_root)
    if validation_error is not None:
        return validation_error
    readiness = classify_index_readiness(
        corpus_root,
        cache_root=cache_root,
        mode="vector",
        check_shadowed=True,
    )
    if readiness.kind is IndexReadinessKind.MISSING:
        return _index_warmup_required(corpus_root, target_path)
    if readiness.kind is IndexReadinessKind.SHADOWED_CONFLICT:
        return _index_conflict_payload(corpus_root, readiness.conflicts)
    if readiness.kind is not IndexReadinessKind.READY:
        return _index_rebuild_required(corpus_root, target_path, readiness.kind.value)

    try:
        conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    except FileNotFoundError:
        return _index_warmup_required(corpus_root, target_path)
    except (ModuleNotFoundError, RuntimeError, sqlite3.Error) as exc:
        return _index_rebuild_required(
            corpus_root,
            target_path,
            "open_failed",
            reason=f"Index became unreadable while opening it: {type(exc).__name__}",
        )

    try:
        target_chunks = _target_chunks(conn, corpus_root, target_path)
        if not target_chunks:
            return _index_warmup_required(
                corpus_root,
                target_path,
                reason="Target has no indexed sections in the explicit corpus index.",
            )
        candidates = _nearest_external_sections(
            conn,
            corpus_root=corpus_root,
            target_chunks=target_chunks,
            limit=selected_limit,
        )
    finally:
        conn.close()

    payload = _shape_payload(
        corpus_root=corpus_root,
        target_path=target_path,
        target_chunks=target_chunks,
        candidates=candidates,
        limit=selected_limit,
        expanded=expanded,
        token_budget=token_budget,
    )
    if not payload["candidates"]:
        return _exit({**payload, "empty": True}, 1)
    return payload


def _validate_target(target_path: Path, corpus_root: Path) -> dict[str, Any] | None:
    if not corpus_root.exists():
        return _exit({"error": "path_not_found", "corpus": str(corpus_root)}, 2)
    if not target_path.exists():
        return _exit({"error": "path_not_found", "target": str(target_path)}, 2)
    try:
        target_path.relative_to(corpus_root)
    except ValueError:
        return _exit(
            {
                "error": "target_outside_corpus",
                "target": str(target_path),
                "corpus": str(corpus_root),
            },
            2,
        )
    if target_path.is_file() and target_path.suffix.lower() not in {".md", ".mdx"}:
        return _exit(
            {
                "error": "not_markdown",
                "target": str(target_path),
                "reason": "semantic-neighbors target must be a Markdown file or a folder.",
            },
            2,
        )
    return None


def _index_warmup_required(
    corpus_root: Path,
    target_path: Path,
    *,
    reason: str = "Warm the explicit corpus index before semantic-neighbors.",
) -> dict[str, Any]:
    index_args = {"corpus": str(corpus_root), "dry_run": True}
    retry_args = {"target": str(target_path), "corpus": str(corpus_root)}
    return _exit(
        {
            "error": "index_warmup_required",
            "corpus": str(corpus_root),
            "target": str(target_path),
            "reason": reason,
            "suggested_index_args": index_args,
            "suggested_retry_args": retry_args,
            "read_next": [
                _read_next(
                    "md_index",
                    index_args,
                    "Warm the explicit corpus index, then retry semantic-neighbors.",
                )
            ],
        },
        4,
    )


def _index_rebuild_required(
    corpus_root: Path,
    target_path: Path,
    readiness: str,
    *,
    reason: str = "Index is not readable enough for semantic-neighbors.",
) -> dict[str, Any]:
    payload = _index_warmup_required(corpus_root, target_path, reason=reason)
    payload["error"] = "index_rebuild_required"
    payload["index_readiness"] = readiness
    return payload


def _index_conflict_payload(
    corpus_root: Path,
    conflicts: list[dict[str, Any]],
) -> dict[str, Any]:
    return _exit(
        {
            "error": "INDEX_CONFLICT",
            "corpus": str(corpus_root),
            "message": "Nested md-navigator indexes conflict with the explicit corpus index; semantic reads refuse to choose silently.",
            "conflicts": conflicts,
            "read_next": [
                _read_next(
                    "md_corpus_scan",
                    {"root": str(corpus_root)},
                    "Inspect indexed corpora and shadowed nested indexes.",
                ),
                _read_next(
                    "md_index",
                    {"corpus": str(corpus_root), "cleanup_shadowed": True, "dry_run": True},
                    "Preview cleanup of shadowed generated index files before retrying semantic reads.",
                ),
            ],
        },
        2,
    )


def _check_explicit_link_coherence(
    corpus_root: Path,
    anchor: Path,
    linked_targets: list[Path],
    threshold: float = 0.4,
    cache_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Dense-distance check for read-related --check-links.

    Returns only explicit links whose best anchor-section to target-section
    distance exceeds threshold. It is read-only and never embeds text.
    """
    try:
        conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError, sqlite3.Error):
        return []

    try:
        try:
            anchor_rel = str(anchor.resolve().relative_to(corpus_root.resolve()))
        except ValueError:
            return []

        anchor_chunks = conn.execute(
            "SELECT chunks.chunk_id, sections.section_id "
            "FROM chunks "
            "JOIN sections ON sections.rowid = chunks.section_rowid "
            "WHERE sections.scope = 'sections' AND sections.relative_path = ?",
            (anchor_rel,),
        ).fetchall()
        if not anchor_chunks:
            return []

        suspicious: list[dict[str, Any]] = []
        for target in linked_targets:
            try:
                target_rel = str(target.resolve().relative_to(corpus_root.resolve()))
            except ValueError:
                continue

            target_chunks = conn.execute(
                "SELECT chunks.chunk_id, sections.section_id "
                "FROM chunks "
                "JOIN sections ON sections.rowid = chunks.section_rowid "
                "WHERE sections.scope = 'sections' AND sections.relative_path = ?",
                (target_rel,),
            ).fetchall()
            if not target_chunks:
                continue

            best = None
            best_pair: tuple[str, str] | None = None
            for a_chunk_id, a_section_id in anchor_chunks:
                vec_row = conn.execute(
                    "SELECT embedding FROM sections_vec WHERE rowid = ?",
                    (a_chunk_id,),
                ).fetchone()
                if not vec_row:
                    continue
                rows = conn.execute(
                    "SELECT vec.distance, sections.section_id "
                    "FROM sections_vec vec "
                    "JOIN chunks c ON c.chunk_id = vec.rowid "
                    "JOIN sections ON sections.rowid = c.section_rowid "
                    "WHERE vec.embedding MATCH ? AND vec.k = ? "
                    "  AND sections.scope = 'sections' "
                    "  AND sections.relative_path = ? "
                    "ORDER BY vec.distance LIMIT 1",
                    (vec_row[0], max(5, len(target_chunks)), target_rel),
                ).fetchall()
                for distance, t_section_id in rows:
                    d = float(distance)
                    if best is None or d < best:
                        best = d
                        best_pair = (a_section_id, t_section_id)

            if best is not None and best > threshold:
                suspicious.append(
                    {
                        "target_relative_path": target_rel,
                        "best_distance": best,
                        "anchor_section": best_pair[0] if best_pair else "",
                        "target_section": best_pair[1] if best_pair else "",
                    }
                )

        return suspicious
    finally:
        conn.close()


def _target_chunks(conn, corpus_root: Path, target_path: Path) -> list[dict[str, Any]]:
    if target_path.is_file():
        rel = target_path.relative_to(corpus_root).as_posix()
        rows = conn.execute(
            "SELECT c.chunk_id, s.section_id, s.relative_path, s.start_line, s.heading_chain "
            "FROM chunks c "
            "JOIN sections s ON s.rowid = c.section_rowid "
            "WHERE s.scope = 'sections' AND s.relative_path = ? "
            "ORDER BY s.relative_path, s.start_line, c.chunk_idx",
            (rel,),
        ).fetchall()
    else:
        rel_prefix = target_path.relative_to(corpus_root).as_posix()
        if rel_prefix in {"", "."}:
            like_value = "%"
        else:
            like_value = f"{rel_prefix.rstrip('/')}/%"
        rows = conn.execute(
            "SELECT c.chunk_id, s.section_id, s.relative_path, s.start_line, s.heading_chain "
            "FROM chunks c "
            "JOIN sections s ON s.rowid = c.section_rowid "
            "WHERE s.scope = 'sections' AND s.relative_path LIKE ? "
            "ORDER BY s.relative_path, s.start_line, c.chunk_idx",
            (like_value,),
        ).fetchall()
    return [
        {
            "chunk_id": int(chunk_id),
            "section_id": section_id,
            "relative_path": relative_path,
            "start_line": int(start_line),
            "heading_chain": heading_chain,
        }
        for chunk_id, section_id, relative_path, start_line, heading_chain in rows
    ]


def _nearest_external_sections(
    conn,
    *,
    corpus_root: Path,
    target_chunks: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    del corpus_root
    target_paths = {str(row["relative_path"]) for row in target_chunks}
    best_by_section: dict[str, dict[str, Any]] = {}
    over_fetch = max(100, limit * 16)

    for target_chunk in target_chunks:
        vec_row = conn.execute(
            "SELECT embedding FROM sections_vec WHERE rowid = ?",
            (target_chunk["chunk_id"],),
        ).fetchone()
        if not vec_row:
            continue
        rows = conn.execute(
            "SELECT s.section_id, s.relative_path, s.start_line, s.heading_chain, "
            "s.heading_text, s.body, s.token_count, vec.distance "
            "FROM sections_vec vec "
            "JOIN chunks c ON c.chunk_id = vec.rowid "
            "JOIN sections s ON s.rowid = c.section_rowid "
            "WHERE vec.embedding MATCH ? AND vec.k = ? "
            "  AND s.scope = 'sections' "
            "ORDER BY vec.distance",
            (vec_row[0], over_fetch),
        ).fetchall()
        for section_id, rel, start_line, heading_chain, heading_text, body, token_count, distance in rows:
            if rel in target_paths:
                continue
            d = float(distance)
            previous = best_by_section.get(section_id)
            if previous is not None and previous["_distance"] <= d:
                continue
            best_by_section[section_id] = {
                "section_id": section_id,
                "relative_path": rel,
                "heading_chain": heading_chain,
                "heading_text": heading_text,
                "start_line": int(start_line),
                "token_count": int(token_count or 0),
                "snippet": _snippet(str(body or "")),
                "_body": str(body or ""),
                "_distance": d,
                "matched_target": {
                    "section_id": target_chunk["section_id"],
                    "relative_path": target_chunk["relative_path"],
                    "heading_chain": target_chunk["heading_chain"],
                    "start_line": target_chunk["start_line"],
                },
            }

    rows = sorted(best_by_section.values(), key=lambda row: (row["_distance"], row["relative_path"], row["start_line"]))
    return rows[:limit]


def _shape_payload(
    *,
    corpus_root: Path,
    target_path: Path,
    target_chunks: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    limit: int,
    expanded: bool,
    token_budget: int | None,
) -> dict[str, Any]:
    budget_defaulted = expanded and token_budget is None
    budget = DEFAULT_EXPANDED_TOKEN_BUDGET if budget_defaulted else int(token_budget or 0)
    shaped: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    token_total = 0
    for rank, raw in enumerate(candidates, start=1):
        row = {
            "rank": rank,
            "section_id": raw["section_id"],
            "mdref": f"{raw['relative_path']}:L{raw['start_line']}",
            "relative_path": raw["relative_path"],
            "heading_chain": raw["heading_chain"],
            "heading_text": raw["heading_text"],
            "start_line": raw["start_line"],
            "token_count": raw["token_count"],
            "snippet": raw["snippet"],
            "matched_target": raw["matched_target"],
            "candidate_class": "semantic_neighbor",
            "source_layer": "semantic_index",
            "obligation": False,
            "graph_edge": False,
        }
        if expanded:
            tokens = int(raw.get("token_count") or 0)
            body = str(raw.get("_body") or "")
            if budget and token_total + tokens > budget:
                remaining = max(budget - token_total, 0)
                if remaining > 0:
                    row["content"] = body[: remaining * 4].rstrip() + f"\n\n...[truncated to ~{budget} approx tokens]\n"
                    row["included_token_count"] = remaining
                    row["truncated_by_budget"] = True
                    token_total += remaining
                    dropped.append(
                        {
                            "section_id": raw["section_id"],
                            "relative_path": raw["relative_path"],
                            "tokens": tokens,
                            "included_tokens": remaining,
                            "reason": "truncated",
                        }
                    )
                else:
                    dropped.append(
                        {
                            "section_id": raw["section_id"],
                            "relative_path": raw["relative_path"],
                            "tokens": tokens,
                            "reason": "over_budget",
                        }
                    )
                    continue
            else:
                row["content"] = body
                row["included_token_count"] = tokens
                token_total += tokens
        shaped.append(row)

    target_rel = target_path.relative_to(corpus_root).as_posix()
    target_value = {
        "path": str(target_path),
        "relative_path": target_rel if target_rel else ".",
        "kind": "folder" if target_path.is_dir() else "file",
    }
    payload = {
        "command": "semantic-neighbors",
        "corpus": str(corpus_root),
        "target": target_value,
        "expanded": bool(expanded),
        "view": "expanded" if expanded else "map",
        "limit": limit,
        "target_sections": len({row["section_id"] for row in target_chunks}),
        "candidates": shaped,
        "candidate_token_total": sum(int(row.get("token_count") or 0) for row in shaped),
        "token_total": token_total,
        "token_budget": budget if expanded else 0,
        "token_budget_defaulted": budget_defaulted,
        "dropped_by_budget": dropped,
        "usage_note": "candidate only, not graph obligation",
        "read_next": [] if expanded else [
            _read_next(
                "md_semantic_neighbors",
                {
                    "target": str(target_path),
                    "corpus": str(corpus_root),
                    "limit": limit,
                    "expanded": True,
                },
                "Expand selected semantic-neighbor candidates into section bodies.",
            )
        ],
    }
    return payload


def _snippet(text: str, width: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= width:
        return compact
    end = width
    while end < len(compact) and end < width + 40 and not compact[end].isspace():
        end += 1
    if end >= len(compact):
        return compact
    return compact[:end].rstrip() + "..."
