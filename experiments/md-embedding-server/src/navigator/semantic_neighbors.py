from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .api_utils import _exit, _read_next
from .index_meta import _open_index_readonly
from .index_resolution import index_conflict_payload, index_exists


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
    if not index_exists(corpus_root, cache_root=cache_root):
        return _index_warmup_required(corpus_root, target_path)
    conflict = index_conflict_payload(corpus_root, cache_root=cache_root)
    if conflict is not None:
        return conflict

    try:
        conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    except FileNotFoundError:
        return _index_warmup_required(corpus_root, target_path)
    except (ModuleNotFoundError, RuntimeError, sqlite3.Error) as exc:
        return _exit({"error": "dependency_failed", "detail": str(exc)}, 3)

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
