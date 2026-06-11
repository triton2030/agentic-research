#!/usr/bin/env python3
"""Check or regenerate skill docs derived from the md CLI catalog.

The md CLI catalog is the source for generated skill-side tool catalogs. This
helper checks Claude + Codex skill roots for stale md-mcp references and keeps
both generated catalogs fresh.

Usage:
    python3 scripts/sync-skill-docs.py --check
    python3 scripts/sync-skill-docs.py --regenerate
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILLS = Path("~/.codex/skills").expanduser()
CLAUDE_SKILLS = Path("~/.claude/skills").expanduser()
SKILL_ROOTS = (
    ("Codex", CODEX_SKILLS),
    ("Claude", CLAUDE_SKILLS),
)
CATALOGS = tuple(
    (label, root / "1md-navigator" / "references" / "tool-catalog.md")
    for label, root in SKILL_ROOTS
)
GENERATOR = ROOT / "scripts" / "generate_tool_catalog_md.py"

STALE_TOOL_IDS = (
    "md_audit",
    "md_changed",
    "md_check",
    "md_cluster",
    "md_coherence_audit",
    "md_corpus_scan",
    "md_cycles",
    "md_deps",
    "md_edit_context",
    "md_extract",
    "md_health",
    "md_impact",
    "md_importance",
    "md_index",
    "md_init",
    "md_ls",
    "md_orient",
    "md_overlaps",
    "md_ping",
    "md_preflight",
    "md_profile_sections",
    "md_query_by_type",
    "md_read_related",
    "md_refactor_candidates",
    "md_repeated_concepts",
    "md_scan",
    "md_search",
    "md_search_read",
    "md_semantic_neighbors",
    "md_section_blast_radius",
    "md_status",
    "md_strip",
    "md_toc",
    "md_walk",
)

STALE_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(name) for name in STALE_TOOL_IDS) + r")\b|"
    r"mcp__md-mcp|md-mcp|MD_NAVIGATOR_SCRIPT|md_navigator\.py|md_graph\.py|"
    r"experiments/md-embedding-server/mcp/README\.md|listTools|"
    r"\bmd\s+(?:changed|map|headings|read(?!-related)|md_[a-z_]+)\b"
)


def generated_catalog() -> str:
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "generate_tool_catalog_md.py failed")
    return result.stdout


def stale_skill_refs() -> list[str]:
    findings: list[str] = []
    for label, root in SKILL_ROOTS:
        if not root.exists():
            findings.append(f"{label} skills root missing: {root}")
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for line_no, line in enumerate(text.splitlines(), 1):
                if STALE_PATTERN.search(line):
                    findings.append(f"{path}:{line_no}: {line.strip()}")
    return findings


def check_catalogs() -> list[str]:
    expected = generated_catalog()
    findings: list[str] = []
    for label, catalog in CATALOGS:
        if not catalog.exists():
            findings.append(f"missing {label} catalog: {catalog}")
            continue
        actual = catalog.read_text(encoding="utf-8")
        if actual != expected:
            findings.append(f"stale {label} catalog: {catalog}")
    return findings


def regenerate() -> None:
    catalog = generated_catalog()
    for _, path in CATALOGS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(catalog, encoding="utf-8")
        print(f"Regenerated {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check Claude/Codex skill docs and catalog freshness.")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate Claude/Codex tool-catalog.md.")
    args = parser.parse_args()

    if args.regenerate:
        regenerate()
        return 0

    if not args.check:
        parser.print_help()
        return 0

    findings = stale_skill_refs() + check_catalogs()
    if findings:
        print("Skill docs check failed:", file=sys.stderr)
        for item in findings:
            print(f"  {item}", file=sys.stderr)
        print("Run with --regenerate for catalog drift; edit stale refs manually.", file=sys.stderr)
        return 1
    print("Claude/Codex skill docs are CLI-migrated; tool catalogs are fresh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
