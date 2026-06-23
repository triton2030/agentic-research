from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from .markdown_io import (
    WIKILINK_RE,
    approx_tokens,
    extract_section_by_anchor,
    markdown_lookup,
    relative_path,
    split_link_target,
    strip_frontmatter_text,
)
from .walk import _resolve_start_path, _resolve_target_with_collision_check


DEFAULT_DEPTH = 2
DEFAULT_TOKEN_BUDGET = 6000


def coherence_audit(
    path: str,
    *,
    anchor: str | None = None,
    scan: str | None = None,
    depth: int | None = None,
    token_budget: int | None = None,
) -> dict[str, Any]:
    scan_root = Path(scan or ".").expanduser().resolve()
    selected_depth = max(0, int(depth if depth is not None else DEFAULT_DEPTH))
    selected_budget = int(token_budget if token_budget is not None else DEFAULT_TOKEN_BUDGET)
    start_path = _resolve_start_path(path, scan_root)

    if not scan_root.exists():
        return _error(
            "scan_root_not_found",
            path=path,
            anchor=anchor,
            scan_root=scan_root,
            depth=selected_depth,
            token_budget=selected_budget,
        )
    if start_path is None:
        return _error(
            "path_not_found",
            path=path,
            anchor=anchor,
            scan_root=scan_root,
            depth=selected_depth,
            token_budget=selected_budget,
        )

    source_text = _read_source_text(start_path, anchor)
    if source_text is None:
        return _error(
            "anchor_not_found",
            path=relative_path(start_path, scan_root),
            anchor=anchor,
            scan_root=scan_root,
            depth=selected_depth,
            token_budget=selected_budget,
        )

    lookup = markdown_lookup(scan_root)
    state: dict[str, Any] = {
        "blocks": [],
        "issues": [],
        "wikilinks_seen": 0,
        "blocks_expanded": 0,
        "skipped_bare_wikilinks": 0,
        "unresolved_wikilinks": 0,
        "token_total": approx_tokens(source_text),
        "token_budget_exhausted": False,
    }
    expanded = _expand_text(
        source_text,
        source_path=start_path,
        scan_root=scan_root,
        lookup=lookup,
        depth_remaining=selected_depth,
        token_budget=selected_budget,
        state=state,
        stack=[],
    )
    source_rel = relative_path(start_path, scan_root)
    text = "\n".join(
        [
            f'<!-- md-coherence-audit source path="{source_rel}" anchor="{anchor or ""}" -->',
            expanded,
        ]
    )
    payload = {
        "command": "coherence-audit",
        "path": source_rel,
        "anchor": anchor,
        "scan_root": str(scan_root),
        "depth": selected_depth,
        "token_budget": selected_budget,
        "source": {
            "path": source_rel,
            "anchor": anchor,
            "content": source_text,
            "tokens": approx_tokens(source_text),
        },
        "blocks": state["blocks"],
        "issues": state["issues"],
        "text": text,
        "stats": {
            "wikilinks_seen": state["wikilinks_seen"],
            "blocks_expanded": state["blocks_expanded"],
            "skipped_bare_wikilinks": state["skipped_bare_wikilinks"],
            "unresolved_wikilinks": state["unresolved_wikilinks"],
            "token_total": state["token_total"],
            "token_budget_exhausted": state["token_budget_exhausted"],
        },
    }
    if state["issues"]:
        payload["_exit_code"] = 1
    return payload


