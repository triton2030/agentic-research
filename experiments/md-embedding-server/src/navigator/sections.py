from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .markdown_io import HEADING_RE, approx_tokens


# Sections with body > this many approx_tokens get sub-chunked at index time so
# the embedding model's max_seq_length (8192 BPE for BGE-M3, ~1.5-2x our
# approx_tokens for mixed RU/EN) does not silently truncate the tail. We keep
# a generous safety margin below the cap; most real sections fit in one chunk.
# Each sub-chunk inherits the same heading-chain prefix; retrieval dedupes
# sub-chunks back to the parent section.
SUBCHUNK_MAX_TOKENS = 2000


def _section_hash(rel: str, start_line: int, body: str, scope: str = "sections") -> str:
    # Default scope = "sections" keeps backwards compat with existing on-disk
    # embedding cache keys. Other scopes get an explicit namespace prefix so
    # caches do not collide.
    if scope == "sections":
        payload = f"{rel}|{start_line}|{body}"
    else:
        payload = f"{scope}|{rel}|{start_line}|{body}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _chunk_hash_for(section_hash: str, chunk_idx: int) -> str:
    # chunk_idx == 0 reuses the bare section_hash so sections that fit in one
    # chunk still hit the pre-subchunking cache layout. Sub-chunked sections
    # generate fresh keys per index — even chunk_idx == 0 of a long section
    # represents different text than the pre-subchunking embedding, so callers
    # decide via `_should_subchunk()` before picking the key strategy.
    if chunk_idx == 0:
        return section_hash
    return hashlib.sha256(
        f"{section_hash}|chunk{chunk_idx}".encode("utf-8")
    ).hexdigest()


def _split_body_into_chunks(body: str, max_tokens: int = SUBCHUNK_MAX_TOKENS) -> list[str]:
    """Split body into ~max_tokens chunks at paragraph then sentence boundaries.
    Returns [body] when body already fits (or is empty)."""
    if not body or approx_tokens(body) <= max_tokens:
        return [body] if body else [""]

    paragraphs = re.split(r"\n\n+", body)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current, current_tokens
        if current:
            chunks.append("\n\n".join(current).strip())
            current = []
            current_tokens = 0

    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        p_tokens = approx_tokens(p_clean)
        if p_tokens > max_tokens:
            flush()
            sentences = re.split(r"(?<=[.!?])\s+", p_clean)
            sent_buf: list[str] = []
            sent_tokens = 0
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                s_tokens = approx_tokens(s)
                if sent_buf and sent_tokens + s_tokens > max_tokens:
                    chunks.append(" ".join(sent_buf).strip())
                    sent_buf = [s]
                    sent_tokens = s_tokens
                else:
                    sent_buf.append(s)
                    sent_tokens += s_tokens
            if sent_buf:
                chunks.append(" ".join(sent_buf).strip())
            continue
        if current and current_tokens + p_tokens > max_tokens:
            flush()
        current.append(p_clean)
        current_tokens += p_tokens
    flush()
    return chunks or [""]


def _should_subchunk(body: str, max_tokens: int = SUBCHUNK_MAX_TOKENS) -> bool:
    return bool(body) and approx_tokens(body) > max_tokens


def _extract_section_body(
    lines: list[str], start_line: int, level: int
) -> tuple[str, int]:
    """Body text after the heading line, until the next same-or-shallower heading.
    For level == 0 (whole-file no-headings), returns the full text."""
    if level == 0:
        return "\n".join(lines).strip(), len(lines)
    start_idx = start_line - 1
    end_idx = len(lines)
    in_fence = False
    for idx in range(start_idx + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(lines[idx].rstrip())
        if m and len(m.group(1)) <= level:
            end_idx = idx
            break
    body = "\n".join(lines[start_idx + 1 : end_idx]).strip()
    return body, end_idx


def _make_section(
    section_id: str,
    file_id: int,
    relative_path: str,
    start_line: int,
    level: int,
    heading_text: str,
    heading_chain: list[str],
    body: str,
    file_description: str,
    file_title: str,
) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "file_id": file_id,
        "relative_path": relative_path,
        "start_line": start_line,
        "level": level,
        "heading_text": heading_text,
        "heading_chain": heading_chain,
        "body": body,
        "file_description": file_description,
        "file_title": file_title,
        "content_hash": _section_hash(relative_path, start_line, body),
        "token_count": approx_tokens(body) + approx_tokens(heading_text),
    }


