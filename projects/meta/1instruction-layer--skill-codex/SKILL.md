---
name: 1instruction-layer
description: >
  Use for instruction placement and routing: AGENTS.md, CLAUDE.md, root
  instructions, subtree rules, owner chain, default route, instruction conflict,
  fresh session. If multiple control surfaces could solve the user's goal or the
  proposed rule hides tradeoffs, route first to `1strategy-discussion`. Route
  skill triggers to `skill-architect`, runtime/folder/tooling shape to
  `1repo-shape`.
---

# Instruction Layer

Design where rules live across AGENTS.md, CLAUDE.md, subtree instructions, and skill routing.

## Role

Use this when the problem is instruction placement, precedence, owner routing, fresh-session comprehension, or conflict between instruction surfaces.

## Planning Boundary

Instruction files are not a planning layer. Do not fix a missing roadmap, task
contract, or substep by adding prose to AGENTS.md or CLAUDE.md. Route to the
owner layer first, then place only the minimal instruction that changes future
routing.

## First Read

- Root and relevant subtree instruction files.
- Live skill contracts affected by the routing.
- `references/system-building-principles.md` for control-surface principles.
- `references/instruction-guardrails.md` for Codex-specific instruction mechanics.

## Workflow

1. Identify the real rule and its owner.
2. If there are meaningful alternatives (root instruction, local instruction,
   skill, runtime guardrail) and the tradeoff is not already chosen, route to
   `1strategy-discussion` before placing the rule.
3. Choose the lightest surface that will refresh at the right moment.
4. Remove duplicates that do not change routing.
5. file write minimal routing text; avoid copying skill bodies into root docs.
6. Preserve fresh-session legibility.

## Output Contract

Name the owner, surface, exact routing rule, and any removed stale rule. If editing, report changed instruction paths.

## Role Boundaries

- Does not design skill trigger descriptions; route to `skill-architect`.
- Does not configure hook or validator where the runtime supports its or validators where the runtime supports them, tool tool permission / approval policys / approval policy, MCP, or folder topology; route to `1repo-shape`.
- Does not own plan or task files.

## References

- [references/system-building-principles.md](references/system-building-principles.md)
- [references/instruction-guardrails.md](references/instruction-guardrails.md)
