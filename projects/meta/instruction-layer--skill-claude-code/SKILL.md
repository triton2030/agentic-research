---
name: instruction-layer
description: >
  Use this skill whenever a rule must be placed or routed in instructions: "AGENTS.md", "CLAUDE.md", "куда положить правило", "root instruction", "routing", "owner-chain", "instruction conflict", "fresh session", "правило в инструкции", "placement", "default route", "subtree instructions", "что должен читать агент". Designs instruction surfaces and precedence. Skip skill trigger design, task criteria, plan strategy, and runtime hooks/settings.
---

# Instruction Layer

Design where rules live across AGENTS.md, CLAUDE.md, subtree instructions, and skill routing.

## Role

Use this when the problem is instruction placement, precedence, owner routing, fresh-session comprehension, or conflict between instruction surfaces.

## First Read

- Root and relevant subtree instruction files.
- Live skill contracts affected by the routing.
- `references/system-building-principles.md` for control-surface principles.
- `references/instruction-guardrails.md` for Claude Code-specific instruction mechanics.

## Workflow

1. Identify the real rule and its owner.
2. Choose the lightest surface that will refresh at the right moment: root instruction, local instruction, skill, or runtime guardrail.
3. Remove duplicates that do not change routing.
4. Write minimal routing text; avoid copying skill bodies into root docs.
5. Preserve fresh-session legibility.

## Output Contract

Name the owner, surface, exact routing rule, and any removed stale rule. If editing, report changed instruction paths.

## Role Boundaries

- Does not design skill trigger descriptions; route to `skill-architect`.
- Does not configure hooks, permissions, MCP, or folder topology; route to `repo-shape`.
- Does not own plan or task files.

## References

- [references/system-building-principles.md](references/system-building-principles.md)
- [references/instruction-guardrails.md](references/instruction-guardrails.md)
