# Batch 3 — Decision & Verification cluster

**Owner**: subagent (general-purpose), spawned by parent session
**Parent plan**: [README](README.md)

## Context

После md-tools-refactor (closed 2026-05-21):

- Backend: `experiments/md-embedding-server/scripts/navigator/`
- Entry CLI: `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` (uv shebang, in-repo)
- MCP server: `experiments/md-embedding-server/mcp/src/server.js` — единственный мост
- Skill folders — **pure SKILL.md** (no `scripts/`, no symlinks). MCP version 0.5.x, 19 tools.

## Reference truth (read FIRST)

1. `~/.claude/skills/1md-navigator/SKILL.md`
2. `~/.claude/skills/1md-graph/SKILL.md`
3. `/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/README.md`
4. `/Users/triton/Documents/GitHub/agentic-research/_ops/findings/2026-05-21-md-refactor-editorial-verification.md`

## Stale signals to fix

**A. Stale script paths** — `~/.claude/skills/1md-{navigator,graph}/scripts/...` or `~/.codex/skills/1md-{navigator,graph}/scripts/...`. Replace with `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` or refer to MCP tool by name.

**B. Outdated tool names / surface**:
- `md_overlaps`, `md_repeated_concepts`, `md_cluster` — folded into `md_audit`
- `md_scan`, `md_check`, `md_doctor`, `md_cycles` — folded into `md_health`
- `md_changed` — git-driven CLI, never MCP
- `md_originality`, `md_owner_candidates`, `md_classify_section` — internal

**C. Stale version mentions** — `0.3.x` / `0.4.x` → `0.5.x`.

**D. Stale framing** — «skill ships scripts/», «bundled CLI» — wrong.

**E. Wrong tool routing** — mismatch with canonical SKILL.md.

**F. Codex syntax** — `$1xxx` skill ref prefix preserved.

**G. Verification framing** — `1work-review`, `1ia-audit`, `1assumption-audit`, `1findings` могут описывать «use navigator to surface evidence» / «use graph to check obligations». Это conceptual claims — проверь что они отражают current capabilities, не legacy.

## Files in your batch

### Claude side
- `~/.claude/skills/1strategy/SKILL.md`
- `~/.claude/skills/1strategy-docs/SKILL.md`
- `~/.claude/skills/1work-review/SKILL.md`
- `~/.claude/skills/1ia-audit/SKILL.md`
- `~/.claude/skills/1assumption-audit/SKILL.md`
- `~/.claude/skills/1findings/SKILL.md`

### Codex side
- `~/.codex/skills/1strategy/SKILL.md`
- `~/.codex/skills/1strategy-docs/SKILL.md`
- `~/.codex/skills/1work-review/SKILL.md`
- `~/.codex/skills/1work-review/agents/openai.yaml`
- `~/.codex/skills/1ia-audit/SKILL.md`
- `~/.codex/skills/1ia-audit/agents/openai.yaml`
- `~/.codex/skills/1assumption-audit/SKILL.md`
- `~/.codex/skills/1findings/SKILL.md`

## Edit rules

- **Minimal edits.** Don't rewrite for style.
- **Preserve voice and intent.**
- **Edit in place** with `Edit` tool.
- **If unsure, leave + report.**
- **Do NOT** run smoke, do NOT commit.

## Expected output

Concise report (under 400 words) per file:
- File path
- Edits made — one line per edit
- Edits skipped + reason
- Concerns / cross-skill consistency findings
