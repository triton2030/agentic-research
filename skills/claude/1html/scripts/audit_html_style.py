#!/usr/bin/env python3
"""Audit one HTML artifact and enforce its portable bundle contract."""

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

EXCLUDED_DIRS = {"_catalog", ".git", "lib", "node_modules", "sources"}
HTML_VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
ACTION_INPUT_TYPES = {"button", "reset", "submit"}
DAISY_ACTION_ROOTS = {
    "btn",
    "collapse-title",
    "link",
    "modal-backdrop",
    "swap",
    "tab",
}
DAISY_COMPONENTS = {
    "alert",
    "badge",
    "btn",
    "card",
    "checkbox",
    "collapse",
    "drawer",
    "dropdown",
    "hero",
    "input",
    "join",
    "list",
    "loading",
    "menu",
    "modal",
    "navbar",
    "radio",
    "select",
    "stats",
    "steps",
    "tab",
    "table",
    "textarea",
    "timeline",
    "toggle",
    "tooltip",
}
CATEGORY_ORDER = (
    "LIKELY_REINVENTION",
    "DAISY_OVERRIDE",
    "CONTRAST_RISK",
    "STYLE_LITERAL",
)
MAX_VISIBLE_FINDINGS = 40
SEMANTIC_ROLES = (
    "primary",
    "secondary",
    "accent",
    "neutral",
    "info",
    "success",
    "warning",
    "error",
)

