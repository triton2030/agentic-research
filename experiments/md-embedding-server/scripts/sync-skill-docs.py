#!/usr/bin/env python3
"""Legacy helper: render the Codex SKILL.md from the Claude SKILL.md.

Use only after explicitly deciding that the Claude skill is the canonical
source for this sync pass. In Codex sessions, Claude-side skill files are
read-only project context; a `--check` failure can be an intentional handoff,
not a backend failure. Do not run the write mode merely as a default closeout
gate after Codex-only recipe edits.

Post-2026-05-21 refactor: the two SKILL.md files have intentional drift
(Codex has Runtime-sanity / agents sections Claude does not). Treat
`--check` as a diff probe, not an enforcement gate.

Mechanical transforms applied:

  - Skill home path (`~/.claude/skills/...` -> `~/.codex/skills/...`)
  - Skill-reference syntax (`1md-graph` -> `$1md-graph` — Codex prefix)

Usage:
    python3 scripts/sync-skill-docs.py            # render Codex from Claude
    python3 scripts/sync-skill-docs.py --check    # exit non-zero on drift
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CLAUDE_SKILL_MD = Path("~/.claude/skills/1md-navigator/SKILL.md").expanduser()
CODEX_SKILL_MD = Path("~/.codex/skills/1md-navigator/SKILL.md").expanduser()


# Skill references that should be prefixed with `$` in the Codex copy.
# Matched as `` `1<name>` `` (backtick-wrapped) to avoid touching prose.
SKILL_REF_PATTERN = re.compile(r"`1([a-z][a-z0-9-]*)`")


def render_for_codex(claude_text: str) -> str:
    out = claude_text

    # 1. Skill home paths.
    out = out.replace("~/.claude/skills/", "~/.codex/skills/")

    # 2. Skill-reference prefix: `1md-graph` → `$1md-graph` etc.
    out = SKILL_REF_PATTERN.sub(r"`$1\1`", out)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the Codex file is out of sync with the rendered output.",
    )
    args = parser.parse_args()

    if not CLAUDE_SKILL_MD.exists():
        print(f"Claude source missing: {CLAUDE_SKILL_MD}", file=sys.stderr)
        return 2
    if not CODEX_SKILL_MD.parent.exists():
        print(f"Codex target dir missing: {CODEX_SKILL_MD.parent}", file=sys.stderr)
        return 2

    source = CLAUDE_SKILL_MD.read_text(encoding="utf-8")
    rendered = render_for_codex(source)

    if args.check:
        existing = CODEX_SKILL_MD.read_text(encoding="utf-8") if CODEX_SKILL_MD.exists() else ""
        if existing == rendered:
            print("SKILL.md in sync.")
            return 0
        print("SKILL.md drift detected.", file=sys.stderr)
        print(f"  Source: {CLAUDE_SKILL_MD}", file=sys.stderr)
        print(f"  Target: {CODEX_SKILL_MD}", file=sys.stderr)
        print(f"  Run: {sys.argv[0]}", file=sys.stderr)
        return 1

    CODEX_SKILL_MD.write_text(rendered, encoding="utf-8")
    print(f"Rendered {CODEX_SKILL_MD} from {CLAUDE_SKILL_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
