#!/usr/bin/env python3
"""Idempotently wire a shipped 1html add-on into every current live page."""

from __future__ import annotations

import argparse
import posixpath
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from audit_html_style import HTML_VOID_ELEMENTS, live_page_topology

ADDON_RESOURCES = {
    "table": {"assets/artifact-table.js"},
    "mermaid": {
        "assets/diagram-viewer.css",
        "lib/mermaid.min.js",
        "lib/mermaid-layout-elk.iife.min.js",
        "lib/panzoom.min.js",
        "assets/diagram-viewer.js",
        "assets/mermaid-init.js",
    },
    "react-flow": {
        "lib/react-flow.css",
        "assets/react-flow-theme.css",
        "lib/react-flow.vendor.js",
        "assets/react-flow-init.js",
    },
    "echarts": {"lib/echarts.min.js", "assets/echarts-init.js"},
}


@dataclass
class TagSpan:
    """One parsed start tag and, when present, its matching end tag."""

    tag: str
    attrs: dict[str, str]
    start: int
    start_end: int
    end_start: int | None = None
    end: int | None = None


class SourceHTMLParser(HTMLParser):
    """Map real HTML tags to source spans without serializing the document."""

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_offsets = [0]
        self.line_offsets.extend(
            index + 1 for index, character in enumerate(source) if character == "\n"
        )
        self.tags: list[TagSpan] = []
        self.open_tags: list[int] = []
        self.closing_tags: dict[str, list[int]] = {}
        self.feed(source)
        self.close()

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        start = self.source_offset()
        raw = self.get_starttag_text()
        span = TagSpan(
            normalized,
            {name.lower(): value or "" for name, value in attrs},
            start,
            start + len(raw),
        )
        self.tags.append(span)
        if normalized not in HTML_VOID_ELEMENTS:
            self.open_tags.append(len(self.tags) - 1)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        normalized = tag.lower()
        if normalized not in HTML_VOID_ELEMENTS:
            self.open_tags.pop()

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        start = self.source_offset()
        end = self.source.find(">", start)
        end = len(self.source) if end < 0 else end + 1
        self.closing_tags.setdefault(normalized, []).append(start)
        for stack_index in range(len(self.open_tags) - 1, -1, -1):
            tag_index = self.open_tags[stack_index]
            if self.tags[tag_index].tag != normalized:
                continue
            span = self.tags[tag_index]
            span.end_start = start
            span.end = end
            del self.open_tags[stack_index:]
            return

    def closing_position(self, tag: str) -> int:
        positions = self.closing_tags.get(tag, [])
        if not positions:
            raise ValueError(f"expected real closing </{tag}> before add-on wiring")
        return positions[0]


def normalized_local_path(value: str) -> str | None:
    stripped = value.split("#", 1)[0].split("?", 1)[0].strip()
    if not stripped or "://" in stripped or stripped.startswith(("//", "/")):
        return None
    return posixpath.normpath(stripped)


def matching_resource_tag(
    document: SourceHTMLParser,
    *,
    tag: str,
    attribute: str,
    value: str,
) -> TagSpan | None:
    expected = normalized_local_path(value)
    return next(
        (
            span
            for span in document.tags
            if span.tag == tag
            and normalized_local_path(span.attrs.get(attribute, "")) == expected
        ),
        None,
    )


def remove_existing_addon_tags(source: str, addon: str, prefix: str) -> str:
    document = SourceHTMLParser(source)
    removals: list[tuple[int, int]] = []
    canonical_paths = {
        normalized_local_path(f"{prefix}{path}") for path in ADDON_RESOURCES[addon]
    }
    for span in document.tags:
        attribute = (
            "href" if span.tag == "link" else "src" if span.tag == "script" else ""
        )
        if not attribute:
            continue
        if normalized_local_path(span.attrs.get(attribute, "")) not in canonical_paths:
            continue
        end = (
            span.end
            if span.tag == "script" and span.end is not None
            else span.start_end
        )
        line_start = source.rfind("\n", 0, span.start) + 1
        line_end = source.find("\n", end)
        line_end = len(source) if line_end < 0 else line_end + 1
        if (
            not source[line_start : span.start].strip()
            and not source[end:line_end].strip()
        ):
            removals.append((line_start, line_end))
        else:
            removals.append((span.start, end))
    for start, end in sorted(removals, reverse=True):
        source = source[:start] + source[end:]
    return source


def page_uses_addon(source: str, addon: str) -> bool:
    attribute = {
        "react-flow": "data-react-flow",
        "echarts": "data-echart",
    }.get(addon)
    if attribute is None:
        return True
    return any(attribute in span.attrs for span in SourceHTMLParser(source).tags)