ARBITRARY_SPACING_RE = re.compile(
    r"(?:^|:)(?:gap(?:-[xy])?|space-[xy]|p[trblxy]?|m[trblxy]?|"
    r"rounded(?:-[trbl]{1,2})?)-\[[^\]]+\]$"
)
ARBITRARY_COLOR_RE = re.compile(
    r"(?:^|:)(?:bg|text|border|ring|fill|stroke)-\[[^\]]+\]$"
)
HARDCODED_COLOR_RE = re.compile(
    r"(?:^|:)(?:bg|text|border|ring|fill|stroke)-"
    r"(?:(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|"
    r"green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|"
    r"pink|rose)-\d{2,3}(?:/\d+)?|black|white)$"
)
BUTTON_OVERRIDE_RE = re.compile(
    r"(?:^|:)(?:bg|text|border|ring|rounded(?:-[trbl]{1,2})?|shadow|"
    r"p[trblxy]?|h|min-h|max-h)-"
)
RAW_COLOR_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|(?:rgb|hsl|oklch)a?\s*\("
)
LITERAL_SPACING_RE = re.compile(
    r"\b(?:gap|row-gap|column-gap|padding(?:-(?:block|inline|top|right|"
    r"bottom|left))?|margin(?:-(?:block|inline|top|right|bottom|left))?|"
    r"border-radius)\s*:\s*(?!var\s*\()"
)
CUSTOM_TOKEN_RE = re.compile(r"(--[a-zA-Z][a-zA-Z0-9_-]*)\s*:")
CUSTOM_BUTTON_SELECTOR_RE = re.compile(
    r"(?<![\w-])\.(?:button|cta|action-button|icon-button)(?![\w-])"
)
DAISY_SELECTOR_RE = re.compile(
    r"(?<![\w-])\.(" + "|".join(sorted(DAISY_COMPONENTS)) + r")(?![\w-])"
)
GLOBAL_ANCHOR_COLOR_RE = re.compile(
    r"(?ms)(?:^|})\s*a\s*\{(?P<body>[^{}]*\bcolor\s*:[^{}]+)\}"
)
THEME_TOKEN_RE = re.compile(
    r"(--color-[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;"
)
CLASS_ATTRIBUTE_RE = re.compile(r"""class\s*=\s*["']([^"']+)["']""")
KNOWN_PLACEHOLDER_MARKERS = (
    "Название HTML-артефакта",
    "Заголовок-ответ страницы",
    "HTML draft bundle",
)
BUNDLE_MARKER = ".1html-bundle-version"
LEGACY_RESOURCE_ATTRIBUTES = {
    "a": ("href",),
    "audio": ("src",),
    "img": ("src", "srcset"),
    "link": ("href",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "video": ("src", "poster"),
}
RESOURCE_ATTRIBUTES = {
    **LEGACY_RESOURCE_ATTRIBUTES,
    "embed": ("src",),
    "iframe": ("src",),
    "input": ("src",),
    "object": ("data",),
    "track": ("src",),
}


@dataclass(frozen=True)
class Finding:
    category: str
    path: Path
    line: int
    message: str
    evidence: str


@dataclass(frozen=True)
class BundleViolation:
    path: Path
    line: int
    code: str
    message: str


@dataclass
class BundleFrame:
    tag: str
    line: int
    in_main: bool
    tablist_id: int | None
    inline_script: bool
    json_script_id: str | None
    inline_style_index: int | None
    inline_script_index: int | None
    element_id: str | None
    daisy_required_part: str | None
    daisy_part_found: bool
    daisy_unwrapped_content: bool


@dataclass(frozen=True)
class ResourceReference:
    tag: str
    attribute: str
    value: str
    line: int


def srcset_candidates(value: str) -> list[str]:
    stripped = value.strip()
    if stripped.startswith("data:"):
        return [stripped.split()[0]]
    return [
        candidate.strip().split()[0]
        for candidate in value.split(",")
        if candidate.strip()
    ]


class BundleHTMLParser(HTMLParser):
    """Collect the source invariants owned by the shipped 1html bundle."""

    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack: list[BundleFrame] = []
        self.violations: list[BundleViolation] = []
        self.mains: list[int] = []
        self.h1s: list[tuple[int, bool]] = []
        self.doctypes: list[int] = []
        self.htmls: list[int] = []
        self.heads: list[int] = []
        self.bodies: list[int] = []
        self.charsets: list[tuple[int, str]] = []
        self.viewports: list[tuple[int, str]] = []
        self.content_security_policies: list[tuple[int, str]] = []
        self.ids: set[str] = set()
        self.text_by_id: dict[str, list[str]] = {}
        self.resources: list[ResourceReference] = []
        self.script_sources: list[tuple[int, str]] = []
        self.stylesheet_hrefs: list[tuple[int, str]] = []
        self.uses_table = False
        self.uses_mermaid = False
        self.uses_react_flow = False
        self.react_flow_hosts: list[tuple[int, str]] = []
        self.uses_echarts = False
        self.echarts_hosts: list[tuple[int, str, str, str, str]] = []
        self.json_script_lines: dict[str, list[int]] = {}
        self.json_script_parts: dict[str, list[str]] = {}
        self.inline_style_blocks: list[tuple[int, list[str]]] = []
        self.inline_style_attributes: list[tuple[int, str]] = []
        self.inline_script_blocks: list[tuple[int, list[str]]] = []
        self.module_scripts: list[int] = []
        self.template_ids: set[str] = set()
        self._next_tablist_id = 1
        self.radio_tab_groups: dict[str, list[tuple[int, int]]] = {}
        self.artifact_title = ""
        self.visible_text_parts: list[str] = []
        self.meaningful_elements = 0

    def violation(self, line: int, code: str, message: str) -> None:
        self.violations.append(
            BundleViolation(self.path, line, code, message)
        )

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._handle_element(
            tag,
            attrs,
            push=tag.lower() not in HTML_VOID_ELEMENTS,
        )

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized_tag = tag.lower()
        if normalized_tag not in HTML_VOID_ELEMENTS:
            line, _ = self.getpos()
            self.violation(
                line,
                "TAG_NESTING",
                f"non-void <{normalized_tag}> cannot use self-closing syntax in HTML",
            )
        self._handle_element(tag, attrs, push=False)

    def handle_decl(self, decl: str) -> None:
        if decl.strip().casefold() == "doctype html":
            line, _ = self.getpos()
            self.doctypes.append(line)

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        line, _ = self.getpos()
        if not self.stack:
            self.violation(
                line,
                "TAG_NESTING",
                f"unexpected closing tag </{normalized_tag}>",
            )
            return
        if self.stack[-1].tag == normalized_tag:
            frame = self.stack.pop()
            self._finish_frame(frame)
            return

        expected = self.stack[-1].tag
        self.violation(
            line,
            "TAG_NESTING",
            f"closing </{normalized_tag}> crosses open <{expected}>",
        )
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == normalized_tag:
                for frame in self.stack[index:]:
                    self._finish_frame(frame)
                del self.stack[index:]
                return

    def _finish_frame(self, frame: BundleFrame) -> None:
        needs_part = frame.daisy_required_part == "hero-content" or (
            frame.daisy_required_part == "card-body"
            and frame.daisy_unwrapped_content
        )
        if needs_part and not frame.daisy_part_found:
            root = {
                "card-body": "card",
                "hero-content": "hero",
            }[frame.daisy_required_part]
            self.violation(
                frame.line,
                "DAISY_STRUCTURE",
                f".{root} "
                f"must contain a direct .{frame.daisy_required_part} child; "
                "use an artifact-specific class for custom layout",
            )

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if stripped:
            for frame in self.stack:
                if frame.element_id:
                    self.text_by_id.setdefault(frame.element_id, []).append(stripped)
            if (
                self.stack
                and self.stack[-1].daisy_required_part == "card-body"
            ):
                self.stack[-1].daisy_unwrapped_content = True
        if self.stack and self.stack[-1].inline_style_index is not None:
            self.inline_style_blocks[self.stack[-1].inline_style_index][1].append(data)
        elif self.stack and self.stack[-1].inline_script:
            script_id = self.stack[-1].json_script_id
            if script_id:
                self.json_script_parts[script_id].append(data)
            elif self.stack[-1].inline_script_index is not None:
                self.inline_script_blocks[self.stack[-1].inline_script_index][1].append(data)
        elif self.stack and self.stack[-1].in_main and stripped:
            self.visible_text_parts.append(stripped)

    def _handle_element(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        push: bool,
    ) -> None:
        line, _ = self.getpos()
        normalized_tag = tag.lower()
        attributes = {name.lower(): value or "" for name, value in attrs}
        classes = set(attributes.get("class", "").split())
        parent = self.stack[-1] if self.stack else None
        in_main = bool(parent and parent.in_main) or normalized_tag == "main"
        if attributes.get("role", "").lower() == "tablist":
            tablist_id = self._next_tablist_id
            self._next_tablist_id += 1
        else:
            tablist_id = parent.tablist_id if parent else None

        if normalized_tag == "base":
            self.violation(
                line,
                "RESOURCE_LINK",
                "<base> is forbidden because local bundle URLs resolve from each page",
            )
        if "data-artifact-placeholder" in attributes:
            self.violation(
                line,
                "PLACEHOLDER",
                "scaffold placeholder marker remains in a live page",
            )

        if (
            normalized_tag == "meta"
            and attributes.get("name", "").lower() == "artifact-title"
        ):
            self.artifact_title = attributes.get("content", "").strip()

        if attributes.get("id"):
            self.ids.add(attributes["id"])
            self.text_by_id.setdefault(attributes["id"], [])
            if normalized_tag == "template":
                self.template_ids.add(attributes["id"])

        if normalized_tag == "html":
            self.htmls.append(line)
        elif normalized_tag == "head":
            self.heads.append(line)
        elif normalized_tag == "body":
            self.bodies.append(line)
        elif normalized_tag == "meta":
            if "charset" in attributes:
                self.charsets.append((line, attributes["charset"].strip()))
            if attributes.get("name", "").casefold() == "viewport":
                self.viewports.append((line, attributes.get("content", "").strip()))
            if attributes.get("http-equiv", "").casefold() == "content-security-policy":
                self.content_security_policies.append(
                    (line, attributes.get("content", "").strip())
                )

        if normalized_tag == "main":
            self.mains.append(line)
        if normalized_tag == "h1":
            self.h1s.append((line, in_main))
        if in_main and normalized_tag in {
            "audio",
            "canvas",
            "embed",
            "form",
            "iframe",
            "img",
            "object",
            "pre",
            "svg",
            "table",
            "video",
        }:
            self.meaningful_elements += 1

        if attributes.get("style"):
            self.inline_style_attributes.append((line, attributes["style"]))

        if parent and parent.daisy_required_part in classes:
            parent.daisy_part_found = True
        elif (
            parent
            and parent.daisy_required_part == "card-body"
            and normalized_tag not in {"figure", "img", "picture", "source"}
        ):
            parent.daisy_unwrapped_content = True

        daisy_required_part = None
        if "card" in classes:
            daisy_required_part = "card-body"
        elif "hero" in classes:
            daisy_required_part = "hero-content"
        if (
            normalized_tag == "input"
            and attributes.get("type", "").lower() == "radio"
            and attributes.get("name")
            and tablist_id is not None
        ):
            self.radio_tab_groups.setdefault(attributes["name"], []).append(
                (line, tablist_id)
            )

        for resource_attribute in RESOURCE_ATTRIBUTES.get(normalized_tag, ()):
            value = attributes.get(resource_attribute, "")
            if not value:
                continue
            values = srcset_candidates(value) if resource_attribute == "srcset" else [value]
            for resource_value in values:
                self.resources.append(
                    ResourceReference(
                        normalized_tag,
                        resource_attribute,
                        resource_value,
                        line,
                    )
                )
            if normalized_tag == "script" and resource_attribute == "src":
                self.script_sources.append((line, value))
            if (
                normalized_tag == "link"
                and resource_attribute == "href"
                and "stylesheet" in attributes.get("rel", "").split()
            ):
                self.stylesheet_hrefs.append((line, value))

        attribute_text = " ".join(attributes.values())
        if "artifactTable(" in attribute_text or any(
            name.startswith("data-table-") for name in attributes
        ):
            self.uses_table = True
        if "mermaid" in classes or "data-diagram-viewer" in attributes:
            self.uses_mermaid = True
        if "data-react-flow" in attributes:
            self.uses_react_flow = True
            self.react_flow_hosts.append(
                (line, attributes.get("data-react-flow", "").strip())
            )
        if "data-echart" in attributes:
            self.uses_echarts = True
            self.echarts_hosts.append(
                (
                    line,
                    attributes.get("data-echart", "").strip(),
                    attributes.get("aria-label", "").strip(),
                    attributes.get("aria-labelledby", "").strip(),
                    attributes.get("data-echart-renderer", "").strip(),
                )
            )

        json_script_id = None
        if (
            normalized_tag == "script"
            and attributes.get("type", "").lower() == "application/json"
            and attributes.get("id")
        ):
            json_script_id = attributes["id"]
            self.json_script_lines.setdefault(json_script_id, []).append(line)
            self.json_script_parts.setdefault(json_script_id, [])

        inline_style_index = None
        if normalized_tag == "style":
            inline_style_index = len(self.inline_style_blocks)
            self.inline_style_blocks.append((line, []))

        inline_script_index = None
        if (
            normalized_tag == "script"
            and attributes.get("type", "").casefold() == "module"
        ):
            self.module_scripts.append(line)
        if (
            normalized_tag == "script"
            and not attributes.get("src")
            and json_script_id is None
        ):
            inline_script_index = len(self.inline_script_blocks)
            self.inline_script_blocks.append((line, []))

        if push:
            self.stack.append(
                BundleFrame(
                    tag=normalized_tag,
                    line=line,
                    in_main=in_main,
                    tablist_id=tablist_id,
                    inline_script=(
                        normalized_tag == "script" and not attributes.get("src")
                    ),
                    json_script_id=json_script_id,
                    inline_style_index=inline_style_index,
                    inline_script_index=inline_script_index,
                    element_id=attributes.get("id") or None,
                    daisy_required_part=daisy_required_part,
                    daisy_part_found=False,
                    daisy_unwrapped_content=False,
                )
            )

    def finish(self) -> None:
        for frame in reversed(self.stack):
            self._finish_frame(frame)
            self.violation(
                frame.line,
                "TAG_NESTING",
                f"unclosed <{frame.tag}> tag",
            )
        self.stack.clear()


def compact(text: str, limit: int = 140) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def parse_hex_color(value: str) -> tuple[float, float, float] | None:
    raw = value.removeprefix("#")
    if len(raw) == 3:
        raw = "".join(character * 2 for character in raw)
    if len(raw) != 6:
        return None
    return tuple(
        int(raw[index : index + 2], 16) / 255
        for index in range(0, 6, 2)
    )


def relative_luminance(color: tuple[float, float, float]) -> float:
    linear = tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in color
    )
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> float:
    light, dark = sorted(
        (relative_luminance(first), relative_luminance(second)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


def global_cascade_findings(path: Path, css: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in GLOBAL_ANCHOR_COLOR_RE.finditer(css):
        findings.append(
            Finding(
                "DAISY_OVERRIDE",
                path,
                line_for_offset(css, match.start()),
                "Global anchor color can override layered DaisyUI foreground "
                "states such as `btn` and `menu-active`; scope inheritance "
                "outside semantic components.",
                compact(match.group(0).lstrip("}")),
            )
        )
    return findings


def semantic_contrast_findings(
    path: Path,
    css: str,
    class_source_files: list[Path],
) -> list[Finding]:
    token_values = {
        name: value
        for name, value in THEME_TOKEN_RE.findall(css)
    }
    parsed_tokens = {
        name: parse_hex_color(value)
        for name, value in token_values.items()
    }
    findings: list[Finding] = []

    for role in SEMANTIC_ROLES:
        color_name = f"--color-{role}"
        content_name = f"--color-{role}-content"
        color = parsed_tokens.get(color_name)
        content = parsed_tokens.get(content_name)
        if color is None or content is None:
            continue
        ratio = contrast_ratio(color, content)
        if ratio < 4.5:
            findings.append(
                Finding(
                    "CONTRAST_RISK",
                    path,
                    line_for_offset(css, css.find(f"{color_name}:")),
                    "Semantic color/content pair is below 4.5:1.",
                    f"{role}: {ratio:.2f}:1",
                )
            )

    used_soft_roles: set[str] = set()
    for source_path in class_source_files:
        source = source_path.read_text(encoding="utf-8")
        for class_value in CLASS_ATTRIBUTE_RE.findall(source):
            classes = set(class_value.split())
            for component in ("alert", "badge"):
                if f"{component}-soft" not in classes:
                    continue
                used_soft_roles.update(
                    role
                    for role in SEMANTIC_ROLES
                    if f"{component}-{role}" in classes
                )

    base = parsed_tokens.get("--color-base-100")
    if base is None:
        return findings
    for role in sorted(used_soft_roles):
        color_name = f"--color-{role}"
        color = parsed_tokens.get(color_name)
        if color is None:
            continue
        ratio = contrast_ratio(color, base)
        if ratio < 4.5:
            findings.append(
                Finding(
                    "CONTRAST_RISK",
                    path,
                    line_for_offset(css, css.find(f"{color_name}:")),
                    "Soft semantic component reuses the role color as "
                    "foreground, but it is too close to `base-100`.",
                    f"{role} soft proxy: {ratio:.2f}:1",
                )
            )
    return findings


def has_dynamic_root(attributes: dict[str, str]) -> bool:
    dynamic = " ".join(
        value
        for name, value in attributes.items()
        if name in {":class", "x-bind:class"}
    )
    return any(
        re.search(rf"(?<![\w-]){re.escape(root)}(?![\w-])", dynamic)
        for root in DAISY_ACTION_ROOTS
    )


class ArtifactHTMLParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.findings: list[Finding] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        line, _ = self.getpos()
        normalized_tag = tag.lower()
        attributes = {name.lower(): value or "" for name, value in attrs}
        classes = set(attributes.get("class", "").split())
        evidence = compact(self.get_starttag_text() or f"<{normalized_tag}>")

        if normalized_tag == "style":
            self.findings.append(
                Finding(
                    "STYLE_LITERAL",
                    self.path,
                    line,
                    "Embedded style block may split CSS ownership; verify intent.",
                    evidence,
                )
            )

        is_action = (
            normalized_tag == "button"
            or (
                normalized_tag == "input"
                and attributes.get("type", "").lower() in ACTION_INPUT_TYPES
            )
            or attributes.get("role", "").lower() == "button"
        )
        has_daisy_root = bool(classes & DAISY_ACTION_ROOTS) or has_dynamic_root(
            attributes
        )

        if is_action and not has_daisy_root:
            self.findings.append(
                Finding(
                    "LIKELY_REINVENTION",
                    self.path,
                    line,
                    "Custom action control: check whether an existing component "
                    "would express the same role more simply.",
                    evidence,
                )
            )

        if "btn" in classes:
            competing = sorted(
                class_name
                for class_name in classes
                if not class_name.startswith("btn")
                and BUTTON_OVERRIDE_RE.search(class_name)
            )
            if competing:
                self.findings.append(
                    Finding(
                        "DAISY_OVERRIDE",
                        self.path,
                        line,
                        "Button geometry or color is overridden by utilities; "
                        "check whether a `btn-*` variant already expresses it.",
                        ", ".join(competing),
                    )
                )

        for class_name in sorted(classes):
            if ARBITRARY_SPACING_RE.search(class_name):
                self.findings.append(
                    Finding(
                        "STYLE_LITERAL",
                        self.path,
                        line,
                        "Arbitrary spacing or radius may fragment this artifact's rhythm.",
                        class_name,
                    )
                )
            elif ARBITRARY_COLOR_RE.search(
                class_name
            ) or HARDCODED_COLOR_RE.search(class_name):
                self.findings.append(
                    Finding(
                        "STYLE_LITERAL",
                        self.path,
                        line,
                        "Hard-coded color may bypass this artifact's semantic tokens.",
                        class_name,
                    )
                )

        if attributes.get("style"):
            self.findings.append(
                Finding(
                    "STYLE_LITERAL",
                    self.path,
                    line,
                    "Inline style may hide a repeated rule from this artifact's CSS owner.",
                    compact(attributes["style"]),
                )
            )


def css_findings(
    path: Path,
    lines: list[tuple[int, str]],
    *,
    inspect_literals: bool,
) -> list[Finding]:
    findings: list[Finding] = []

    for line_number, line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("/*", "*", "*/")):
            continue

        if "{" in stripped and not stripped.startswith("@"):
            daisy_components = sorted(set(DAISY_SELECTOR_RE.findall(stripped)))
            if daisy_components:
                findings.append(
                    Finding(
                        "DAISY_OVERRIDE",
                        path,
                        line_number,
                        "CSS selector overrides a DaisyUI component root.",
                        ", ".join(f".{name}" for name in daisy_components),
                    )
                )
            if CUSTOM_BUTTON_SELECTOR_RE.search(stripped):
                findings.append(
                    Finding(
                        "LIKELY_REINVENTION",
                        path,
                        line_number,
                        "Custom button-like selector may duplicate DaisyUI `btn`.",
                        compact(stripped),
                    )
                )

        if not inspect_literals:
            continue

        if RAW_COLOR_RE.search(stripped):
            findings.append(
                Finding(
                    "STYLE_LITERAL",
                    path,
                    line_number,
                    "Literal CSS color bypasses the shared semantic palette.",
                    compact(stripped),
                )
            )
        if LITERAL_SPACING_RE.search(stripped):
            findings.append(
                Finding(
                    "STYLE_LITERAL",
                    path,
                    line_number,
                    "Literal spacing or radius creates a local scale value.",
                    compact(stripped),
                )
            )
        custom_tokens = sorted(set(CUSTOM_TOKEN_RE.findall(stripped)))
        if custom_tokens:
            findings.append(
                Finding(
                    "STYLE_LITERAL",
                    path,
                    line_number,
                    "New CSS variable creates another token owner.",
                    ", ".join(custom_tokens),
                )
            )

    return findings


def is_included(path: Path, root: Path) -> bool:
    return not any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts)


def source_files(root: Path, suffix: str) -> list[Path]:
    return sorted(
        path
        for path in root.rglob(f"*{suffix}")
        if path.is_file() and is_included(path, root)
    )


def resolve_html_target(target: Path) -> tuple[Path, list[Path]]:
    resolved = target.expanduser().resolve()
    if resolved.is_file() and resolved.suffix.lower() == ".html":
        root = resolved.parent
        html_files = [resolved]
    elif resolved.is_dir():
        root = resolved
        html_files = source_files(root, ".html")
    else:
        raise ValueError("target must be an artifact directory or HTML file")

    if not html_files:
        raise ValueError("target contains no HTML files")
    return root, html_files


def live_page_topology(
    root: Path,
) -> tuple[list[Path], list[BundleViolation]]:
    live_pages: list[Path] = []
    violations: list[BundleViolation] = []
    html_candidates = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.casefold() == ".html"
    )

    for path in html_candidates:
        relative = path.relative_to(root)
        if relative == Path("index.html"):
            live_pages.append(path)
            continue
        if (
            len(relative.parts) == 2
            and relative.parts[0] == "pages"
            and relative.suffix == ".html"
            and not relative.name.startswith("_")
        ):
            live_pages.append(path)
            continue
        violations.append(
            BundleViolation(
                path,
                1,
                "PAGE_TOPOLOGY",
                "live HTML must be index.html or a direct pages/*.html file",
            )
        )

    index_path = root / "index.html"
    if index_path not in live_pages:
        violations.append(
            BundleViolation(
                index_path,
                1,
                "PAGE_TOPOLOGY",
                "required lowercase index.html is missing",
            )
        )
    return live_pages, violations


