#!/usr/bin/env python3
"""Report likely DaisyUI reinvention and style drift in one HTML artifact."""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


EXCLUDED_DIRS = {"_catalog", ".git", "lib", "node_modules", "sources"}
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
    "STYLE_LITERAL",
    "OWNER_DIVERGENCE",
)
MAX_VISIBLE_FINDINGS = 40

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


@dataclass(frozen=True)
class Finding:
    category: str
    path: Path
    line: int
    message: str
    evidence: str


def compact(text: str, limit: int = 140) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


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
                    "Embedded style block creates a local CSS owner.",
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
                    "Action control has no DaisyUI action root such as `btn`.",
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
                        "Arbitrary spacing or radius bypasses the shared scale.",
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
                        "Hard-coded color bypasses DaisyUI semantic color roles.",
                        class_name,
                    )
                )

        if attributes.get("style"):
            self.findings.append(
                Finding(
                    "STYLE_LITERAL",
                    self.path,
                    line,
                    "Inline style creates a local style owner.",
                    compact(attributes["style"]),
                )
            )


def changed_target_lines(baseline: str, current: str) -> list[tuple[int, str]]:
    matcher = difflib.SequenceMatcher(
        a=baseline.splitlines(), b=current.splitlines(), autojunk=False
    )
    changed: list[tuple[int, str]] = []
    current_lines = current.splitlines()

    for operation, _, _, current_start, current_end in matcher.get_opcodes():
        if operation not in {"insert", "replace"}:
            continue
        changed.extend(
            (line_number + 1, current_lines[line_number])
            for line_number in range(current_start, current_end)
        )

    return changed


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


def audit(target: Path) -> tuple[Path, list[Path], list[Path], list[Finding]]:
    resolved = target.expanduser().resolve()
    if resolved.is_file() and resolved.suffix.lower() == ".html":
        root = resolved.parent
    elif resolved.is_dir():
        root = resolved
    else:
        raise ValueError("target must be an artifact directory or HTML file")

    html_files = (
        [resolved]
        if resolved.is_file()
        else source_files(root, ".html")
    )
    css_files = source_files(root, ".css")
    if not html_files:
        raise ValueError("target contains no HTML files")

    findings: list[Finding] = []
    for html_path in html_files:
        parser = ArtifactHTMLParser(html_path)
        parser.feed(html_path.read_text(encoding="utf-8"))
        findings.extend(parser.findings)

    skill_dir = Path(__file__).resolve().parent.parent
    owner_baselines = {
        "theme.css": skill_dir / "assets" / "starter" / "assets" / "theme.css",
        "diagram-viewer.css": (
            skill_dir / "assets" / "mermaid" / "assets" / "diagram-viewer.css"
        ),
    }

    for css_path in css_files:
        current = css_path.read_text(encoding="utf-8")
        baseline_path = owner_baselines.get(css_path.name)
        if baseline_path is not None:
            baseline = baseline_path.read_text(encoding="utf-8")
            if current == baseline:
                continue
            findings.append(
                Finding(
                    "OWNER_DIVERGENCE",
                    css_path,
                    1,
                    "Shared CSS asset differs from the current 1html owner; "
                    "review whether the change is an intentional exception.",
                    css_path.name,
                )
            )
            lines = changed_target_lines(baseline, current)
            findings.extend(
                css_findings(css_path, lines, inspect_literals=False)
            )
            continue

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
    return root, html_files, css_files, ordered


def print_report(
    root: Path,
    html_files: list[Path],
    css_files: list[Path],
    findings: list[Finding],
) -> None:
    print("HTML anti-drift audit — advisory, never pass/fail")
    print(f"target={root}")
    print(f"scanned={len(html_files)} html, {len(css_files)} css")
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


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: audit_html_style.py <artifact-directory-or-index.html>",
            file=sys.stderr,
        )
        return 2

    try:
        root, html_files, css_files, findings = audit(Path(sys.argv[1]))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print_report(root, html_files, css_files, findings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
