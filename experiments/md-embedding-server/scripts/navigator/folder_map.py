from __future__ import annotations

from pathlib import Path
from typing import Any

from .markdown_io import (
    approx_tokens,
    collect_headings,
    iter_markdown,
    parse_frontmatter,
    section_token_count,
)


def build_map(path: Path, max_heading_level: int, with_tokens: bool = False) -> dict[str, Any]:
    root = path.resolve()
    files: list[dict[str, Any]] = []
    for file_index, file_path in enumerate(iter_markdown(path), start=1):
        text = file_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        frontmatter = parse_frontmatter(lines)
        headings = collect_headings(lines, max_heading_level)
        # Single-file corpus: `root` IS the file, so `relative_to(root)` is
        # impossible and `file_path.resolve()` would give an absolute path —
        # confusing for a field literally named `relative_path` and broken
        # for downstream consumers (path filters, pick, search remap).
        # Use the bare filename instead so the field stays "relative-ish".
        if root.is_dir():
            rel_path = str(file_path.resolve().relative_to(root))
        else:
            rel_path = file_path.name
        title = next((h["text"] for h in headings if h["level"] == 1), "")
        heading_items = []
        for heading_index, heading in enumerate(headings, start=1):
            item: dict[str, Any] = {
                "id": f"{file_index}.{heading_index}",
                "line": heading["line"],
                "level": heading["level"],
                "text": heading["text"],
            }
            if with_tokens:
                item["tokens"] = section_token_count(lines, heading["line"], heading["level"])
            heading_items.append(item)
        file_entry: dict[str, Any] = {
            "id": file_index,
            "path": str(file_path.resolve()),
            "relative_path": rel_path,
            "description": frontmatter.get("description", ""),
            "title": title,
            "heading_count": len(heading_items),
            "headings": heading_items,
        }
        if with_tokens:
            file_entry["tokens"] = approx_tokens(text)
        files.append(file_entry)
    data: dict[str, Any] = {
        "root": str(root),
        "file_count": len(files),
        "description_gap_count": sum(1 for item in files if not item["description"]),
        "heading_count": sum(item["heading_count"] for item in files),
        "files": files,
    }
    if with_tokens:
        data["token_count"] = sum(item.get("tokens", 0) for item in files)
    return data


def query_terms(query: str) -> list[str]:
    return [term.lower() for term in query.split() if term.strip()]


def matched_terms(item: dict[str, Any], terms: list[str]) -> list[str]:
    if not terms:
        return []
    haystack = " ".join(
        [
            (item.get("description") or "").lower(),
            (item.get("title") or "").lower(),
            item["relative_path"].lower(),
            " ".join((h.get("text") or "").lower() for h in item["headings"]),
        ]
    )
    return [term for term in terms if term in haystack]


def apply_match_filter(data: dict[str, Any], query: str) -> dict[str, Any]:
    if not query:
        return data
    terms = query_terms(query)
    filtered_files: list[dict[str, Any]] = []
    for item in data["files"]:
        hits = matched_terms(item, terms)
        if hits:
            enriched = dict(item)
            enriched["matched_terms"] = hits
            filtered_files.append(enriched)
    data = dict(data)
    data["files"] = filtered_files
    data["file_count"] = len(filtered_files)
    data["description_gap_count"] = sum(1 for item in filtered_files if not item["description"])
    data["heading_count"] = sum(item["heading_count"] for item in filtered_files)
    if "token_count" in data:
        data["token_count"] = sum(item.get("tokens", 0) for item in filtered_files)
    data["match"] = query
    data["match_terms"] = terms
    return data


def render_map(data: dict[str, Any], include_headings: bool, with_tokens: bool) -> str:
    lines = [
        f"# Markdown map: {data['root']}",
        "",
        f"Files: {data['file_count']}",
        f"Description gaps: {data['description_gap_count']}",
        f"Headings: {data['heading_count']}",
    ]
    if with_tokens and "token_count" in data:
        lines.append(f"Tokens (approx): {data['token_count']}")
    if data.get("match"):
        lines.append(f"Match filter: {data['match']}")
    lines.append("")
    for item in data["files"]:
        desc = item["description"] or "TODO description"
        title = f" | title: {item['title']}" if item["title"] else ""
        tokens = f" | {item['tokens']}t" if with_tokens and "tokens" in item else ""
        match_hits = (
            f" | match: {','.join(item['matched_terms'])}"
            if item.get("matched_terms")
            else ""
        )
        lines.append(
            f"{item['id']}. {item['relative_path']} - {desc}{title} "
            f"({item['heading_count']} headings{tokens}){match_hits}"
        )
        if include_headings:
            for heading in item["headings"]:
                hashes = "#" * heading["level"]
                section_tokens = f" — {heading['tokens']}t" if with_tokens and "tokens" in heading else ""
                lines.append(
                    f"   [{heading['id']}] L{heading['line']} {hashes} {heading['text']}{section_tokens}"
                )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