def add_file_contract(
    violations: list[BundleViolation],
    artifact_path: Path,
    owner_path: Path,
) -> None:
    if not artifact_path.is_file():
        violations.append(
            BundleViolation(
                artifact_path,
                1,
                "SHARED_ASSET",
                f"required shared file is missing: {artifact_path.name}",
            )
        )
        return
    if artifact_path.read_bytes() != owner_path.read_bytes():
        violations.append(
            BundleViolation(
                artifact_path,
                1,
                "OWNER_DIVERGENCE",
                f"shared file differs from 1html owner: {artifact_path.name}",
            )
        )
def css_resource_violations(
    root: Path,
    path: Path,
    source: str,
    *,
    base_directory: Path,
    first_line: int = 1,
    allow_data: bool = True,
) -> list[BundleViolation]:
    def preserve_lines(match: re.Match[str]) -> str:
        return "".join(
            "\n" if character == "\n" else " " for character in match.group()
        )

    without_comments = re.sub(
        r"/\*.*?\*/",
        preserve_lines,
        source,
        flags=re.DOTALL,
    )
    violations: list[BundleViolation] = []
    for match in re.finditer(r"(?i)@import\b", without_comments):
        violations.append(
            BundleViolation(
                path,
                first_line + line_for_offset(without_comments, match.start()) - 1,
                "RESOURCE_LINK",
                "CSS cannot use @import; link local CSS in HTML",
            )
        )
    for match in re.finditer(
        r"(?i)url\(\s*(?P<quote>['\"]?)(?P<value>.*?)\1\s*\)",
        without_comments,
    ):
        value = match.group("value").strip()
        if not value or value.startswith("#") or (
            allow_data and value.startswith("data:")
        ):
            continue
        parsed = urlsplit(value)
        target = (base_directory / unquote(parsed.path)).resolve()
        if parsed.scheme or parsed.netloc:
            message = f"CSS URL must use a local file: {value}"
        elif not target.is_relative_to(root.resolve()):
            message = f"CSS URL escapes artifact root: {value}"
        elif not target.is_file():
            message = f"CSS URL does not exist: {value}"
        else:
            continue
        violations.append(
            BundleViolation(
                path,
                first_line + line_for_offset(without_comments, match.start()) - 1,
                "RESOURCE_LINK",
                message,
            )
        )
    return violations