def insert_tags(source: str, position: int, tags: tuple[str, ...]) -> str:
    """Insert tags at an exact parsed span, retaining surrounding source bytes."""

    line_start = source.rfind("\n", 0, position) + 1
    line_prefix = source[line_start:position]
    if line_prefix.strip():
        content = "\n  " + "\n  ".join(tags) + "\n  "
    else:
        content = ("\n" + line_prefix).join(tags) + "\n" + line_prefix
    return source[:position] + content + source[position:]


def wire_page(page: Path, root: Path, addon: str) -> str:
    source = page.read_text(encoding="utf-8")
    prefix = "../" if page.parent == root / "pages" else ""
    source = remove_existing_addon_tags(source, addon, prefix)
    if not page_uses_addon(source, addon):
        return source

    document = SourceHTMLParser(source)
    head_close = document.closing_position("head")
    body_close = document.closing_position("body")
    alpine = matching_resource_tag(
        document,
        tag="script",
        attribute="src",
        value=f"{prefix}lib/alpine.js",
    )
    if addon == "table" and alpine is None:
        raise ValueError(f"{page}: expected local alpine.js before add-on wiring")

    if addon == "table":
        assert alpine is not None
        return insert_tags(
            source,
            alpine.start,
            (f'<script defer src="{prefix}assets/artifact-table.js"></script>',),
        )

    local_css = matching_resource_tag(
        document,
        tag="link",
        attribute="href",
        value=f"{prefix}assets/local.css",
    )
    if addon == "react-flow":
        stylesheets = (
            f'<link href="{prefix}lib/react-flow.css" rel="stylesheet">',
            f'<link href="{prefix}assets/react-flow-theme.css" rel="stylesheet">',
        )
        source = insert_tags(
            source,
            local_css.start if local_css is not None else head_close,
            stylesheets,
        )
        document = SourceHTMLParser(source)
        alpine = matching_resource_tag(
            document,
            tag="script",
            attribute="src",
            value=f"{prefix}lib/alpine.js",
        )
        scripts = (
            f'<script defer src="{prefix}lib/react-flow.vendor.js"></script>',
            f'<script defer src="{prefix}assets/react-flow-init.js"></script>',
        )
        position = (
            alpine.start if alpine is not None else document.closing_position("body")
        )
        return insert_tags(source, position, scripts)

    if addon == "echarts":
        scripts = (
            f'<script defer src="{prefix}lib/echarts.min.js"></script>',
            f'<script defer src="{prefix}assets/echarts-init.js"></script>',
        )
        position = alpine.start if alpine is not None else body_close
        return insert_tags(source, position, scripts)

    stylesheet = (f'<link href="{prefix}assets/diagram-viewer.css" rel="stylesheet">',)
    source = insert_tags(
        source,
        local_css.start if local_css is not None else head_close,
        stylesheet,
    )
    document = SourceHTMLParser(source)
    alpine = matching_resource_tag(
        document,
        tag="script",
        attribute="src",
        value=f"{prefix}lib/alpine.js",
    )
    scripts = tuple(
        f'<script defer src="{prefix}{path}"></script>'
        for path in (
            "lib/mermaid.min.js",
            "lib/mermaid-layout-elk.iife.min.js",
            "lib/panzoom.min.js",
            "assets/diagram-viewer.js",
            "assets/mermaid-init.js",
        )
    )
    position = alpine.start if alpine is not None else document.closing_position("body")
    return insert_tags(source, position, scripts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("check", "apply"))
    parser.add_argument("addon", choices=("table", "mermaid", "react-flow", "echarts"))
    parser.add_argument("artifact_directory", type=Path)
    arguments = parser.parse_args()

    root = arguments.artifact_directory.expanduser().resolve()
    if not (root / "index.html").is_file():
        print(f"artifact index not found: {root / 'index.html'}", file=sys.stderr)
        return 1
    pages, violations = live_page_topology(root)
    if violations:
        for violation in violations:
            print(
                f"{violation.path}:{violation.line}: {violation.message}",
                file=sys.stderr,
            )
        return 1

    try:
        active_pages = sum(
            page_uses_addon(page.read_text(encoding="utf-8"), arguments.addon)
            for page in pages
        )
        planned = [(page, wire_page(page, root, arguments.addon)) for page in pages]
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if arguments.mode == "apply":
        for page, source in planned:
            page.write_text(source, encoding="utf-8")
    if arguments.addon in {"react-flow", "echarts"} and active_pages == 0:
        marker = "data-react-flow" if arguments.addon == "react-flow" else "data-echart"
        print(f"no page contains a {marker} host", file=sys.stderr)
        return 1
    print(f"pages={active_pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
