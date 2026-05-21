from __future__ import annotations

from typing import Any

import numpy as np


def _tokens(text: str) -> set[str]:
    import re

    return {t.lower() for t in re.findall(r"[\wА-Яа-яЁё-]{3,}", text)}


def _section_lookup(conn, section_id: str) -> tuple[int, str, str, int, str, str]:
    row = conn.execute(
        "SELECT rowid, section_id, relative_path, start_line, heading_text, body "
        "FROM sections WHERE scope='sections' AND (section_id=? OR rowid=?)",
        (section_id, section_id if str(section_id).isdigit() else -1),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Section not found: {section_id}")
    return row


def _section_embedding(conn, rowid: int) -> np.ndarray | None:
    try:
        rows = conn.execute(
            "SELECT sections_vec.embedding FROM sections_vec "
            "JOIN chunks ON chunks.chunk_id = sections_vec.rowid "
            "WHERE chunks.section_rowid = ?",
            (rowid,),
        ).fetchall()
    except Exception:
        return None
    if not rows:
        return None
    vectors = [np.frombuffer(row[0], dtype=np.float32) for row in rows if row[0]]
    if not vectors:
        return None
    vec = np.mean(np.vstack(vectors), axis=0)
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > 1e-12 else vec


def nearest_neighbors(
    conn,
    section_id: str,
    top_k: int = 5,
    exclude_same_file: bool = True,
) -> list[dict[str, Any]]:
    target = _section_lookup(conn, section_id)
    target_vec = _section_embedding(conn, int(target[0]))
    if target_vec is None:
        return []

    params: list[Any] = [target[0]]
    where = "WHERE scope='sections' AND rowid != ?"
    if exclude_same_file:
        where += " AND relative_path != ?"
        params.append(target[2])
    rows = conn.execute(
        "SELECT rowid, section_id, relative_path, start_line, heading_text, "
        "heading_chain, profile_type, profile_subject, profile_owns_terms, "
        "profile_confidence, token_count FROM sections "
        f"{where}",
        params,
    ).fetchall()

    scored: list[dict[str, Any]] = []
    for row in rows:
        vec = _section_embedding(conn, int(row[0]))
        if vec is None:
            continue
        cosine = float(vec @ target_vec)
        scored.append(
            {
                "rowid": row[0],
                "section_id": row[1],
                "relative_path": row[2],
                "start_line": row[3],
                "heading_text": row[4],
                "heading_chain": row[5],
                "profile_type": row[6],
                "profile_subject": row[7],
                "profile_owns_terms": row[8],
                "profile_confidence": row[9],
                "token_count": row[10],
                "cosine_similarity": round(cosine, 4),
            }
        )
    scored.sort(key=lambda item: -item["cosine_similarity"])
    return scored[:top_k]


def _lexical_fallback(conn, target: tuple[Any, ...]) -> dict[str, Any]:
    target_tokens = _tokens(target[5] or "")
    nearest: dict[str, Any] | None = None
    best = 0.0
    for other in conn.execute(
        "SELECT section_id, relative_path, start_line, heading_text, body "
        "FROM sections WHERE scope='sections' AND rowid != ?",
        (target[0],),
    ).fetchall():
        other_tokens = _tokens(other[4] or "")
        score = (
            len(target_tokens & other_tokens) / len(target_tokens | other_tokens)
            if target_tokens and other_tokens
            else 0.0
        )
        if score > best:
            best = score
            nearest = {
                "section_id": other[0],
                "relative_path": other[1],
                "start_line": other[2],
                "heading_text": other[3],
                "similarity": round(score, 3),
            }
    return {
        "uniqueness": round(1.0 - best, 3),
        "nearest_neighbor": nearest,
        "method": "lexical_jaccard_fallback",
    }


def originality_for_section(conn, section_id: str) -> dict[str, Any]:
    target = _section_lookup(conn, section_id)
    neighbors = nearest_neighbors(conn, section_id, top_k=1)
    if neighbors:
        best = neighbors[0]
        uniqueness = max(0.0, min(1.0, 1.0 - float(best["cosine_similarity"])))
        result = {
            "uniqueness": round(uniqueness, 3),
            "nearest_neighbor": best,
            "method": "indexed_embedding_cosine",
        }
    else:
        result = _lexical_fallback(conn, target)
    return {
        "section": {
            "rowid": target[0],
            "section_id": target[1],
            "relative_path": target[2],
            "start_line": target[3],
            "heading_text": target[4],
        },
        **result,
    }