def local_css_resource_violations(
    root: Path,
    path: Path,
) -> list[BundleViolation]:
    if not path.is_file():
        return []
    return css_resource_violations(
        root,
        path,
        path.read_text(encoding="utf-8"),
        base_directory=path.parent,
    )


def page_css_resource_violations(
    root: Path,
    page: Path,
    parser: BundleHTMLParser,
) -> list[BundleViolation]:
    violations: list[BundleViolation] = []
    for line, parts in parser.inline_style_blocks:
        violations.extend(
            css_resource_violations(
                root,
                page,
                "".join(parts),
                base_directory=page.parent,
                first_line=line,
            )
        )
    for line, style in parser.inline_style_attributes:
        violations.extend(
            css_resource_violations(
                root,
                page,
                style,
                base_directory=page.parent,
                first_line=line,
            )
        )
    return violations


NETWORK_JS_RE = re.compile(
    r"(?ix)"
    r"\b(?:fetch|import)\s*\(|"
    r"\b(?:new\s+)?(?:XMLHttpRequest|WebSocket|EventSource)\b|"
    r"\bimport\s+(?:[^;\n]+?\s+from\s+)?[\"']"
)


def javascript_portability_violations(
    path: Path,
    source: str,
    *,
    first_line: int = 1,
) -> list[BundleViolation]:
    without_comments = re.sub(
        r"/\*.*?\*/|//[^\n]*",
        lambda match: "".join(
            "\n" if character == "\n" else " " for character in match.group()
        ),
        source,
        flags=re.DOTALL | re.MULTILINE,
    )
    return [
        BundleViolation(
            path,
            first_line + line_for_offset(without_comments, match.start()) - 1,
            "SCRIPT_PORTABILITY",
            "file:// artifact cannot use module import or network runtime APIs",
        )
        for match in NETWORK_JS_RE.finditer(without_comments)
    ]


def positions_for(
    references: list[tuple[int, str]], expected: str
) -> list[int]:
    return [index for index, (_, value) in enumerate(references) if value == expected]


