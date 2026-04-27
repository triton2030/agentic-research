---
name: skill-architect
description: >
  Use for Codex skill/agent design: skill, description, trigger, frontmatter, implicit invocation, matcher, split, merge, validation, openai.yaml. Design trigger surfaces and references. Route AGENTS/CLAUDE placement to `1instruction-layer`, runtime/folders to `1repo-shape`. Skip ordinary coding.
---

# Skill Architect

Design and repair skill/agent control surfaces by trigger surface, not by capability list.

## Role

Use this for skill descriptions, trigger boundaries, skill splitting/merging, reference layout, and validation design. Marketplace/live files may be edited only when the user asks implementation; otherwise emit prescriptions.

## First Read

- Current live skill or agent contract.
- Neighboring skills that might collide.
- `references/local-skill-contract.md` before recommending a new skill.
- `references/anti-patterns.md` and `references/audit-lenses.md` for critique.
- `references/workflow.md` for full audit sequence when needed.

## Codex Notes

- `name` and `description` are the trigger surface read before the body.
- `agents/openai.yaml` is UI/policy metadata; keep it aligned with SKILL.md.
- Validate drafts and installed copies with `quick_validate.py`.

## Workflow

1. Identify the user phrase cluster being caught.
2. Separate trigger surface from internal capability.
3. Define `Trigger when`, quoted phrases, and `Skip on` near-misses.
4. Keep body lean; move details to references.
5. Validate against should-trigger and should-not-trigger examples.

## Output Contract

For design: skill name, trigger surface, skip surface, body shape, references, validation prompts. For implementation: changed paths and validation evidence.

## Role Boundaries

- Does not own `_ops`, task-files, AGENTS/CLAUDE placement, hook or validator where the runtime supports its or validators where the runtime supports them, tool tool permission / approval policys / approval policy, or MCP shape.
- Route instruction placement to `1instruction-layer`; runtime/folder/tooling shape to `1repo-shape`.

## References

- [references/local-skill-contract.md](references/local-skill-contract.md)
- [references/anti-patterns.md](references/anti-patterns.md)
- [references/audit-lenses.md](references/audit-lenses.md)
- [references/output-shape.md](references/output-shape.md)
- [references/workflow.md](references/workflow.md)