def _expand_text(
    text: str,
    *,
    source_path: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]],
    depth_remaining: int,
    token_budget: int,
    state: dict[str, Any],
    stack: list[tuple[Path, str]],
) -> str:
    if depth_remaining <= 0:
        return text

    parts: list[str] = []
    cursor = 0
    for ref in _iter_wikilinks(text):
        parts.append(text[cursor : ref["start"]])
        cursor = ref["end"]
        trailing = ""
        if cursor < len(text) and text[cursor] in ".,;:!?…":
            trailing = text[cursor]
            cursor += 1
        state["wikilinks_seen"] += 1

        raw_link = str(ref["raw"])
        target = str(ref["target"])
        link_anchor = ref["anchor"]
        if not link_anchor:
            state["skipped_bare_wikilinks"] += 1
            parts.append(raw_link + trailing)
            continue

        resolved = _resolve_target_with_collision_check(target, source_path, scan_root, lookup)
        if resolved["status"] != "ok":
            state["unresolved_wikilinks"] += 1
            state["issues"].append(
                {
                    "code": resolved["status"],
                    "link": raw_link,
                    "source_path": relative_path(source_path, scan_root),
                    "anchor": link_anchor,
                    "candidates": resolved.get("candidates", []),
                }
            )
            parts.append(raw_link + trailing)
            continue

        target_path = resolved["path"]
        target_key = (target_path.resolve(), _normalize_anchor(str(link_anchor)))
        if target_key in stack:
            state["issues"].append(
                {
                    "code": "cycle",
                    "link": raw_link,
                    "source_path": relative_path(source_path, scan_root),
                    "target_path": relative_path(target_path, scan_root),
                    "anchor": link_anchor,
                }
            )
            parts.append(raw_link + trailing)
            continue

        body = extract_section_by_anchor(target_path, str(link_anchor))
        if body is None:
            state["unresolved_wikilinks"] += 1
            state["issues"].append(
                {
                    "code": "anchor_not_found",
                    "link": raw_link,
                    "source_path": relative_path(source_path, scan_root),
                    "target_path": relative_path(target_path, scan_root),
                    "anchor": link_anchor,
                }
            )
            parts.append(raw_link + trailing)
            continue

        tokens = approx_tokens(body)
        if token_budget > 0 and state["token_total"] + tokens > token_budget:
            state["token_budget_exhausted"] = True
            state["issues"].append(
                {
                    "code": "token_budget",
                    "link": raw_link,
                    "source_path": relative_path(source_path, scan_root),
                    "target_path": relative_path(target_path, scan_root),
                    "anchor": link_anchor,
                    "tokens": tokens,
                }
            )
            parts.append(raw_link + trailing)
            continue

        state["token_total"] += tokens
        occurrence = len(state["blocks"])
        target_rel = relative_path(target_path, scan_root)
        state["blocks"].append(
            {
                "occurrence": occurrence,
                "depth": len(stack) + 1,
                "link": raw_link,
                "source_path": relative_path(source_path, scan_root),
                "target_path": target_rel,
                "anchor": link_anchor,
                "content": body,
                "tokens": tokens,
            }
        )
        state["blocks_expanded"] += 1
        nested = _expand_text(
            body,
            source_path=target_path,
            scan_root=scan_root,
            lookup=lookup,
            depth_remaining=depth_remaining - 1,
            token_budget=token_budget,
            state=state,
            stack=[*stack, target_key],
        )
        parts.append(raw_link + trailing)
        parts.append(
            "\n\n"
            + f'<!-- md-coherence-audit link={occurrence} target="{target_rel}" anchor="{link_anchor}" -->\n'
            + nested
            + f"\n<!-- /md-coherence-audit link={occurrence} -->\n"
            + f"\n*⤴ {link_anchor}*\n\n---\n\n"
        )

    parts.append(text[cursor:])
    return "".join(parts)


def _iter_wikilinks(text: str) -> Iterator[dict[str, Any]]:
    for match in WIKILINK_RE.finditer(text):
        raw = match.group(0)
        inner = match.group(1)
        if not inner:
            continue
        target = inner.split("|", 1)[0].strip().strip("<>").strip()
        if not target:
            continue
        if "#" in target:
            path_part, anchor_part = target.split("#", 1)
            path_clean = split_link_target(path_part)
            anchor_clean = anchor_part.split("?", 1)[0].strip()
            if path_clean or anchor_clean:
                yield {
                    "raw": raw,
                    "target": path_clean,
                    "anchor": anchor_clean or None,
                    "start": match.start(),
                    "end": match.end(),
                }
        else:
            path_clean = split_link_target(target)
            if path_clean:
                yield {
                    "raw": raw,
                    "target": path_clean,
                    "anchor": None,
                    "start": match.start(),
                    "end": match.end(),
                }


def _read_source_text(path: Path, anchor: str | None) -> str | None:
    if anchor:
        return extract_section_by_anchor(path, anchor)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return strip_frontmatter_text(text).strip()


def _normalize_anchor(value: str) -> str:
    return "".join(value.lower().split())


def _error(
    code: str,
    *,
    path: str,
    anchor: str | None,
    scan_root: Path,
    depth: int,
    token_budget: int,
) -> dict[str, Any]:
    return {
        "command": "coherence-audit",
        "path": path,
        "anchor": anchor,
        "scan_root": str(scan_root),
        "depth": depth,
        "token_budget": token_budget,
        "source": None,
        "blocks": [],
        "issues": [{"code": code, "path": path, "anchor": anchor}],
        "text": "",
        "stats": {
            "wikilinks_seen": 0,
            "blocks_expanded": 0,
            "skipped_bare_wikilinks": 0,
            "unresolved_wikilinks": 0,
            "token_total": 0,
            "token_budget_exhausted": False,
        },
        "_exit_code": 2,
    }