def require_reference(
    violations: list[BundleViolation],
    page: Path,
    references: list[tuple[int, str]],
    expected: str,
    kind: str,
) -> int | None:
    positions = positions_for(references, expected)
    if len(positions) != 1:
        violations.append(
            BundleViolation(
                page,
                1,
                "DEPENDENCY_WIRING",
                f"{kind} must reference {expected} exactly once",
            )
        )
        return None
    return positions[0]


def check_order(
    violations: list[BundleViolation],
    page: Path,
    ordered: list[tuple[str, int | None]],
    kind: str,
) -> None:
    present = [(name, position) for name, position in ordered if position is not None]
    if len(present) != len(ordered):
        return
    positions = [position for _, position in present]
    if positions != sorted(positions):
        names = " → ".join(name for name, _ in ordered)
        violations.append(
            BundleViolation(
                page,
                1,
                "DEPENDENCY_ORDER",
                f"{kind} dependency order must be {names}",
            )
        )


def validate_local_resources(
    root: Path,
    page: Path,
    parser: BundleHTMLParser,
    *,
    same_generation: bool,
) -> list[BundleViolation]:
    violations: list[BundleViolation] = []
    resolved_root = root.resolve()
    navigation_root = resolved_root.parent

    for reference in parser.resources:
        if (
            not same_generation
            and reference.attribute
            not in LEGACY_RESOURCE_ATTRIBUTES.get(reference.tag, ())
        ):
            continue
        parsed = urlsplit(reference.value)
        if reference.tag == "a":
            if parsed.scheme in {"http", "https", "mailto", "tel"}:
                continue
            if parsed.scheme or parsed.netloc:
                violations.append(
                    BundleViolation(
                        page,
                        reference.line,
                        "RESOURCE_LINK",
                        f"unsupported navigation target: {reference.value}",
                    )
                )
                continue
            if not parsed.path:
                target = unquote(parsed.fragment)
                if reference.value == "#":
                    continue
                if target and target not in parser.ids:
                    violations.append(
                        BundleViolation(
                            page,
                            reference.line,
                            "RESOURCE_LINK",
                            f"same-page anchor target does not exist: #{target}",
                        )
                    )
                continue

        if parsed.scheme or parsed.netloc:
            violations.append(
                BundleViolation(
                    page,
                    reference.line,
                    "RESOURCE_LINK",
                    f"{reference.tag}[{reference.attribute}] must use a local file",
                )
            )
            continue
        if not parsed.path:
            continue
        resource_path = (page.parent / unquote(parsed.path)).resolve()
        allowed_root = navigation_root if reference.tag == "a" else resolved_root
        if not resource_path.is_relative_to(allowed_root):
            violations.append(
                BundleViolation(
                    page,
                    reference.line,
                    "RESOURCE_LINK",
                    f"resource escapes artifact root: {reference.value}",
                )
            )
        elif not resource_path.is_file():
            violations.append(
                BundleViolation(
                    page,
                    reference.line,
                    "RESOURCE_LINK",
                    f"local resource does not exist: {reference.value}",
                )
            )
    return violations


def validate_page_shell(
    page: Path,
    parser: BundleHTMLParser,
    *,
    same_generation: bool,
) -> list[BundleViolation]:
    if not same_generation:
        violations = [
            violation
            for violation in parser.violations
            if violation.code in {"TAG_NESTING", "PLACEHOLDER"}
        ]
        return violations

    violations = list(parser.violations)
    shell_contracts = (
        (parser.doctypes, "PAGE_DOCTYPE", "live page requires <!doctype html>"),
        (parser.htmls, "PAGE_HTML", "live page requires exactly one html element"),
        (parser.heads, "PAGE_HEAD", "live page requires exactly one head element"),
        (parser.bodies, "PAGE_BODY", "live page requires exactly one body element"),
    )
    for occurrences, code, message in shell_contracts:
        if len(occurrences) != 1:
            violations.append(
                BundleViolation(
                    page,
                    occurrences[1] if len(occurrences) > 1 else 1,
                    code,
                    message,
                )
            )
    valid_charsets = [
        line for line, value in parser.charsets if value.casefold() == "utf-8"
    ]
    if len(valid_charsets) != 1:
        violations.append(
            BundleViolation(
                page,
                valid_charsets[1] if len(valid_charsets) > 1 else 1,
                "PAGE_CHARSET",
                "live page requires exactly one <meta charset=\"utf-8\">",
            )
        )
    valid_viewports = [
        line
        for line, value in parser.viewports
        if re.search(
            r"(?:^|,)\s*width\s*=\s*device-width(?:\s*,|$)",
            value,
            re.IGNORECASE,
        )
    ]
    if len(valid_viewports) != 1:
        violations.append(
            BundleViolation(
                page,
                valid_viewports[1] if len(valid_viewports) > 1 else 1,
                "PAGE_VIEWPORT",
                "live page requires one viewport meta with width=device-width",
            )
        )
    required_csp = {
        "default-src 'self'",
        "connect-src 'none'",
        "img-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "worker-src 'self'",
    }
    valid_csp = [
        line
        for line, value in parser.content_security_policies
        if all(directive in value for directive in required_csp)
    ]
    if len(valid_csp) != 1:
        violations.append(
            BundleViolation(
                page,
                valid_csp[1] if len(valid_csp) > 1 else 1,
                "PAGE_CSP",
                "live page requires the local-only Content-Security-Policy",
            )
        )
    if len(parser.mains) != 1:
        violations.append(
            BundleViolation(
                page,
                parser.mains[1] if len(parser.mains) > 1 else 1,
                "PAGE_MAIN",
                "live page requires exactly one semantic main element",
            )
        )

    headings_in_main = [line for line, in_main in parser.h1s if in_main]
    if len(headings_in_main) > 1:
        violations.append(
            BundleViolation(
                page,
                headings_in_main[1],
                "PAGE_HEADING",
                "live page allows at most one h1 inside main",
            )
        )
    elif not headings_in_main and not parser.artifact_title:
        violations.append(
            BundleViolation(
                page,
                1,
                "PAGE_HEADING",
                "live page requires an h1 inside main or artifact-title metadata",
            )
        )

    if not parser.visible_text_parts and parser.meaningful_elements == 0:
        violations.append(
            BundleViolation(
                page,
                parser.mains[0] if parser.mains else 1,
                "EMPTY_PAGE",
                "main has no readable text, media, form, canvas, table, or diagram",
            )
        )

    for line in parser.module_scripts:
        violations.append(
            BundleViolation(
                page,
                line,
                "SCRIPT_PORTABILITY",
                "type=module is not portable in the direct file:// contract",
            )
        )

    for name, occurrences in sorted(parser.radio_tab_groups.items()):
        tablists = {tablist_id for _, tablist_id in occurrences}
        if len(tablists) < 2:
            continue
        first_by_tablist: dict[int, int] = {}
        for line, tablist_id in occurrences:
            first_by_tablist.setdefault(tablist_id, line)
        for line in first_by_tablist.values():
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "TAB_RADIO_SCOPE",
                    f"radio name {name!r} spans multiple role=tablist containers",
                )
            )
    return violations


def strict_json_loads(source: str) -> object:
    def reject_constant(value: str) -> object:
        raise ValueError(f"non-finite JSON number: {value}")

    return json.loads(source, parse_constant=reject_constant)


