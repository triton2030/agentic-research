from __future__ import annotations

from pathlib import Path
from typing import Any

from .markdown_io import (
    approx_tokens,
    extract_section_by_anchor,
    markdown_lookup,
    relative_path,
    split_link_target,
    wikilinks_with_anchors_from_text,
)


DEFAULT_DEPTH = 3
DEFAULT_TOKEN_BUDGET = 3000


def walk_chain(
    path: str,
    *,
    anchor: str,
    scan: str | None = None,
    depth: int | None = None,
    token_budget: int | None = None,
) -> dict[str, Any]:
    scan_root = Path(scan or ".").expanduser().resolve()
    selected_depth = max(0, int(depth if depth is not None else DEFAULT_DEPTH))
    selected_budget = int(token_budget if token_budget is not None else DEFAULT_TOKEN_BUDGET)
    start_path = _resolve_start_path(path, scan_root)
    if not scan_root.exists():
        return _stop(
            "scan_root_not_found",
            [],
            scan_root=scan_root,
            depth=selected_depth,
            token_budget=selected_budget,
            path=path,
            anchor=anchor,
            exit_code=2,
        )
    if start_path is None:
        return _stop(
            "path_not_found",
            [],
            scan_root=scan_root,
            depth=selected_depth,
            token_budget=selected_budget,
            path=path,
            anchor=anchor,
            exit_code=2,
        )

    lookup = markdown_lookup(scan_root)
    chain: list[dict[str, Any]] = []
    visited: set[tuple[Path, str]] = set()
    total_tokens = 0
    current_path = start_path
    current_anchor = anchor
    links_followed = 0
    skipped_bare_total = 0
    stopped_reason = "depth_reached"
    stop_detail: dict[str, Any] = {}

    while True:
        visit_key = (current_path.resolve(), _normalize_anchor(current_anchor))
        if visit_key in visited:
            stopped_reason = "cycle"
            stop_detail = {
                "cycle_at": {
                    "path": relative_path(current_path, scan_root),
                    "anchor": current_anchor,
                }
            }
            break

        body = extract_section_by_anchor(current_path, current_anchor)
        if body is None:
            stopped_reason = "anchor_not_found"
            stop_detail = {
                "missing": {
                    "path": relative_path(current_path, scan_root),
                    "anchor": current_anchor,
                }
            }
            break

        tokens = approx_tokens(body)
        if selected_budget > 0 and total_tokens + tokens > selected_budget:
            stopped_reason = "token_budget"
            stop_detail = {
                "dropped": {
                    "path": relative_path(current_path, scan_root),
                    "anchor": current_anchor,
                    "tokens": tokens,
                }
            }
            break

        visited.add(visit_key)
        chain.append(
            {
                "step": len(chain),
                "path": relative_path(current_path, scan_root),
                "anchor": current_anchor,
                "content": body,
                "tokens": tokens,
            }
        )
        total_tokens += tokens

        if links_followed >= selected_depth:
            stopped_reason = "depth_reached"
            break

        next_link = _first_anchored_wikilink(body)
        skipped_bare_total += next_link["skipped_bare"]
        if next_link["target"] is None:
            stopped_reason = "no_anchored_outlink"
            stop_detail = {"skipped_bare_wikilinks": skipped_bare_total}
            break

        target_status = _resolve_target_with_collision_check(
            str(next_link["target"]),
            current_path,
            scan_root,
            lookup,
        )
        if target_status["status"] != "ok":
            stopped_reason = target_status["status"]
            stop_detail = {
                "link": next_link,
                "candidates": target_status.get("candidates", []),
            }
            break

        current_path = target_status["path"]
        current_anchor = str(next_link["anchor"])
        links_followed += 1

    return _stop(
        stopped_reason,
        chain,
        scan_root=scan_root,
        depth=selected_depth,
        token_budget=selected_budget,
        path=relative_path(start_path, scan_root),
        anchor=anchor,
        token_total=total_tokens,
        links_followed=max(0, len(chain) - 1),
        skipped_bare_wikilinks=skipped_bare_total,
        detail=stop_detail,
        exit_code=1 if not chain else 0,
    )


