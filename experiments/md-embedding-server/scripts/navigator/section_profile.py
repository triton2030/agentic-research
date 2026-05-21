from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .embeddings import OpenRouterClient
from .index_meta import _index_dir_for_corpus

PROFILE_VERSION = "section-profile-2026-05-21"
DEFAULT_PROFILE_MODEL = os.environ.get(
    "MD_PROFILE_MODEL", "anthropic/claude-haiku-4.5"
)
DEFAULT_PROFILE_MODE = os.environ.get("MD_PROFILE_MODE", "heuristic")
HEURISTIC_MODEL = "local-heuristic"
VALID_TYPES = {
    "definition",
    "decision",
    "open-question",
    "rule",
    "example",
    "uses",
    "external-citation",
    "heading-only",
}

CLASSIFICATION_PROMPT = """You are a section profile classifier for a Markdown knowledge corpus.

Return JSON only:
{{
  "type": "definition|decision|open-question|rule|example|uses|external-citation|heading-only",
  "subject": "one sentence, <=100 chars",
  "owns_terms": ["terms this section defines, lowercase, max 5"],
  "mentions": ["terms used but not defined here, lowercase, max 10"],
  "evidence_sources": ["URLs, file paths, named sources, max 5"],
  "confidence": 0.0
}}

Decision rules:
- definition: explicitly defines a term or contract.
- decision: records a choice, commitment, or stopped alternative.
- open-question: unresolved question, TODO, blocker, or explicit unknown.
- rule: actionable prescription: always/never/must/should.
- example: usage demonstration of a concept defined elsewhere.
- uses: uses or explains concepts without owning their definition.
- external-citation: primarily cites an external source.
- heading-only: no substantive body.

Be conservative: when unsure between definition and uses, choose uses.

Section heading: {heading}
Section text:
{body}
"""

TYPE_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("open-question", ("todo", "open question", "unresolved", "вопрос", "?", "нужно решить", "блокер")),
    ("decision", ("decision", "decided", "решение", "выбрано", "фиксируем", "зафиксировано", "отклонён")),
    ("rule", ("must", "must not", "always", "never", "should", "нельзя", "всегда", "никогда", "обязательно", "правило")),
    ("definition", ("definition", "source of truth", "owner", "источник истины", "владелец", "контракт", "означает", "это ")),
    ("example", ("example", "sample", "пример", "wrong", "right", "например")),
    ("external-citation", ("http://", "https://", "paper", "docs", "source:", "источник:")),
]


def _terms(text: str) -> list[str]:
    backticked = re.findall(r"`([^`]{2,80})`", text)
    latin_caps = re.findall(r"\b[A-Z][A-Za-z0-9_-]{2,}\b", text)
    cyrillic_phrases = re.findall(r"\b[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁа-яё][а-яё]+){0,2}\b", text)
    seen: set[str] = set()
    out: list[str] = []
    for raw in [*backticked, *latin_caps, *cyrillic_phrases]:
        term = raw.strip().lower()
        if not term or term in seen:
            continue
        seen.add(term)
        out.append(term)
        if len(out) >= 12:
            break
    return out


def _normalize_profile(profile: dict[str, Any], fallback_subject: str) -> dict[str, Any]:
    ptype = str(profile.get("type") or "uses").strip()
    if ptype not in VALID_TYPES:
        ptype = "uses"
    subject = str(profile.get("subject") or fallback_subject or "")[:100]
    owns_terms = [
        str(term).strip().lower()
        for term in (profile.get("owns_terms") or [])
        if str(term).strip()
    ][:5]
    mentions = [
        str(term).strip().lower()
        for term in (profile.get("mentions") or [])
        if str(term).strip()
    ][:10]
    evidence_sources = [
        str(item).strip()
        for item in (profile.get("evidence_sources") or [])
        if str(item).strip()
    ][:5]
    try:
        confidence = float(profile.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence = 0.5
    return {
        "type": ptype,
        "subject": subject,
        "owns_terms": owns_terms,
        "mentions": mentions,
        "evidence_sources": evidence_sources,
        "confidence": max(0.0, min(1.0, round(confidence, 2))),
    }


def classify_section_heuristic(section: dict[str, Any]) -> dict[str, Any]:
    heading = str(section.get("heading_text") or "")
    chain = str(section.get("heading_chain") or "")
    body = str(section.get("body") or "")
    text = f"{heading}\n{chain}\n{body}"
    lowered = text.lower()

    if len(body.strip()) < 40:
        selected = "heading-only"
        evidence: list[str] = []
    else:
        selected = "uses"
        evidence = []
        for profile_type, keywords in TYPE_KEYWORDS:
            hits = [kw for kw in keywords if kw in lowered]
            if hits:
                selected = profile_type
                evidence = hits[:5]
                break

    terms = _terms(text)
    confidence = 0.5 + min(0.25, len(evidence) * 0.07)
    if selected in {"uses", "heading-only"}:
        confidence = 0.45
    return {
        "type": selected,
        "subject": heading or chain or str(section.get("relative_path") or ""),
        "owns_terms": terms[:5] if selected in {"definition", "rule", "decision"} else [],
        "mentions": terms[:10],
        "evidence_sources": evidence if selected == "external-citation" else [],
        "confidence": round(confidence, 2),
    }


def classify_section_llm(
    section: dict[str, Any],
    client: OpenRouterClient,
    model: str = DEFAULT_PROFILE_MODEL,
) -> dict[str, Any]:
    heading = str(section.get("heading_text") or section.get("heading_chain") or "")
    body = str(section.get("body") or "")
    prompt = CLASSIFICATION_PROMPT.format(heading=heading[:200], body=body[:3000])
    raw = client.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.0,
    ).strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.removeprefix("json").strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(raw[start : end + 1])
    if not isinstance(parsed, dict):
        raise RuntimeError("Profile classifier returned non-object JSON")
    return _normalize_profile(parsed, fallback_subject=heading)