def validate_react_flow_config(
    page: Path,
    parser: BundleHTMLParser,
) -> list[BundleViolation]:
    violations: list[BundleViolation] = []

    for line, config_id in parser.react_flow_hosts:
        if not config_id:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "REACT_FLOW_CONFIG",
                    "data-react-flow must name an application/json script id",
                )
            )
            continue
        script_lines = parser.json_script_lines.get(config_id, [])
        if len(script_lines) != 1:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "REACT_FLOW_CONFIG",
                    f"React Flow config {config_id!r} must exist exactly once",
                )
            )
            continue
        try:
            config = strict_json_loads("".join(parser.json_script_parts[config_id]))
        except (json.JSONDecodeError, ValueError) as error:
            message = error.msg if isinstance(error, json.JSONDecodeError) else str(error)
            relative_line = error.lineno - 1 if isinstance(error, json.JSONDecodeError) else 0
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0] + relative_line,
                    "REACT_FLOW_CONFIG",
                    f"invalid JSON in React Flow config {config_id!r}: {message}",
                )
            )
            continue
        if not isinstance(config, dict):
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0],
                    "REACT_FLOW_CONFIG",
                    f"React Flow config {config_id!r} must be an object",
                )
            )
            continue
        nodes = config.get("nodes")
        edges = config.get("edges", [])
        if not isinstance(nodes, list) or not nodes:
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0],
                    "REACT_FLOW_CONFIG",
                    f"React Flow config {config_id!r} needs a non-empty nodes array",
                )
            )
            continue
        if not isinstance(edges, list):
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0],
                    "REACT_FLOW_CONFIG",
                    f"React Flow config {config_id!r} edges must be an array",
                )
            )
            continue

        node_ids: set[str] = set()
        for node in nodes:
            node_id = node.get("id") if isinstance(node, dict) else None
            if not isinstance(node_id, str) or not node_id:
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        "every React Flow node needs a non-empty string id",
                    )
                )
                continue
            if node_id in node_ids:
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        f"duplicate React Flow node id: {node_id}",
                    )
                )
            node_ids.add(node_id)
            position = node.get("position")
            coordinates = (
                position.get("x") if isinstance(position, dict) else None,
                position.get("y") if isinstance(position, dict) else None,
            )
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                for value in coordinates
            ):
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        f"React Flow node needs numeric x/y position: {node_id}",
                    )
                )
            if "data" in node and not isinstance(node["data"], dict):
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        f"React Flow node data must be an object: {node_id}",
                    )
                )
                data = {}
            else:
                data = node.get("data", {})
            template_id = node.get("template", data.get("template"))
            label = node.get("label", data.get("label"))
            if template_id is not None:
                if not isinstance(template_id, str) or not template_id:
                    violations.append(
                        BundleViolation(
                            page,
                            script_lines[0],
                            "REACT_FLOW_CONFIG",
                            f"React Flow node template must be a non-empty id: {node_id}",
                        )
                    )
                elif template_id not in parser.template_ids:
                    violations.append(
                        BundleViolation(
                            page,
                            script_lines[0],
                            "REACT_FLOW_CONFIG",
                            f"React Flow node template does not exist: {template_id}",
                        )
                    )
            elif not isinstance(label, str) or not label.strip():
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        f"React Flow node needs template or label: {node_id}",
                    )
                )

        edge_ids: set[str] = set()
        for edge in edges:
            edge_id = edge.get("id") if isinstance(edge, dict) else None
            if not isinstance(edge_id, str) or not edge_id:
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        "every React Flow edge needs a non-empty string id",
                    )
                )
                continue
            if edge_id in edge_ids:
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        f"duplicate React Flow edge id: {edge_id}",
                    )
                )
            edge_ids.add(edge_id)
            if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
                violations.append(
                    BundleViolation(
                        page,
                        script_lines[0],
                        "REACT_FLOW_CONFIG",
                        f"React Flow edge points to an unknown node: {edge_id}",
                    )
                )
    return violations


def validate_echarts_config(
    page: Path,
    parser: BundleHTMLParser,
) -> list[BundleViolation]:
    violations: list[BundleViolation] = []

    for line, config_id, host_aria_label, labelled_by, renderer in parser.echarts_hosts:
        if not config_id:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "ECHARTS_CONFIG",
                    "data-echart must name an application/json script id",
                )
            )
            continue
        script_lines = parser.json_script_lines.get(config_id, [])
        if len(script_lines) != 1:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "ECHARTS_CONFIG",
                    f"ECharts config {config_id!r} must exist exactly once",
                )
            )
            continue
        try:
            option = strict_json_loads("".join(parser.json_script_parts[config_id]))
        except (json.JSONDecodeError, ValueError) as error:
            message = error.msg if isinstance(error, json.JSONDecodeError) else str(error)
            relative_line = error.lineno - 1 if isinstance(error, json.JSONDecodeError) else 0
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0] + relative_line,
                    "ECHARTS_CONFIG",
                    f"invalid JSON in ECharts config {config_id!r}: {message}",
                )
            )
            continue
        if not isinstance(option, dict):
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0],
                    "ECHARTS_CONFIG",
                    f"ECharts config {config_id!r} must be an object",
                )
            )
            continue
        series = option.get("series")
        if not isinstance(series, list) or not series:
            violations.append(
                BundleViolation(
                    page,
                    script_lines[0],
                    "ECHARTS_CONFIG",
                    f"ECharts config {config_id!r} needs a non-empty series array",
                )
            )
        if renderer and renderer not in {"svg", "canvas"}:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "ECHARTS_CONFIG",
                    "data-echart-renderer must be svg or canvas",
                )
            )
        aria = option.get("aria") if isinstance(option.get("aria"), dict) else {}
        option_aria_label = (
            aria.get("label") if isinstance(aria.get("label"), dict) else {}
        )
        authored_description = option_aria_label.get("description") or aria.get(
            "description"
        )
        labelled_ids = labelled_by.split()
        missing_label_ids = [item for item in labelled_ids if item not in parser.ids]
        empty_label_ids = [
            item
            for item in labelled_ids
            if item in parser.ids
            and not " ".join(parser.text_by_id.get(item, [])).strip()
        ]
        host_has_description = bool(host_aria_label) or bool(
            labelled_ids and not missing_label_ids and not empty_label_ids
        )
        if not host_has_description and not (
            isinstance(authored_description, str) and authored_description.strip()
        ):
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "ECHARTS_CONFIG",
                    "ECharts host needs aria-label/aria-labelledby or aria.label.description",
                )
            )
        if missing_label_ids:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "ECHARTS_CONFIG",
                    "ECharts aria-labelledby points to missing id(s): "
                    + ", ".join(missing_label_ids),
                )
            )
        if empty_label_ids:
            violations.append(
                BundleViolation(
                    page,
                    line,
                    "ECHARTS_CONFIG",
                    "ECharts aria-labelledby points to empty id(s): "
                    + ", ".join(empty_label_ids),
                )
            )
    return violations


