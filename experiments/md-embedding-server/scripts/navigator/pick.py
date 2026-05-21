from __future__ import annotations

from pathlib import Path
from typing import Any

from .markdown_io import HEADING_RE


def parse_csv(value: str) -> set[str]:
    return {part.strip() for part in value.split(",") if part.strip()}


def section_lines(path: Path, start_line: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if start_line < 1 or start_line > len(lines):
        return ""
    start_index = start_line - 1
    match = HEADING_RE.match(lines[start_index].rstrip())
    if not match:
        return lines[start_index]
    level = len(match.group(1))
    end_index = len(lines)
    in_fence = False
    for index in range(start_index + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        next_match = HEADING_RE.match(lines[index].rstrip())
        if next_match and len(next_match.group(1)) <= level:
            end_index = index
            break
    return "\n".join(lines[start_index:end_index]).strip()


def apply_token_budget(
    files: list[dict[str, Any]],
    headings: list[dict[str, Any]],
    budget: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int]:
    if budget <= 0:
        kept_tokens = sum(f.get("tokens", 0) for f in files) + sum(h.get("tokens", 0) for h in headings)
        return files, headings, [], kept_tokens
    kept_files: list[dict[str, Any]] = []
    kept_headings: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    running = 0
    for item in files:
        cost = item.get("tokens", 0)
        if running + cost <= budget:
            kept_files.append(item)
            running += cost
        else:
            dropped.append({"kind": "file", "id": item["id"], "tokens": cost})
    for heading in headings:
        cost = heading.get("tokens", 0)
        if running + cost <= budget:
            kept_headings.append(heading)
            running += cost
        else:
            dropped.append({"kind": "heading", "id": heading["id"], "tokens": cost})
    return kept_files, kept_headings, dropped, running


def pick_items(
    data: dict[str, Any],
    file_ids: set[str],
    heading_ids: set[str],
    extract: bool,
    token_budget: int = 0,
) -> dict[str, Any]:
    files_by_id = {str(item["id"]): item for item in data["files"]}
    picked_files = [files_by_id[file_id] for file_id in sorted(file_ids, key=int) if file_id in files_by_id]
    # When user asks `pick --files X,Y --extract`, the intent is "give me
    # content of those files". Without this expansion, only file metadata was
    # returned (no body text). Auto-expand to every heading of every picked
    # file. Explicit --headings remain additive — union, not override.
    if extract and picked_files:
        heading_ids = set(heading_ids) | {
            h["id"] for f in picked_files for h in f["headings"]
        }
    picked_headings = []
    for item in data["files"]:
        for heading in item["headings"]:
            if heading["id"] not in heading_ids:
                continue
            selected: dict[str, Any] = {
                "id": heading["id"],
                "file_id": item["id"],
                "path": item["path"],
                "relative_path": item["relative_path"],
                "line": heading["line"],
                "level": heading["level"],
                "text": heading["text"],
            }
            if "tokens" in heading:
                selected["tokens"] = heading["tokens"]
            if extract:
                selected["content"] = section_lines(Path(item["path"]), heading["line"])
            picked_headings.append(selected)
    kept_files, kept_headings, dropped, running = apply_token_budget(
        picked_files, picked_headings, token_budget
    )
    return {
        "root": data["root"],
        "files": kept_files,
        "headings": kept_headings,
        "token_total": running,
        "token_budget": token_budget,
        "dropped_by_budget": dropped,
        "missing_file_ids": sorted(file_ids - set(files_by_id)),
        "missing_heading_ids": sorted(heading_ids - {h["id"] for f in data["files"] for h in f["headings"]}),
    }


def render_pick(selection: dict[str, Any], extract: bool) -> str:
    lines = ["# Markdown selection", ""]
    if selection.get("token_total"):
        budget = selection.get("token_budget", 0)
        budget_note = f" / {budget} budget" if budget else ""
        lines.append(f"Tokens (approx): {selection['token_total']}{budget_note}")
        lines.append("")
    if selection.get("dropped_by_budget"):
        lines.append("## Dropped by token budget")
        for item in selection["dropped_by_budget"]:
            lines.append(f"- {item['kind']} {item['id']} ({item['tokens']}t)")
        lines.append("")
    if selection["files"]:
        lines.append("## Files")
        for item in selection["files"]:
            desc = item["description"] or "TODO description"
            tokens = f" | {item['tokens']}t" if "tokens" in item else ""
            lines.append(f"- [{item['id']}] {item['relative_path']} - {desc}{tokens}")
        lines.append("")
    if selection["headings"]:
        lines.append("## Headings")
        for heading in selection["headings"]:
            hashes = "#" * heading["level"]
            tokens = f" — {heading['tokens']}t" if "tokens" in heading else ""
            lines.append(
                f"- [{heading['id']}] {heading['relative_path']}:L{heading['line']} "
                f"{hashes} {heading['text']}{tokens}"
            )
            if extract and heading.get("content"):
                lines.append("")
                lines.append("```md")
                lines.append(heading["content"])
                lines.append("```")
                lines.append("")
        lines.append("")
    if selection["missing_file_ids"] or selection["missing_heading_ids"]:
        lines.append("## Missing ids")
        if selection["missing_file_ids"]:
            lines.append(f"- files: {', '.join(selection['missing_file_ids'])}")
        if selection["missing_heading_ids"]:
            lines.append(f"- headings: {', '.join(selection['missing_heading_ids'])}")
    return "\n".join(lines).rstrip() + "\n"
