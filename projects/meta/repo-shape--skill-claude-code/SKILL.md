---
name: repo-shape
description: >
  Use this skill whenever repo/runtime shape is the object: "папки", "структура репы", "hooks", "permissions", "MCP", "settings.json", "tools", "validators", "guardrail", "runtime", "файловая форма", "folder ownership", "repo shape", "Claude Code config", "permission rule". Designs folders, hooks, permissions, validators, and tool boundaries. Skip skill descriptions, task criteria, project strategy, and prose-only instruction placement.
---

# Repo Shape

Design repo and runtime control surfaces: folders, files, hooks, permissions, MCP, validators, and tool boundaries.

## Role

Use this when the system shape is enforced by filesystem topology or Claude Code runtime mechanics rather than instruction wording alone.

## First Read

- Current repo tree and relevant config files.
- `.claude/settings.json`, `.claude/settings.local.json`, or global settings when relevant.
- Existing hooks, validators, scripts, and MCP config.
- `references/claude-runtime-guardrails.md` for Claude Code runtime mechanisms.

## Workflow

1. Name the failure mode or desired invariant.
2. Choose the strongest appropriate layer: hook, permission, validator, folder rule, MCP scope, skill, or instruction text.
3. Prefer structural enforcement over wording when failure cost is high.
4. Keep repo shape minimal and explain ownership.

## Output Contract

Return the chosen control surface, owner, exact config/file target, expected behavior, and verification command.

## Role Boundaries

- Does not write task contracts or project strategy.
- Does not design skill trigger surfaces; route to `skill-architect`.
- Does not place prose rules in AGENTS/CLAUDE unless paired with `instruction-layer`.

## References

- [references/claude-runtime-guardrails.md](references/claude-runtime-guardrails.md)
