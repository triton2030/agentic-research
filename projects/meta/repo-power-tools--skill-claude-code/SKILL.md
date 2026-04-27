---
name: repo-power-tools
description: Use when repo work needs fast CLI-backed evidence: moves, renames, cleanup, dead files/exports, broken docs links, stale docs references, package shape, dependency drift, import graph checks, security scans, or structural code patterns. Skip browser, Playwright, visual QA, and ordinary feature implementation.
---

# Repo Power Tools

Fast CLI-backed evidence for code, docs, package, and security work.

1. Probe once: `bash ~/.claude/marketplaces/my-skills/skills/repo-power-tools/scripts/probe-tools.sh`
2. Read `references/tool-map.md`.
3. Prefer project-local binaries: `pnpm exec`, `npm exec`, `npx`, then globals.
4. Start with `rg` when an old name/path is known.
5. Use narrow, JSON/changed-only commands when possible.
6. Never delete from one tool signal; confirm callers/refs first.
