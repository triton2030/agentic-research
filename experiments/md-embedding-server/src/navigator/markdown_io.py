from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - fallback keeps the script dependency-light.
    yaml = None


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
WIKILINK_RE = re.compile(r"!\[\[[^\]]+\]\]|\[\[([^\]]+)\]\]")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
GRAPH_LINK_KEYS = ("read-before-edit", "edit-after-edit")

# Walked-past path parts. These contain either (a) tooling state that holds a
# full copy of the corpus (claude-code worktrees, codex worktrees), or (b)
# generated / vendored artefacts that double indexing cost without adding
# useful retrieval signal. Hidden / dotted dirs are skipped by default — if
# you really want to index `.docs` or similar, point `iter_markdown` directly
# at it.
DEFAULT_EXCLUDED_PARTS = frozenset(
    {
        ".git",
        ".github",
        ".claude",
        ".codex",
        ".md-navigator",
        ".cache",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".next",
        ".nuxt",
        "dist",
        "build",
        "out",
        "target",
        "_archive",
        # Auto-generated execution logs: `experiments/*/runs/<timestamp>/`
        # carries claude-bridge / gemini-mcp / similar live-output dumps.
        # Strong-multilingual embedding models surface boilerplate phrases
        # from these files as top retrieval hits (e.g. "Reading context and
        # preparing response"), drowning canonical knowledge. Treat as
        # build artefacts — not knowledge content.
        "runs",
    }
)


