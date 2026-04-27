---
name: 1repo-shape
description: >
  Use for Codex repo/runtime shape: folders, files, plugins, MCP/apps,
  subagents, validators, scripts, config, tool boundaries, guardrails. If the
  shape choice has strategic alternatives or hidden future constraints, route to
  `1strategy-discussion` before proposing the structure. Choose structural
  controls over wording when needed. Route skill triggers to `skill-architect`,
  instruction prose to `1instruction-layer`, task criteria to `1task-contract`.
---

# Repo Shape

Design repo and Codex runtime control surfaces: folders, files, AGENTS.md layers, skills, plugins, MCP/apps, subagents, validators, scripts, config, and tool boundaries.

## Role

Use this when behavior should be shaped structurally rather than by adding more prose. Prefer runtime checks, validators, scripts, folder ownership, plugin/MCP boundaries, or local instruction placement when those are stronger than reminder text.

## Planning Boundary

Repo/runtime shape is not a planning layer. Do not create folders, plugins,
scripts, validators, or config to compensate for an unresolved roadmap or
missing task contract. Route to the owner layer first, then choose structure if
structure is still the right lever.

## First Read

- Current repo tree and relevant config/instruction files.
- `AGENTS.md`, subtree instructions, `.codex/` surfaces, plugin/MCP/app config, validators, scripts, and existing subagents when relevant.
- `references/codex-control-surfaces.md` for Codex-shaped controls.

## Workflow

1. Name the failure mode or invariant.
2. If validator/script, folder rule, plugin/MCP/app boundary, subagent, skill,
   or instruction text are meaningfully different ways to reach the same goal,
   route to `1strategy-discussion` unless the route was already chosen.
3. Choose the strongest appropriate control surface.
4. Keep repo shape minimal and explicit about ownership.
5. Route prose placement to `1instruction-layer` and trigger design to `skill-architect`.

## Output Contract

Return chosen surface, owner, exact file/config target, expected behavior, and verification command.

## Role Boundaries

- Does not write task contracts or project roadmap.
- Does not design skill trigger surfaces; route to `skill-architect`.
- Does not place prose rules in AGENTS/CLAUDE unless paired with `1instruction-layer`.

## References

- [references/codex-control-surfaces.md](references/codex-control-surfaces.md)
