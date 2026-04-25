---
name: repo-shape
description: >
  Use for Codex repo/runtime shape: folders, files, plugins, MCP/apps, subagents, validators, scripts, config, tool boundaries, guardrails. Choose structural controls over wording when needed. Route skill triggers to `skill-architect`, instruction prose to `instruction-layer`, task criteria to `task-contract`.
---

# Repo Shape

Design repo and Codex runtime control surfaces: folders, files, AGENTS.md layers, skills, plugins, MCP/apps, subagents, validators, scripts, config, and tool boundaries.

## Role

Use this when behavior should be shaped structurally rather than by adding more prose. Prefer runtime checks, validators, scripts, folder ownership, plugin/MCP boundaries, or local instruction placement when those are stronger than reminder text.

## First Read

- Current repo tree and relevant config/instruction files.
- `AGENTS.md`, subtree instructions, `.codex/` surfaces, plugin/MCP/app config, validators, scripts, and existing subagents when relevant.
- `references/codex-control-surfaces.md` for Codex-shaped controls.

## Workflow

1. Name the failure mode or invariant.
2. Choose the strongest appropriate control surface: validator/script, folder rule, plugin/MCP/app boundary, subagent, skill, or instruction text.
3. Keep repo shape minimal and explicit about ownership.
4. Route prose placement to `instruction-layer` and trigger design to `skill-architect`.

## Output Contract

Return chosen surface, owner, exact file/config target, expected behavior, and verification command.

## Role Boundaries

- Does not write task contracts or project strategy.
- Does not design skill trigger surfaces; route to `skill-architect`.
- Does not place prose rules in AGENTS/CLAUDE unless paired with `instruction-layer`.

## References

- [references/codex-control-surfaces.md](references/codex-control-surfaces.md)
