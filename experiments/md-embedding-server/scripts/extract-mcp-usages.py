#!/usr/bin/env python3
"""Extract md_* usage mentions from Claude/Codex skill Markdown."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


SKILLS = [
    "1md-navigator",
    "1md-graph",
    "1ia-audit",
    "1instruction-layer",
    "1planning",
    "1strategy",
    "1strategy-docs",
    "1folder-contract",
    "1assumption-audit",
    "1work-review",
    "1skill-architect",
    "1smart-simple",
    "1cli-tools",
]

TOOL_RE = re.compile(r"md_[a-z_]+")
CALL_RE = re.compile(r"md_[a-z_]+\s*\(\s*\{[^`\n]*")


def skill_paths() -> list[tuple[str, str, Path]]:
    home = Path.home()
    roots = {
        "claude": home / ".claude" / "skills",
        "codex": home / ".codex" / "skills",
    }
    paths: list[tuple[str, str, Path]] = []
    for platform, root in roots.items():
        for skill in SKILLS:
            paths.append((platform, skill, root / skill / "SKILL.md"))
    return paths


def rows() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for platform, skill, path in skill_paths():
        if not path.exists():
            out.append(
                {
                    "platform": platform,
                    "skill": skill,
                    "path": str(path),
                    "line_number": "",
                    "tool": "",
                    "invocation_pattern": "MISSING_SKILL_FILE",
                }
            )
            continue
        before = len(out)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            tools = sorted(set(TOOL_RE.findall(line)))
            if not tools:
                continue
            call_match = CALL_RE.search(line)
            pattern = call_match.group(0) if call_match else line.strip()
            for tool in tools:
                out.append(
                    {
                        "platform": platform,
                        "skill": skill,
                        "path": str(path),
                        "line_number": str(line_number),
                        "tool": tool,
                        "invocation_pattern": pattern,
                    }
                )
        if len(out) == before:
            out.append(
                {
                    "platform": platform,
                    "skill": skill,
                    "path": str(path),
                    "line_number": "",
                    "tool": "",
                    "invocation_pattern": "NO_MD_REFERENCES",
                }
            )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/mcp-usages-extracted.csv")
    args = parser.parse_args()

    data = rows()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["platform", "skill", "path", "line_number", "tool", "invocation_pattern"],
        )
        writer.writeheader()
        writer.writerows(data)
    print(f"wrote {len(data)} rows -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