def _resolve_start_path(value: str, scan_root: Path) -> Path | None:
    raw = Path(value).expanduser()
    candidates = [raw] if raw.is_absolute() else [Path.cwd() / raw, scan_root / raw]
    for candidate in _with_markdown_suffixes(candidates):
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def _with_markdown_suffixes(candidates: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for candidate in candidates:
        expanded.append(candidate)
        if candidate.suffix.lower() not in {".md", ".mdx"}:
            expanded.extend([candidate.with_suffix(".md"), candidate.with_suffix(".mdx")])
    return expanded


def _first_anchored_wikilink(text: str) -> dict[str, Any]:
    skipped_bare = 0
    for target, anchor in wikilinks_with_anchors_from_text(text):
        if anchor:
            return {"target": target, "anchor": anchor, "skipped_bare": skipped_bare}
        skipped_bare += 1
    return {"target": None, "anchor": None, "skipped_bare": skipped_bare}


def _resolve_target_with_collision_check(
    target: str,
    source_path: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]],
) -> dict[str, Any]:
    if target == "":
        return {"status": "ok", "path": source_path.resolve()}

    clean = split_link_target(target)
    if not clean:
        return {"status": "target_not_found"}
    lowered = clean.lower()
    if "://" in lowered or lowered.startswith(("mailto:", "tel:", "data:")):
        return {"status": "target_not_found"}

    raw_path = Path(clean).expanduser()
    direct_candidates = [raw_path] if raw_path.is_absolute() else [source_path.parent / raw_path, scan_root / raw_path]
    existing = _dedupe_paths(
        candidate.resolve()
        for candidate in _with_markdown_suffixes(direct_candidates)
        if candidate.exists() and candidate.is_file()
    )
    if len(existing) == 1:
        return {"status": "ok", "path": existing[0]}
    if len(existing) > 1:
        return {
            "status": "ambiguous_target",
            "candidates": [relative_path(path, scan_root) for path in existing],
        }

    keys = [lowered]
    if not lowered.endswith((".md", ".mdx")):
        keys.extend([f"{lowered}.md", f"{lowered}.mdx"])
    matches = _dedupe_paths(path.resolve() for key in keys for path in lookup.get(key, []))
    if len(matches) == 1:
        return {"status": "ok", "path": matches[0]}
    if len(matches) > 1:
        return {
            "status": "ambiguous_target",
            "candidates": [relative_path(path, scan_root) for path in matches],
        }
    return {"status": "target_not_found"}


def _dedupe_paths(paths: Any) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = Path(path).resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def _normalize_anchor(anchor: str) -> str:
    return "".join(anchor.lower().split())


def _stop(
    reason: str,
    chain: list[dict[str, Any]],
    *,
    scan_root: Path,
    depth: int,
    token_budget: int,
    path: str,
    anchor: str,
    token_total: int = 0,
    links_followed: int = 0,
    skipped_bare_wikilinks: int = 0,
    detail: dict[str, Any] | None = None,
    exit_code: int = 0,
) -> dict[str, Any]:
    payload = {
        "command": "walk",
        "path": path,
        "anchor": anchor,
        "scan_root": str(scan_root),
        "depth": depth,
        "token_budget": token_budget,
        "chain": chain,
        "text": _join_chain(chain),
        "stats": {
            "stopped_reason": reason,
            "blocks": len(chain),
            "links_followed": links_followed,
            "token_total": token_total,
            "skipped_bare_wikilinks": skipped_bare_wikilinks,
            **(detail or {}),
        },
    }
    if exit_code:
        payload["_exit_code"] = exit_code
    return payload


def _join_chain(chain: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for item in chain:
        blocks.append(
            "\n".join(
                [
                    f"<!-- md-walk step={item['step']} path=\"{item['path']}\" anchor=\"{item['anchor']}\" -->",
                    str(item["content"]),
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)