def validate_page_dependencies(
    root: Path,
    page: Path,
    parser: BundleHTMLParser,
    *,
    same_generation: bool,
) -> list[BundleViolation]:
    violations = validate_local_resources(
        root,
        page,
        parser,
        same_generation=same_generation,
    )
    if not same_generation:
        return violations
    prefix = "../" if page.parent.name == "pages" else ""

    if parser.uses_table:
        table_script = require_reference(
            violations,
            page,
            parser.script_sources,
            f"{prefix}assets/artifact-table.js",
            "table script",
        )
        alpine_script = require_reference(
            violations,
            page,
            parser.script_sources,
            f"{prefix}lib/alpine.js",
            "table runtime",
        )
        check_order(
            violations,
            page,
            [
                ("artifact-table.js", table_script),
                ("alpine.js", alpine_script),
            ],
            "table script",
        )

    if parser.uses_mermaid:
        diagram_css = require_reference(
            violations,
            page,
            parser.stylesheet_hrefs,
            f"{prefix}assets/diagram-viewer.css",
            "Mermaid stylesheet",
        )
        local_positions = positions_for(
            parser.stylesheet_hrefs,
            f"{prefix}assets/local.css",
        )
        if local_positions:
            check_order(
                violations,
                page,
                [
                    ("diagram-viewer.css", diagram_css),
                    ("local.css", local_positions[0]),
                ],
                "Mermaid stylesheet",
            )
        mermaid_scripts = [
            ("mermaid.min.js", f"{prefix}lib/mermaid.min.js"),
            (
                "mermaid-layout-elk.iife.min.js",
                f"{prefix}lib/mermaid-layout-elk.iife.min.js",
            ),
            ("panzoom.min.js", f"{prefix}lib/panzoom.min.js"),
            ("diagram-viewer.js", f"{prefix}assets/diagram-viewer.js"),
            ("mermaid-init.js", f"{prefix}assets/mermaid-init.js"),
        ]
        positions = [
            (
                name,
                require_reference(
                    violations,
                    page,
                    parser.script_sources,
                    source,
                    "Mermaid script",
                ),
            )
            for name, source in mermaid_scripts
        ]
        check_order(violations, page, positions, "Mermaid script")

    if parser.uses_react_flow:
        violations.extend(validate_react_flow_config(page, parser))
        vendor_css = require_reference(
            violations,
            page,
            parser.stylesheet_hrefs,
            f"{prefix}lib/react-flow.css",
            "React Flow stylesheet",
        )
        bridge_css = require_reference(
            violations,
            page,
            parser.stylesheet_hrefs,
            f"{prefix}assets/react-flow-theme.css",
            "React Flow palette bridge",
        )
        local_positions = positions_for(
            parser.stylesheet_hrefs,
            f"{prefix}assets/local.css",
        )
        ordered_css = [
            ("react-flow.css", vendor_css),
            ("react-flow-theme.css", bridge_css),
        ]
        if local_positions:
            ordered_css.append(("local.css", local_positions[0]))
        check_order(violations, page, ordered_css, "React Flow stylesheet")
        vendor_script = require_reference(
            violations,
            page,
            parser.script_sources,
            f"{prefix}lib/react-flow.vendor.js",
            "React Flow vendor script",
        )
        init_script = require_reference(
            violations,
            page,
            parser.script_sources,
            f"{prefix}assets/react-flow-init.js",
            "React Flow init script",
        )
        check_order(
            violations,
            page,
            [
                ("react-flow.vendor.js", vendor_script),
                ("react-flow-init.js", init_script),
            ],
            "React Flow script",
        )

    if parser.uses_echarts:
        violations.extend(validate_echarts_config(page, parser))
        vendor_script = require_reference(
            violations,
            page,
            parser.script_sources,
            f"{prefix}lib/echarts.min.js",
            "ECharts vendor script",
        )
        init_script = require_reference(
            violations,
            page,
            parser.script_sources,
            f"{prefix}assets/echarts-init.js",
            "ECharts init script",
        )
        check_order(
            violations,
            page,
            [
                ("echarts.min.js", vendor_script),
                ("echarts-init.js", init_script),
            ],
            "ECharts script",
        )

    return violations


def bundle_violations(
    target: Path,
    *,
    legacy_requested: bool,
) -> tuple[Path, list[Path], str, list[BundleViolation]]:
    root = target.expanduser().resolve()
    if not root.is_dir():
        raise ValueError("target must be an artifact directory")

    skill_dir = Path(__file__).resolve().parent.parent
    scaffold_dir = skill_dir / "assets/scaffold"
    owner_marker = scaffold_dir / BUNDLE_MARKER
    artifact_marker = root / BUNDLE_MARKER
    marker_matches = (
        owner_marker.is_file()
        and artifact_marker.is_file()
        and owner_marker.read_bytes() == artifact_marker.read_bytes()
    )
    marker_missing = not artifact_marker.exists()
    marker_unknown = artifact_marker.exists() and not marker_matches
    same_generation = marker_matches
    legacy_mode = not same_generation and legacy_requested
    if same_generation:
        mode = "same-generation"
    elif legacy_mode:
        mode = "legacy"
    elif marker_unknown and not legacy_requested:
        mode = "unknown-version"
    else:
        mode = "unversioned"
    live_pages, violations = live_page_topology(root)
    if not same_generation:
        violations = []

    if marker_missing and not legacy_requested:
        violations.append(
            BundleViolation(
                artifact_marker,
                1,
                "BUNDLE_VERSION",
                "bundle marker is missing; rerun finish explicitly with --legacy",
            )
        )
    elif marker_unknown and not legacy_requested:
        violations.append(
            BundleViolation(
                artifact_marker,
                1,
                "BUNDLE_VERSION",
                "bundle marker is not current; rerun finish explicitly with --legacy",
            )
        )
    elif marker_matches and legacy_requested:
        violations.append(
            BundleViolation(
                artifact_marker,
                1,
                "BUNDLE_VERSION",
                "current bundle marker cannot be audited with --legacy",
            )
        )
    if same_generation:
        for owner_runtime in sorted((scaffold_dir / "lib").rglob("*")):
            if owner_runtime.is_file() and owner_runtime.suffix in {
                ".css",
                ".js",
                ".txt",
            }:
                add_file_contract(
                    violations,
                    root / owner_runtime.relative_to(scaffold_dir),
                    owner_runtime,
                )

    for css_path in source_files(root, ".css"):
        violations.extend(local_css_resource_violations(root, css_path))

    parsed_pages: list[BundleHTMLParser] = []
    for page in live_pages:
        source = page.read_text(encoding="utf-8")
        parser = BundleHTMLParser(page)
        parser.feed(source)
        parser.close()
        parser.finish()
        parsed_pages.append(parser)
        violations.extend(
            validate_page_shell(
                page,
                parser,
                same_generation=same_generation,
            )
        )
        violations.extend(
            validate_page_dependencies(
                root,
                page,
                parser,
                same_generation=same_generation,
            )
        )
        if same_generation:
            violations.extend(page_css_resource_violations(root, page, parser))
            for line, parts in parser.inline_script_blocks:
                violations.extend(
                    javascript_portability_violations(
                        page,
                        "".join(parts),
                        first_line=line,
                    )
                )
        for marker in KNOWN_PLACEHOLDER_MARKERS:
            if marker in source:
                violations.append(
                    BundleViolation(
                        page,
                        line_for_offset(source, source.index(marker)),
                        "PLACEHOLDER",
                        f"scaffold placeholder text remains: {marker}",
                    )
                )

    if same_generation:
        for javascript_path in source_files(root, ".js"):
            violations.extend(
                javascript_portability_violations(
                    javascript_path,
                    javascript_path.read_text(encoding="utf-8"),
                )
            )

        mermaid_names = {
            "mermaid.min.js",
            "mermaid-layout-elk.iife.min.js",
            "panzoom.min.js",
            "diagram-viewer.js",
            "mermaid-init.js",
            "diagram-viewer.css",
        }
        mermaid_active = any(
            parser.uses_mermaid
            or any(
                Path(urlsplit(source).path).name in mermaid_names
                for _, source in [
                    *parser.script_sources,
                    *parser.stylesheet_hrefs,
                ]
            )
            for parser in parsed_pages
        )
        if mermaid_active:
            mermaid_files = (
                "lib/mermaid.min.js",
                "lib/mermaid-layout-elk.iife.min.js",
                "lib/panzoom.min.js",
                "lib/MERMAID_THIRD_PARTY_NOTICES.txt",
                "lib/licenses/mermaid.txt",
                "lib/licenses/mermaid-layout-elk.txt",
                "lib/licenses/panzoom.txt",
            )
            for relative in mermaid_files:
                add_file_contract(
                    violations,
                    root / relative,
                    skill_dir / "assets/mermaid" / relative,
                )

        react_flow_names = {
            "react-flow.vendor.js",
            "react-flow.css",
            "react-flow-theme.css",
            "react-flow-init.js",
        }
        react_flow_active = any(
            parser.uses_react_flow
            or any(
                Path(urlsplit(source).path).name in react_flow_names
                for _, source in [
                    *parser.script_sources,
                    *parser.stylesheet_hrefs,
                ]
            )
            for parser in parsed_pages
        )
        if react_flow_active:
            react_flow_vendor_files = [
                "lib/react-flow.vendor.js",
                "lib/react-flow.css",
                "lib/REACT_FLOW_THIRD_PARTY_NOTICES.txt",
            ]
            react_flow_vendor_files.extend(
                str(path.relative_to(skill_dir / "assets/react-flow"))
                for path in sorted(
                    (skill_dir / "assets/react-flow/lib/licenses").glob("*.txt")
                )
            )
            for relative in react_flow_vendor_files:
                add_file_contract(
                    violations,
                    root / relative,
                    skill_dir / "assets/react-flow" / relative,
                )

        echarts_names = {"echarts.min.js", "echarts-init.js"}
        echarts_active = any(
            parser.uses_echarts
            or any(
                Path(urlsplit(source).path).name in echarts_names
                for _, source in parser.script_sources
            )
            for parser in parsed_pages
        )
        if echarts_active:
            echarts_vendor_files = (
                "lib/echarts.min.js",
                "lib/ECHARTS_LICENSE",
                "lib/ECHARTS_NOTICE",
                "lib/ECHARTS_THIRD_PARTY_NOTICES.txt",
                "lib/licenses/ECHARTS_LICENSE-d3",
            )
            owner_files = {
                "lib/echarts.min.js": "lib/echarts.min.js",
                "lib/ECHARTS_LICENSE": "lib/LICENSE",
                "lib/ECHARTS_NOTICE": "lib/NOTICE",
                "lib/ECHARTS_THIRD_PARTY_NOTICES.txt": (
                    "lib/ECHARTS_THIRD_PARTY_NOTICES.txt"
                ),
                "lib/licenses/ECHARTS_LICENSE-d3": "lib/licenses/LICENSE-d3",
            }
            for relative in echarts_vendor_files:
                add_file_contract(
                    violations,
                    root / relative,
                    skill_dir / "assets/echarts" / owner_files[relative],
                )

    unique = {
        (violation.path, violation.line, violation.code, violation.message): violation
        for violation in violations
    }
    ordered = sorted(
        unique.values(),
        key=lambda violation: (
            str(violation.path),
            violation.line,
            violation.code,
            violation.message,
        ),
    )
    return root, live_pages, mode, ordered