def classify_section(
    section: dict[str, Any],
    client: OpenRouterClient | None = None,
    model: str = DEFAULT_PROFILE_MODEL,
    mode: str = "heuristic",
) -> dict[str, Any]:
    profile, _, _ = _classify_section_with_method(
        section,
        client=client,
        model=model,
        mode=mode,
    )
    return profile


def _classify_section_with_method(
    section: dict[str, Any],
    client: OpenRouterClient | None = None,
    model: str = DEFAULT_PROFILE_MODEL,
    mode: str = "heuristic",
) -> tuple[dict[str, Any], str, str]:
    if mode in {"llm", "auto"} and client is not None:
        try:
            return classify_section_llm(section, client=client, model=model), "llm", model
        except Exception:
            if mode == "llm":
                raise
    return classify_section_heuristic(section), "heuristic", HEURISTIC_MODEL


def _profile_from_row(row: Any) -> dict[str, Any]:
    keys = [
        "rowid",
        "section_id",
        "relative_path",
        "start_line",
        "level",
        "heading_text",
        "heading_chain",
        "body",
        "token_count",
        "profile_type",
        "profile_version",
        "profile_model",
        "profile_source_mtime",
    ]
    return dict(zip(keys, row))


def _source_mtime(corpus_root: Path | None, relative_path: str) -> float | None:
    if corpus_root is None:
        return None
    try:
        return (corpus_root / relative_path).stat().st_mtime
    except OSError:
        return None


def _needs_profile(
    section: dict[str, Any],
    current_model: str,
    source_mtime: float | None,
    force: bool,
) -> bool:
    if force:
        return True
    if not section.get("profile_type"):
        return True
    if section.get("profile_version") != PROFILE_VERSION:
        return True
    stored_model = section.get("profile_model")
    if stored_model != current_model:
        if current_model == HEURISTIC_MODEL and stored_model:
            # Cheap default mode must not downgrade an existing LLM profile.
            return False
        return True
    if source_mtime is not None:
        cached = section.get("profile_source_mtime")
        if cached is None or abs(float(cached) - float(source_mtime)) > 0.001:
            return True
    return False


def _write_profile(
    conn,
    rowid: int,
    profile: dict[str, Any],
    model: str,
    method: str,
    source_mtime: float | None,
) -> None:
    conn.execute(
        "UPDATE sections SET "
        "profile_type=?, profile_subject=?, profile_owns_terms=?, "
        "profile_mentions=?, profile_evidence=?, profile_confidence=?, "
        "profile_version=?, profile_model=?, profile_classified_at=?, "
        "profile_source_mtime=?, profile_method=? "
        "WHERE rowid=?",
        (
            profile["type"],
            profile["subject"],
            json.dumps(profile["owns_terms"], ensure_ascii=False),
            json.dumps(profile["mentions"], ensure_ascii=False),
            json.dumps(profile["evidence_sources"], ensure_ascii=False),
            float(profile["confidence"]),
            PROFILE_VERSION,
            model,
            datetime.now(timezone.utc).isoformat(),
            source_mtime,
            method,
            rowid,
        ),
    )


