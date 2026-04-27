---
name: skill-architect
description: >
  Use this skill whenever designing or repairing skills, agents, or their triggers: "скилл", "skill", "description", "trigger", "не срабатывает", "overtrigger", "undertrigger", "разрезать скил", "создать skill", "обновить SKILL.md", "matcher", "implicit invocation", "frontmatter", "router", "agent design". Designs trigger surfaces, boundaries, references, and validation. Skip ordinary coding, task criteria, root instruction placement, and runtime hooks.
---

# Skill Architect

Design and repair skill/agent control surfaces by trigger surface, not by capability list.

## Role

Use this for skill descriptions, trigger boundaries, skill splitting/merging, reference layout, validation design, and agent (subagent) design — persona, three-category vocabularies, swarm-safety, fallback patterns. Same discipline applies to skills, agents, and hook-scripts: design by trigger surface (or invocation surface), not by capability list. Marketplace/live files may be edited only when the user asks implementation; otherwise emit prescriptions.

## First Read

- Current live skill or agent contract.
- Neighboring skills that might collide.
- `references/local-skill-contract.md` before recommending a new skill.
- `references/anti-patterns.md` and `references/audit-lenses.md` for critique.
- `references/workflow.md` for full audit sequence when needed.

## Workflow

1. Identify the user phrase cluster being caught.
2. Separate trigger surface from internal capability.
3. Define `Trigger when`, quoted phrases, and `Skip on` near-misses.
4. Keep body lean; move details to references.
5. Validate against should-trigger and should-not-trigger examples.

## Output Contract

For design: skill name, trigger surface, skip surface, body shape, references, validation prompts. For implementation: changed paths and validation evidence.

## Role Boundaries

- Does not own `_ops`, task-files, AGENTS/CLAUDE placement, hooks, permissions, or MCP shape.
- Route instruction placement to `1instruction-layer`; runtime/folder/tooling shape to `1repo-shape`.

## Surface Choice

Первый шаг любого аудита/дизайна — назвать surface: skill / agent / hook-as-code / instruction-text. У них разный runtime, разная discipline, разное место жизни. Не смешивать «по аналогии». Если паттерн живёт как агенты в `~/.claude/agents/` — новый член семьи тоже агент, не скил. Если паттерн runtime-enforced (хук) — не клади его в инструкционный текст.

## Структурная критика — Brooks-оптика

Применяю к design скилов / агентов / hook-скриптов:

- **Central model violation** — description перечисляет capabilities вместо trigger surface (моментов, фраз, состояний)
- **Shallow abstraction** — description ≈ paraphrase body; интерфейс не экономит чтение реализации
- **Configuration explosion** — N пересекающихся скилов на ту же фразовую поверхность
- **Cargo cult creation** — новый артефакт «по аналогии» без verify, что он ловит чего не ловят существующие

**Stop-rule:** если не могу назвать trigger surface скила/агента в одной фразе — это и есть находка, не дописывай description.

**Subagent fallback:** при сложном случае или когда нужен независимый контекст-свободный взгляд — `brooks` (опционально, не дефолт).

Полный словарь: `knowledge/wisdom-structural-critique.md`.

## References

- [references/local-skill-contract.md](references/local-skill-contract.md)
- [references/anti-patterns.md](references/anti-patterns.md)
- [references/audit-lenses.md](references/audit-lenses.md)
- [references/output-shape.md](references/output-shape.md)
- [references/workflow.md](references/workflow.md)