def audit(
    target: Path,
) -> tuple[Path, list[Path], list[Path], list[Path], list[Finding]]:
    root, html_files = resolve_html_target(target)
    css_files = source_files(root, ".css")
    js_files = source_files(root, ".js")

    findings: list[Finding] = []
    for html_path in html_files:
        parser = ArtifactHTMLParser(html_path)
        parser.feed(html_path.read_text(encoding="utf-8"))
        findings.extend(parser.findings)

    theme_path = next(
        (path for path in css_files if path.name == "theme.css"),
        None,
    )
    if theme_path is not None:
        findings.extend(
            semantic_contrast_findings(
                theme_path,
                theme_path.read_text(encoding="utf-8"),
                [*html_files, *js_files],
            )
        )

    for css_path in css_files:
        current = css_path.read_text(encoding="utf-8")
        findings.extend(global_cascade_findings(css_path, current))
        lines = list(enumerate(current.splitlines(), start=1))
        findings.extend(css_findings(css_path, lines, inspect_literals=True))

    unique = {
        (
            finding.category,
            finding.path,
            finding.line,
            finding.message,
            finding.evidence,
        ): finding
        for finding in findings
    }
    ordered = sorted(
        unique.values(),
        key=lambda finding: (
            CATEGORY_ORDER.index(finding.category),
            str(finding.path),
            finding.line,
            finding.message,
        ),
    )
    return root, html_files, css_files, js_files, ordered


def print_report(
    root: Path,
    html_files: list[Path],
    css_files: list[Path],
    js_files: list[Path],
    findings: list[Finding],
) -> None:
    print("HTML anti-drift audit — advisory, never pass/fail")
    print(f"target={root}")
    print(
        f"scanned={len(html_files)} html, {len(css_files)} css, "
        f"{len(js_files)} js"
    )
    print(f"findings={len(findings)}")

    if not findings:
        print(
            "\nNo strong source-level drift signals found. "
            "This is not a visual-quality verdict."
        )
        return

    visible = findings[:MAX_VISIBLE_FINDINGS]
    for category in CATEGORY_ORDER:
        category_findings = [
            finding
            for finding in visible
            if finding.category == category
        ]
        if not category_findings:
            continue
        print(f"\n{category} ({len(category_findings)})")
        for finding in category_findings:
            relative_path = finding.path.relative_to(root)
            print(
                f"- {relative_path}:{finding.line} — {finding.message} "
                f"[{finding.evidence}]"
            )

    omitted = len(findings) - len(visible)
    if omitted:
        print(f"\n… {omitted} additional signals omitted.")
    print(
        "\nInterpret these as review prompts. Keep intentional local "
        "exceptions local; do not auto-fix them."
    )


def print_bundle_report(
    root: Path,
    live_pages: list[Path],
    mode: str,
    violations: list[BundleViolation],
) -> None:
    print("HTML bundle contract — blocking")
    print(f"target={root}")
    print(f"mode={mode}")
    print(f"scanned={len(live_pages)} live html")
    print(f"violations={len(violations)}")

    for violation in violations:
        try:
            relative = violation.path.relative_to(root)
        except ValueError:
            relative = violation.path
        print(
            f"- {relative}:{violation.line} [{violation.code}] "
            f"{violation.message}"
        )

    if not violations:
        print("Bundle contract satisfied.")


def main() -> int:
    arguments = sys.argv[1:]
    bundle_mode = "--check-bundle" in arguments
    advisory_mode = len(arguments) == 1
    if bundle_mode:
        allowed = {"--check-bundle", "--legacy"}
        options = [argument for argument in arguments if argument.startswith("--")]
        targets = [argument for argument in arguments if not argument.startswith("--")]
        if (
            any(option not in allowed for option in options)
            or len(targets) != 1
        ):
            print(
                "Usage: audit_html_style.py --check-bundle "
                "[--legacy] <artifact-directory>",
                file=sys.stderr,
            )
            return 2
        try:
            root, live_pages, mode, violations = bundle_violations(
                Path(targets[0]),
                legacy_requested="--legacy" in arguments,
            )
        except (OSError, UnicodeError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print_bundle_report(root, live_pages, mode, violations)
        return 1 if violations else 0

    if not advisory_mode:
        print(
            "Usage: audit_html_style.py <artifact-directory-or-index.html>",
            file=sys.stderr,
        )
        return 2

    target = Path(arguments[-1])

    try:
        root, html_files, css_files, js_files, findings = audit(target)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print_report(root, html_files, css_files, js_files, findings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
