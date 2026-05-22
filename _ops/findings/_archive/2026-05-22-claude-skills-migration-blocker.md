# Claude skills migration blocker — 2026-05-22

## Verdict

resolved-after-user-authorization

## Reason

This was a valid blocker under the earlier repo instruction. The current
`AGENTS.md` adds a narrow exception: Claude skills may be edited from Codex
only by explicit user request and through `1skill-architect`. The user gave
that explicit request for this goal, so this finding is superseded for
Claude skill files only.

## Evidence

Stale MCP-era refs remain in `/Users/triton/.claude/skills/**`, including:

- `1md-navigator` / `1md-graph`
- `1ia-audit`
- `1instruction-layer`
- `1planning`
- `1strategy`
- `1work-review`
- `1assumption-audit`
- `1smart-simple`
- `1skill-architect`
- `1folder-contract`
- `1cli-tools/references`

Probe:

```bash
rg 'md_[a-z_]+\(\{|mcp__md-mcp|md-mcp|MD_NAVIGATOR_SCRIPT|md_navigator\.py|md_graph\.py' /Users/triton/.claude/skills
```

## Resolution

Claude-side skill migration was completed in
`_ops/findings/2026-05-22-claude-skills-cli-migration.md`. The boundary still
stands for `CLAUDE.md`, `.claude/settings*`, hooks and runtime configs unless
the user gives a separate explicit request.
