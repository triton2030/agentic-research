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


def _sort_id(value: str) -> tuple[int, int | str]:
    try:
        return (0, int(value))
    except ValueError:
        return (1, value)


def _path_from_search_result(root: str, relative_path: str) -> str:
    path = Path(relative_path)
    if path.is_absolute():
        return str(path)
    if root:
        return str(Path(root) / relative_path)
    return relative_path


def _map_search_results(data: dict[str, Any]) -> dict[str, Any]:
    files_by_id: dict[str, dict[str, Any]] = {}
    root = str(data.get("root") or "")
    for result in data.get("results", []):
        file_id = str(result.get("file_id") or "")
        section_id = str(result.get("section_id") or "")
        relative_path = str(result.get("relative_path") or "")
        if not file_id or not section_id or not relative_path:
            continue
        file_item = files_by_id.setdefault(
            file_id,
            {
                "id": result.get("file_id"),
                "path": result.get("path") or _path_from_search_result(root, relative_path),
                "relative_path": relative_path,
                "description": result.get("file_description") or "",
                "title": result.get("file_title") or "",
                "heading_count": 0,
                "headings": [],
            },
        )
        heading: dict[str, Any] = {
            "id": section_id,
            "line": int(result.get("start_line") or 1),
            "level": int(result.get("level") or 0),
            "text": result.get("heading_text") or result.get("heading_chain") or section_id,
        }
        if "token_count" in result:
            heading["tokens"] = result["token_count"]
        if "body" in result:
            heading["body"] = result["body"]
        file_item["headings"].append(heading)
        file_item["heading_count"] = len(file_item["headings"])
    return {
        "root": root,
        "files": list(files_by_id.values()),
    }


def normalize_map_data(data: dict[str, Any]) -> dict[str, Any]:
    if "files" in data:
        return data
    if "results" in data:
        return _map_search_results(data)
    return {
        "root": data.get("root", ""),
        "files": [],
    }


def heading_content(item: dict[str, Any], heading: dict[str, Any]) -> str:
    if int(heading.get("level") or 0) <= 0 and "body" in heading:
        return str(heading["body"])
    try:
        content = section_lines(Path(item["path"]), int(heading.get("line") or 1))
    except OSError:
        content = ""
    return content or str(heading.get("body") or "")


def pick_items(
    data: dict[str, Any],
    file_ids: set[str],
    heading_ids: set[str],
    extract: bool,
    token_budget: int = 0,
) -> dict[str, Any]:
    data = normalize_map_data(data)
    files_by_id = {str(item["id"]): item for item in data["files"]}
    picked_files = [files_by_id[file_id] for file_id in sorted(file_ids, key=_sort_id) if file_id in files_by_id]
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
                selected["content"] = heading_content(item, heading)
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
