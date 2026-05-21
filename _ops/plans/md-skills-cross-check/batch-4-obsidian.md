# Batch 4 — Obsidian (domain-specific) cluster

**Owner**: subagent (general-purpose), spawned by parent session
**Parent plan**: [README](README.md)

## Context

После md-tools-refactor (closed 2026-05-21):

- Backend: `experiments/md-embedding-server/scripts/navigator/`
- Entry CLI: `experiments/md-embedding-server/scripts/{md_navigator.py, md_graph.py}` (uv shebang, in-repo)
- MCP server: `experiments/md-embedding-server/mcp/src/server.js` — единственный мост
- Skill folders — **pure SKILL.md**. MCP version 0.5.x, 19 tools.

`1obsidian` — heaviest single skill in cross-check: 4 files × 2 platforms. Owns Obsidian-facing UX (callouts, Bases, kanban, wikilinks display, Meta Bind). Defers graph schema and dependency questions to `1md-graph`.

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

**D. Stale framing** — «skill ships scripts/», «bundled CLI» — wrong post-refactor.

**E. Wrong tool routing** — особенно проверь `1obsidian`'s boundary к `1md-graph`: should say "graph schema, dependency questions → `1md-graph`", не упоминать specific CLI commands (which may be stale).

**F. Codex syntax** — `$1xxx` skill ref prefix preserved.

**G. Obsidian-specific** — `1obsidian` describes how Obsidian UX интегрируется с graph (links, backlinks, Bases queries). Эти описания могут упоминать `1md-graph`'s capabilities. Проверь что description аккуратно отражает current surface — особенно `references/links-and-graph.md` который явно про graph integration.

## Files in your batch

### Claude side
- `~/.claude/skills/1obsidian/SKILL.md`
- `~/.claude/skills/1obsidian/references/links-and-graph.md`
- `~/.claude/skills/1obsidian/references/obsidian-primitives.md`
- `~/.claude/skills/1obsidian/references/root-base.md`

### Codex side
- `~/.codex/skills/1obsidian/SKILL.md`
- `~/.codex/skills/1obsidian/agents/openai.yaml`
- `~/.codex/skills/1obsidian/references/links-and-graph.md`
- `~/.codex/skills/1obsidian/references/obsidian-primitives.md`
- `~/.codex/skills/1obsidian/references/root-base.md`

## Edit rules

- **Minimal edits.** Don't rewrite for style.
- **Preserve voice and intent.** This is Obsidian UX expertise; preserve domain-specific language.
- **Edit in place** with `Edit` tool.
- **If unsure, leave + report.**
- **Do NOT** run smoke, do NOT commit.

## Expected output

Concise report (under 400 words) per file:
- File path
- Edits made — one line per edit
- Edits skipped + reason
- Concerns about `1obsidian` ↔ `1md-graph` / `1md-navigator` boundary integrity post-refactor
