# Batch 2 — Architecture & Instructions cluster

**Owner**: subagent (general-purpose), spawned by parent session
**Parent plan**: [README](README.md)

## Context

После md-tools-refactor (closed 2026-05-21):

- Backend: `experiments/md-embedding-server/scripts/navigator/` (parsing, graph, search, profile, refactor signals — единый Python package)
- Entry CLI scripts: `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` (uv shebang, in-repo)
- MCP server: `experiments/md-embedding-server/mcp/src/server.js` — единственный мост от агента к backend
- Skill folders — **pure SKILL.md** (no `scripts/`, no symlinks). MCP version 0.5.x, 19 tools.

## Reference truth (read FIRST)

1. `~/.claude/skills/1md-navigator/SKILL.md`
2. `~/.claude/skills/1md-graph/SKILL.md`
3. `/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/README.md`
4. `/Users/triton/Documents/GitHub/agentic-research/_ops/findings/2026-05-21-md-refactor-editorial-verification.md`

## Stale signals to fix

**A. Stale script paths** — `~/.claude/skills/1md-{navigator,graph}/scripts/...` or `~/.codex/skills/1md-{navigator,graph}/scripts/...`. Replace with `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` or refer to MCP tool by name.

**B. Outdated tool names / surface** — current MCP catalog has 19 tools (mcp/README.md):
- `md_overlaps`, `md_repeated_concepts`, `md_cluster` — folded into `md_audit`
- `md_scan`, `md_check`, `md_doctor`, `md_cycles` — folded into `md_health`
- `md_changed` — git-driven CLI, never MCP
- `md_originality`, `md_owner_candidates`, `md_classify_section` — internal, not in listTools

**C. Stale version mentions** — `0.3.x` / `0.4.x` → `0.5.x`.

**D. Stale framing** — «skill ships scripts/», «bundled CLI in skill folder» — wrong post-refactor.

**E. Wrong tool routing** — claim mismatch with canonical SKILL.md.

**F. Codex syntax** — `$1xxx` skill ref prefix is intentional Codex convention; preserve.

**G. Architecture claims** — these skills (`1instruction-layer`, `1folder-contract`, `1skill-architect`, `1planning`) могут содержать claims о том как graph/navigator ВПИСЫВАЮТСЯ в systems thinking, owner map, planning recipes. Эти claims могут быть concept-level и НЕ требовать тулово точности — judgment call. Если упоминание просто называет skill в routing matrix, проверь что routing верный после refactor.

## Files in your batch

### Claude side
- `~/.claude/skills/1instruction-layer/SKILL.md`
- `~/.claude/skills/1instruction-layer/references/language-quality-audit.md`
- `~/.claude/skills/1folder-contract/SKILL.md`
- `~/.claude/skills/1skill-architect/SKILL.md`
- `~/.claude/skills/1planning/SKILL.md`
- `~/.claude/skills/1planning/references/archive-and-folders.md`

### Codex side
- `~/.codex/skills/1instruction-layer/SKILL.md`
- `~/.codex/skills/1folder-contract/SKILL.md`
- `~/.codex/skills/1skill-architect/SKILL.md`
- `~/.codex/skills/1planning/SKILL.md`
- `~/.codex/skills/1planning/references/archive-and-folders.md`

## Edit rules

- **Minimal edits.** Don't rewrite for style. Fix what's stale or wrong.
- **Preserve voice and intent.** Routing, boundaries, language tone stay intact.
- **Edit in place** with `Edit` tool.
- **If unsure, leave + report.** Skills in this cluster live in concept-space — judgment call when concept-level mention isn't strictly wrong post-refactor.
- **Do NOT** run smoke, do NOT commit.

## Expected output

Concise report (under 400 words) per file:
- File path
- Edits made — one line per edit
- Edits skipped + reason
- Concerns / cross-skill inconsistency findings

Don't pad with what didn't need changing.