def build_items_from_map(
    data: dict[str, Any], scope: str = "sections"
) -> list[dict[str, Any]]:
    """Dispatcher: scope='sections' returns heading-bounded sections,
    scope='descriptions' returns one item per file whose frontmatter
    description is non-empty (body = the description itself)."""
    if scope == "descriptions":
        return build_description_items(data)
    return build_sections_from_map(data)


def build_description_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    """File-level items for `--scope descriptions`: each item is one file
    whose body is its frontmatter description. Skipped if description is
    missing or empty. Embeddings then ride the existing pipeline."""
    items: list[dict[str, Any]] = []
    for f in data["files"]:
        desc = (f.get("description") or "").strip()
        if not desc:
            continue
        item: dict[str, Any] = {
            "section_id": f"{f['id']}.desc",
            "file_id": f["id"],
            "relative_path": f["relative_path"],
            "start_line": 1,
            "level": 0,
            "heading_text": "(description)",
            "heading_chain": [],
            "body": desc,
            "file_description": desc,
            "file_title": f.get("title", "") or "",
            "token_count": approx_tokens(desc),
            "scope": "descriptions",
        }
        item["content_hash"] = _section_hash(
            item["relative_path"], 1, desc, scope="descriptions"
        )
        items.append(item)
    return items


def build_sections_from_map(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten map_data into a list of section dicts ready for indexing."""
    sections: list[dict[str, Any]] = []
    for f in data["files"]:
        file_path = Path(f["path"])
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        f_desc = f.get("description", "") or ""
        f_title = f.get("title", "") or ""
        if not f["headings"]:
            body = "\n".join(lines).strip()
            sections.append(
                _make_section(
                    f"{f['id']}.0",
                    f["id"],
                    f["relative_path"],
                    1,
                    0,
                    "",
                    [],
                    body,
                    f_desc,
                    f_title,
                )
            )
            continue
        chain_stack: list[tuple[int, str]] = []
        for h in f["headings"]:
            while chain_stack and chain_stack[-1][0] >= h["level"]:
                chain_stack.pop()
            chain_stack.append((h["level"], h["text"]))
            body, _end = _extract_section_body(lines, h["line"], h["level"])
            sections.append(
                _make_section(
                    h["id"],
                    f["id"],
                    f["relative_path"],
                    h["line"],
                    h["level"],
                    h["text"],
                    [x[1] for x in chain_stack],
                    body,
                    f_desc,
                    f_title,
                )
            )
    return sections


def _contextual_prefix(sec: dict[str, Any]) -> str:
    """Structural prefix portion of Contextual Retrieval (no body)."""
    parts: list[str] = []
    if sec.get("file_description"):
        parts.append(sec["file_description"])
    if sec.get("file_title"):
        parts.append(sec["file_title"])
    chain = sec.get("heading_chain")
    if chain:
        if isinstance(chain, list):
            parts.append(" > ".join(chain))
        else:
            parts.append(str(chain))
    if sec.get("heading_text") and not chain:
        parts.append(sec["heading_text"])
    return "\n".join(parts)


def _contextual_passage(sec: dict[str, Any], body_override: str | None = None) -> str:
    """Structural Contextual Retrieval shape: prepend description + title +
    heading-chain to the body before embedding. Anthropic's Sept 2024
    pattern, without the LLM call — structural context is free here.

    `body_override` lets sub-chunked sections share one prefix but vary the
    body slice per chunk."""
    prefix = _contextual_prefix(sec)
    body = sec.get("body") if body_override is None else body_override
    body = body or ""
    if not body:
        return prefix
    if not prefix:
        return body
    return prefix + "\n" + body
