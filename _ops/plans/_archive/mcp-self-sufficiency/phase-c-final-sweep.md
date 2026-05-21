# Phase C — Final sweep + verification + commits

**Owner**: parent session (me)
**Parent plan**: [README](README.md)
**Depends on**: Phases A, B1, B2, B3, B4 done

## Цель

Verify the whole mcp-self-sufficiency landed clean; commit per-phase; cross-runtime check.

## Steps

### C.1 — Backend smoke regression

```bash
cd /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp
npm run smoke
```

Expect: 100% pass with ~37 assertions (was 24).

### C.2 — Cross-runtime tools listing

Verify fresh Claude session and Codex session see all 27 tools via MCP:
- Manual: open new session in each, ask «list md_ tools».
- Or scripted: `claude mcp list` shows md-mcp Connected; Codex `config.toml` has block.

### C.3 — Final grep sweep

Check for stale references after all batches:

```bash
# Stale skill-folder script paths anywhere
grep -rln "skills/1md-navigator/scripts\|skills/1md-graph/scripts" \
  ~/.claude/skills ~/.codex/skills /path/to/repo \
  --include="*.md" --include="*.py" --include="*.js" --include="*.yaml" \
  --exclude-dir=_archive --exclude-dir=node_modules

# Old MCP version (0.3.x / 0.4.x / 0.5.x) — should all be 0.6.x now
grep -rn "0\.3\.\|0\.4\.\|0\.5\." ~/.claude/skills ~/.codex/skills

# Bare CLI invocations as primary (should be MCP-first wherever exists)
grep -rn "md_navigator\.py search\|md_navigator\.py read-related\|md_navigator\.py status\|md_navigator\.py impact\|md_graph\.py preflight\|md_graph\.py impact\|md_graph\.py deps\|md_graph\.py health\|md_graph\.py cycles\|md_graph\.py check\|md_graph\.py scan\|md_graph\.py changed" \
  ~/.claude/skills ~/.codex/skills
```

Acceptable remaining (CLI-only):
- `md_navigator.py index` (mutating; CLI fallback for setup)
- `md_navigator.py profile-sections` (mutating; expensive op)
- `md_graph.py init`, `md_graph.py strip` (mutating)
- Bare CLI inside `references/setup.md` (entry script invocation framing)

Not acceptable: `md_search` / `md_preflight` / `md_health` / etc. shown as bare CLI when MCP equivalent exists.

### C.4 — Spawn `1md-navigator` audit on the corpus

Run `md_audit knowledge/` itself and verify it surfaces no new IA breakage from skill rewrites.

### C.5 — Commits (per phase)

Recommended commit shape:

1. **Archive + new plan structure**: `Archive completed plans + plan mcp-self-sufficiency`
2. **Phase A backend**: `Expand MCP to 27 self-sufficient tools (v0.6.0)` — touches `mcp/src/**`, `mcp/test/smoke.js`, `mcp/README.md`, `mcp/package.json`
3. **Phase B (one combined commit OR four per-batch)**: `Rewrite 16 SKILL.md as MCP overlay (B1-B4 batches)` — touches files outside repo, not git-tracked; commit message documents what changed
4. **Roadmap update**: `Mark mcp-self-sufficiency complete in roadmap` — touches `_ops/PROJECT-ROADMAP.md`

### C.6 — Update PROJECT-ROADMAP

Active fronts updated:
- ✅ mcp-self-sufficiency done
- Remaining: knowledge-description-cleanup (if still open)
- Any new fronts surfaced by subagents (cross-skill consistency findings)

### C.7 — Update `_ops/project-graph.md`

Если что-то поменялось в graph (depends-on / related-when / veto-class) после refactor — отразить. Likely no change in this phase.

## Definition of done (Phase C)

- Smoke 100% pass
- Cross-runtime check confirmed (Claude + Codex see surface)
- No stale references in grep sweep
- All commits landed
- PROJECT-ROADMAP updated
- README of mcp-self-sufficiency marks complete

## After Phase C

Archive `_ops/plans/mcp-self-sufficiency/` to `_ops/plans/_archive/mcp-self-sufficiency/`.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Subagent for Phase A leaves wrappers partial / smoke fails | Don't launch B1-B4 until A confirmed pass |
| B subagents make inconsistent overlay style across skills | C.4 audit catches; if drift, single-pass normalizer subagent |
| Mutating guards bypass-able by agent | Test in C with explicit no-confirm invocation; if dry_run/confirm not enforced, fix in backend before commit |
| Cross-runtime check fails (Claude or Codex doesn't pick up new tools) | Verify both have current MCP registered; restart sessions; if persistent, check version bump propagated |
