# Batch 1 — Tools & Navigation cluster

**Owner**: subagent (general-purpose), spawned by parent session
**Parent plan**: [README](README.md)

## Context

После md-tools-refactor (closed 2026-05-21):

- Backend: `experiments/md-embedding-server/scripts/navigator/` (parsing, graph, search, profile, refactor signals — единый Python package)
- Entry CLI scripts: `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` (uv shebang, in-repo)
- MCP server: `experiments/md-embedding-server/mcp/src/server.js` — единственный мост от агента к backend
- Skill folders (`~/.claude/skills/1md-{navigator,graph}/`, `~/.codex/skills/1md-{navigator,graph}/`) — **pure SKILL.md** (нет `scripts/`, нет symlinks). MCP version 0.5.x, 19 tools.

## Reference truth (read FIRST before touching anything)

1. `~/.claude/skills/1md-navigator/SKILL.md`
2. `~/.claude/skills/1md-graph/SKILL.md`
3. `/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/README.md`
4. `/Users/triton/Documents/GitHub/agentic-research/_ops/findings/2026-05-21-md-refactor-editorial-verification.md`

## Stale signals to fix

When you see any of these in your assigned files, fix or report:

**A. Stale script paths** — any `~/.claude/skills/1md-{navigator,graph}/scripts/...` or `~/.codex/skills/1md-{navigator,graph}/scripts/...`. Replace with `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` (in-repo) or refer to MCP tool by name.

**B. Outdated tool names / surface** — current MCP catalog has 19 tools (see mcp/README.md). Watch for:
- `md_overlaps`, `md_repeated_concepts`, `md_cluster` — folded into `md_audit` composite. CLI still has them, but MCP doesn't.
- `md_scan`, `md_check`, `md_doctor`, `md_cycles` — folded into `md_health`.
- `md_changed` — git-driven, CLI only, never MCP.
- `md_originality`, `md_owner_candidates`, `md_classify_section` — internal helpers, not exposed in MCP listTools.

**C. Stale version mentions** — `0.3.x` / `0.4.x` MCP version → `0.5.x`.

**D. Stale framing** — «skill ships scripts/», «bundled CLI in skill folder», «symlink in skill scripts/» — все wrong post-refactor. Skills are pure SKILL.md.

**E. Wrong tool routing** — if a skill claims «use md_X for Y» but Y belongs elsewhere now (cross-check against canonical SKILL.md).

**F. Codex-specific syntax** — Codex SKILL.md uses `$1xxx` prefix for skill refs in backticks (e.g. `` `$1md-graph` ``). Don't strip this if present; preserve runtime convention.

## Files in your batch

### Claude side
- `~/.claude/skills/1cli-tools/SKILL.md`
- `~/.claude/skills/1cli-tools/references/tool-map.md`
- `~/.claude/skills/1cli-tools/references/markdown-track.md`
- `~/.claude/skills/1start-here/SKILL.md`
- `~/.claude/skills/1repo-map/SKILL.md`
- `~/.claude/skills/1smart-simple/SKILL.md`

### Codex side
- `~/.codex/skills/1cli-tools/SKILL.md`
- `~/.codex/skills/1cli-tools/references/tool-map.md`
- `~/.codex/skills/1cli-tools/references/markdown-work.md`
- `~/.codex/skills/1start-here/SKILL.md`
- `~/.codex/skills/1start-here/agents/openai.yaml`
- `~/.codex/skills/1repo-map/SKILL.md`
- `~/.codex/skills/1repo-map/agents/openai.yaml`
- `~/.codex/skills/1smart-simple/SKILL.md`

## Edit rules

- **Minimal edits.** Don't rewrite for style. Fix what's actually stale or wrong.
- **Preserve voice and intent.** Tool routing, boundaries, language tone stay intact.
- **Edit in place** with the `Edit` tool (old_string + new_string). For new content use `Write`.
- **If unsure, leave + report.** When a mention is ambiguous (legitimately historical, intentional choice), don't change. List in your report.
- **Do NOT** run smoke, do NOT commit. Parent sweeps results.

## Expected output

Concise report (under 400 words) per file:
- File path
- Edits made — one line per edit: `<old> → <new>` (truncated)
- Edits skipped + reason
- Concerns / unclear cases / cross-skill consistency findings

Don't pad the report with what didn't need changing. Focus on what changed and what surprised you.