def profile_corpus(
    conn,
    corpus_root: Path | None = None,
    limit: int | None = None,
    force: bool = False,
    mode: str | None = None,
    model: str | None = None,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> dict[str, Any]:
    from .index_meta import _ensure_profile_columns
    from .filters import normalize_path_filter_patterns, sqlite_path_filter_sql

    _ensure_profile_columns(conn)
    if getattr(conn, "in_transaction", False):
        conn.commit()
    selected_mode = mode or DEFAULT_PROFILE_MODE
    selected_model = model or DEFAULT_PROFILE_MODEL
    if selected_mode not in {"heuristic", "llm", "auto"}:
        selected_mode = "heuristic"
    current_model = selected_model if selected_mode in {"llm", "auto"} else HEURISTIC_MODEL
    client = (
        OpenRouterClient(corpus_root=corpus_root)
        if selected_mode in {"llm", "auto"}
        else None
    )

    sql = (
        "SELECT rowid, section_id, relative_path, start_line, level, heading_text, "
        "heading_chain, body, token_count, profile_type, profile_version, "
        "profile_model, profile_source_mtime FROM sections "
        "WHERE scope='sections'"
    )
    if corpus_root is not None:
        include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
        exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
    else:
        include_patterns = list(path_include or [])
        exclude_patterns = list(path_exclude or [])
    path_clause, path_params = sqlite_path_filter_sql(
        "relative_path",
        include_patterns,
        exclude_patterns,
    )
    sql += path_clause
    sql += " ORDER BY relative_path, start_line"
    params: list[Any] = list(path_params)
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    stats = {
        "total_sections": len(rows),
        "profiled": 0,
        "skipped_cached": 0,
        "failed": 0,
        "cost_estimate_usd": 0.0,
        "model": current_model,
        "version": PROFILE_VERSION,
        "mode": selected_mode,
        "path_include": include_patterns,
        "path_exclude": exclude_patterns,
    }
    for row in rows:
        section = _profile_from_row(row)
        source_mtime = _source_mtime(corpus_root, str(section["relative_path"]))
        if not _needs_profile(section, current_model, source_mtime, force):
            stats["skipped_cached"] += 1
            continue
        try:
            profile, method, model_used = _classify_section_with_method(
                section,
                client=client,
                model=selected_model,
                mode=selected_mode,
            )
            _write_profile(
                conn,
                int(section["rowid"]),
                profile,
                model=model_used,
                method=method,
                source_mtime=source_mtime,
            )
            conn.commit()
            stats["profiled"] += 1
            if method == "llm":
                stats["cost_estimate_usd"] += 0.001
        except Exception:
            if getattr(conn, "in_transaction", False):
                conn.rollback()
            stats["failed"] += 1
    stats["cost_estimate_usd"] = round(float(stats["cost_estimate_usd"]), 4)
    return stats


def profile_unprofiled_sections(
    conn,
    limit: int | None = None,
    corpus_root: Path | None = None,
    force: bool = False,
    mode: str | None = None,
    model: str | None = None,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> int:
    return int(
        profile_corpus(
            conn,
            corpus_root=corpus_root,
            limit=limit,
            force=force,
            mode=mode,
            model=model,
            path_include=path_include,
            path_exclude=path_exclude,
        )["profiled"]
    )


def profile_rows(
    conn,
    types: list[str] | None = None,
    filter_text: str | None = None,
    limit: int = 50,
    corpus_root: Path | None = None,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> list[dict[str, Any]]:
    from .index_meta import _ensure_profile_columns
    from .filters import normalize_path_filter_patterns, sqlite_path_filter_sql

    _ensure_profile_columns(conn)
    where = "WHERE scope='sections' AND profile_type IS NOT NULL"
    params: list[Any] = []
    if corpus_root is not None:
        include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
        exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
    else:
        include_patterns = list(path_include or [])
        exclude_patterns = list(path_exclude or [])
    path_clause, path_params = sqlite_path_filter_sql(
        "relative_path",
        include_patterns,
        exclude_patterns,
    )
    where += path_clause
    params.extend(path_params)
    if types:
        placeholders = ",".join("?" * len(types))
        where += f" AND profile_type IN ({placeholders})"
        params.extend(types)
    if filter_text:
        where += " AND (LOWER(profile_subject) LIKE ? OR LOWER(heading_text) LIKE ?)"
        needle = f"%{filter_text.lower()}%"
        params.extend([needle, needle])
    params.append(limit)
    rows = conn.execute(
        "SELECT section_id, relative_path, start_line, heading_text, heading_chain, "
        "profile_type, profile_subject, profile_owns_terms, profile_mentions, "
        "profile_evidence, profile_confidence, profile_model, profile_method "
        "FROM sections "
        f"{where} ORDER BY relative_path, start_line LIMIT ?",
        params,
    ).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "section_id": row[0],
                "relative_path": row[1],
                "start_line": row[2],
                "heading_text": row[3],
                "heading_chain": row[4],
                "profile": {
                    "type": row[5],
                    "subject": row[6],
                    "owns_terms": json.loads(row[7] or "[]"),
                    "mentions": json.loads(row[8] or "[]"),
                    "evidence_sources": json.loads(row[9] or "[]"),
                    "confidence": row[10],
                    "version": PROFILE_VERSION,
                    "model": row[11],
                    "method": row[12],
                },
            }
        )
    return out


def open_profile_db(corpus: Path):
    import sqlite3

    db_path = _index_dir_for_corpus(corpus.resolve(), create=False) / "index.sqlite"
    if not db_path.exists():
        raise RuntimeError(f"No md-navigator index at {db_path}; run `md_navigator.py index {corpus}` first.")
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        import sqlite_vec

        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
    except Exception:
        # Non-vector commands can still read/write ordinary profile columns.
        # Vector-backed originality will fall back if the extension is absent.
        pass
    conn.row_factory = None
    return conn