def iter_markdown(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in {".md", ".mdx"} else []
    if not path.exists():
        raise SystemExit(f"Path does not exist: {path}")
    root = path.resolve()
    # Heads-up: if the target itself sits in (or under) a default-excluded
    # folder, the disjoint filter below silently drops every result and the
    # user gets `Files: 0` with no clue why. Warn once to stderr so the
    # exclusion is visible without changing the contract or polluting stdout
    # (downstream JSON parsers stay clean).
    try:
        resolved_parts = path.resolve().parts
    except (OSError, RuntimeError):
        resolved_parts = path.parts
    excluded_in_target = DEFAULT_EXCLUDED_PARTS.intersection(resolved_parts)
    if excluded_in_target:
        import sys

        sys.stderr.write(
            f"[md_navigator] note: target path contains default-excluded "
            f"part(s) {sorted(excluded_in_target)} — every Markdown file "
            f"under this path will be skipped, so results will be empty. "
            f"To work with this folder anyway, point md_navigator at a "
            f"specific file inside it, or rename / move it out of the "
            f"excluded set. Default exclusions: "
            f"{sorted(DEFAULT_EXCLUDED_PARTS)}\n"
        )
    files: list[Path] = []
    for p in path.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md", ".mdx"}:
            continue
        try:
            resolved = p.resolve()
        except (OSError, RuntimeError):
            continue
        try:
            resolved.relative_to(root)
        except ValueError:
            # Avoid indexing symlink targets outside the selected corpus root.
            # This keeps broad scans such as `/tmp` from walking visible skill
            # mirrors that point back into `~/.codex` / `~/.claude`.
            continue
        if not DEFAULT_EXCLUDED_PARTS.isdisjoint(p.parts):
            continue
        if not DEFAULT_EXCLUDED_PARTS.isdisjoint(resolved.parts):
            continue
        files.append(p)
    return sorted(files)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def normalize_frontmatter_links(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        out: list[str] = []
        for item in value:
            out.extend(normalize_frontmatter_links(item))
        return out
    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw == "[]":
            return []
        if raw.startswith("[") and raw.endswith("]") and not (
            raw.startswith("[[") and raw.endswith("]]")
        ):
            raw = raw[1:-1]
            return [strip_quotes(part.strip()) for part in raw.split(",") if part.strip()]
        return [strip_quotes(raw)]
    return [str(value).strip()]


def parse_frontmatter(lines: list[str]) -> dict[str, Any]:
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        frontmatter_lines.append(line)

    if yaml is not None:
        try:
            parsed = yaml.safe_load("\n".join(frontmatter_lines)) or {}
        except yaml.YAMLError:
            parsed = None
        if parsed is not None:
            data: dict[str, Any] = {}
            if isinstance(parsed, dict):
                data.update(parsed)
                if "description" in data:
                    data["description"] = str(data.get("description") or "").strip()
                for key in GRAPH_LINK_KEYS:
                    if key in parsed:
                        data[key] = normalize_frontmatter_links(parsed.get(key))
            return data
        # YAML parser tripped (e.g. unquoted colon inside folded scalar);
        # fall through to the line-based fallback below.

    data: dict[str, Any] = {}
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        if ":" not in line:
            index += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        marker = raw.strip()
        if key == "description":
            if marker in {">", "|", ">-", "|-"}:
                folded: list[str] = []
                index += 1
                while index < len(frontmatter_lines):
                    next_line = frontmatter_lines[index]
                    if next_line and not next_line.startswith((" ", "\t")):
                        break
                    folded.append(next_line.strip())
                    index += 1
                data[key] = " ".join(part for part in folded if part)
                continue
            data[key] = strip_quotes(raw)
        elif key in GRAPH_LINK_KEYS:
            if not marker:
                links: list[str] = []
                index += 1
                while index < len(frontmatter_lines):
                    next_line = frontmatter_lines[index]
                    stripped = next_line.strip()
                    if next_line and not next_line.startswith((" ", "\t")):
                        break
                    if stripped.startswith("- "):
                        links.append(strip_quotes(stripped[2:]))
                    index += 1
                data[key] = [link for link in links if link]
                continue
            data[key] = normalize_frontmatter_links(marker)
        else:
            if marker in {">", "|", ">-", "|-"}:
                folded = []
                index += 1
                while index < len(frontmatter_lines):
                    next_line = frontmatter_lines[index]
                    if next_line and not next_line.startswith((" ", "\t")):
                        break
                    folded.append(next_line.strip())
                    index += 1
                data[key] = " ".join(part for part in folded if part)
                continue
            if not marker:
                items: list[str] = []
                index += 1
                while index < len(frontmatter_lines):
                    next_line = frontmatter_lines[index]
                    stripped = next_line.strip()
                    if next_line and not next_line.startswith((" ", "\t")):
                        break
                    if stripped.startswith("- "):
                        items.append(strip_quotes(stripped[2:]))
                    index += 1
                data[key] = items
                continue
            data[key] = strip_quotes(marker)
        index += 1
    return data


def collect_headings(lines: list[str], max_level: int) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    in_fence = False
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line.rstrip())
        if not match:
            continue
        level = len(match.group(1))
        if level > max_level:
            continue
        headings.append(
            {
                "line": line_no,
                "level": level,
                "text": match.group(2).strip(),
            }
        )
    return headings


def approx_tokens(text: str) -> int:
    # Char-based approximation. ~4 chars/token is the standard rough estimate
    # for mixed Latin/Cyrillic prose; precise enough for navigation budgeting.
    if not text:
        return 0
    return max(1, len(text) // 4)


def section_token_count(lines: list[str], start_line: int, level: int) -> int:
    start_index = start_line - 1
    if start_index < 0 or start_index >= len(lines):
        return 0
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
    return approx_tokens("\n".join(lines[start_index:end_index]))


def split_link_target(target: str) -> str:
    target = target.strip().strip("<>").strip()
    if not target:
        return ""
    if " " in target and not Path(target.split(" ", 1)[0]).exists():
        target = target.split(" ", 1)[0]
    return target.split("#", 1)[0].split("?", 1)[0].strip()


def wikilinks_from_text(text: str) -> list[str]:
    targets: list[str] = []
    for match in WIKILINK_RE.finditer(text):
        raw = match.group(1)
        if not raw:
            continue
        target = raw.split("|", 1)[0].strip()
        target = split_link_target(target)
        if target:
            targets.append(target)
    return targets


def wikilinks_with_anchors_from_text(text: str) -> list[tuple[str, str | None]]:
    """Same as wikilinks_from_text but preserves the `#anchor` part.

    Returns (target_path, anchor_or_None) tuples. `[[file#Heading Name]]`
    becomes ("file", "Heading Name"); `[[#Heading Name]]` becomes
    ("", "Heading Name"); plain `[[file]]` becomes ("file", None).
    """
    results: list[tuple[str, str | None]] = []
    for match in WIKILINK_RE.finditer(text):
        raw = match.group(1)
        if not raw:
            continue
        target = raw.split("|", 1)[0].strip().strip("<>").strip()
        if not target:
            continue
        if "#" in target:
            path_part, anchor_part = target.split("#", 1)
            path_clean = split_link_target(path_part)
            anchor_clean = anchor_part.split("?", 1)[0].strip()
            if path_clean or anchor_clean:
                results.append((path_clean, anchor_clean or None))
        else:
            path_clean = split_link_target(target)
            if path_clean:
                results.append((path_clean, None))
    return results


def markdown_links_from_text(text: str) -> list[str]:
    targets: list[str] = []
    for raw in MD_LINK_RE.findall(text):
        target = split_link_target(raw)
        if not target:
            continue
        lowered = target.lower()
        if (
            "://" in lowered
            or lowered.startswith(("mailto:", "tel:", "data:"))
            or lowered.startswith("#")
        ):
            continue
        targets.append(target)
    return targets


def markdown_links_with_anchors_from_text(text: str) -> list[tuple[str, str | None]]:
    """Same as markdown_links_from_text but preserves the `#anchor` part."""
    results: list[tuple[str, str | None]] = []
    for raw in MD_LINK_RE.findall(text):
        raw_stripped = raw.strip().strip("<>").strip()
        if not raw_stripped:
            continue
        if " " in raw_stripped and not Path(raw_stripped.split(" ", 1)[0]).exists():
            raw_stripped = raw_stripped.split(" ", 1)[0]
        lowered = raw_stripped.lower()
        if (
            "://" in lowered
            or lowered.startswith(("mailto:", "tel:", "data:"))
            or lowered.startswith("#")
        ):
            continue
        if "#" in raw_stripped:
            path_part, anchor_part = raw_stripped.split("#", 1)
            path_clean = path_part.split("?", 1)[0].strip()
            anchor_clean = anchor_part.split("?", 1)[0].strip()
            if path_clean:
                results.append((path_clean, anchor_clean or None))
        else:
            path_clean = raw_stripped.split("?", 1)[0].strip()
            if path_clean:
                results.append((path_clean, None))
    return results


def extract_section_by_anchor(file_path: Path, anchor: str) -> str | None:
    """Extract a single heading-bounded section from a file by heading text.

    Matches anchor against heading text case-insensitively with whitespace
    normalized — Obsidian/Markdown wikilink convention `[[file#Heading]]`.
    Returns the section body (from the heading line through the next
    sibling-or-higher heading) or None when no heading matches.
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = text.splitlines()
    headings = collect_headings(lines, max_level=6)
    normalized_anchor = "".join(anchor.lower().split())
    for heading in headings:
        normalized_heading = "".join(heading["text"].lower().split())
        if normalized_anchor == normalized_heading:
            from .pick import section_lines
            return section_lines(file_path, heading["line"])
    return None


def markdown_lookup(root: Path) -> dict[str, list[Path]]:
    lookup: dict[str, list[Path]] = {}
    for path in iter_markdown(root):
        resolved = path.resolve()
        keys = {
            path.name.lower(),
            path.stem.lower(),
            str(resolved).lower(),
        }
        try:
            keys.add(str(resolved.relative_to(root.resolve())).lower())
        except ValueError:
            pass
        for key in keys:
            lookup.setdefault(key, []).append(resolved)
    return lookup


def resolve_markdown_target(
    target: str,
    source_path: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]],
) -> Path | None:
    clean = split_link_target(target)
    if not clean:
        return None
    lowered = clean.lower()
    if "://" in lowered or lowered.startswith(("mailto:", "tel:", "data:")):
        return None

    raw_path = Path(clean).expanduser()
    candidates: list[Path] = []
    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.extend([source_path.parent / raw_path, scan_root / raw_path])

    expanded: list[Path] = []
    for candidate in candidates:
        expanded.append(candidate)
        if candidate.suffix.lower() not in {".md", ".mdx"}:
            expanded.extend([candidate.with_suffix(".md"), candidate.with_suffix(".mdx")])

    for candidate in expanded:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    keys = [clean.lower()]
    if not lowered.endswith((".md", ".mdx")):
        keys.append(f"{lowered}.md")
        keys.append(f"{lowered}.mdx")
    for key in keys:
        paths = lookup.get(key)
        if paths:
            return paths[0]
    return None


def resolve_input_path(value: str, scan_root: Path) -> Path:
    raw = Path(value).expanduser()
    candidates = [raw] if raw.is_absolute() else [Path.cwd() / raw, scan_root / raw]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    raise SystemExit(f"Markdown file does not exist: {value}")


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())
