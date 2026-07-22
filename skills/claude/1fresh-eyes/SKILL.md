---
name: 1fresh-eyes
description: >
  Use when the user asks for native Claude critics/fresh eyes, or a material
  decision needs one independent expert challenge. Choose the named profile by
  strongest defeater. Generic cross-model review → `1codex`; UI screenshot
  critique → `screenshot-design`; questions only → `1expert-questions`.
---

# Свежие Глаза

## Результат

Независимая expert lens проверяет решение сверху и возвращает собственный
judgment. Critic атакует подход, не цель пользователя, и связывает finding с
alternative: better path, smaller probe, другой порядок, missing input или
честное `alternative not currently available`. `auditor` и `md-scout`
следуют своим native contracts.

Основной контекст владеет brief, проверкой evidence, синтезом и правками.
Subagent не получает вывод основного агента как oracle.

## Gate

Native Claude critic обязателен, когда пользователь прямо просит fresh eyes,
named critic, независимый аудит или parallel agents; также — перед material
решением, если соседний домен может опровергнуть локально зелёный результат.

Пропускай routine closeout, low-stakes правку, skill packaging и текущую сессию,
уже работающую как subagent. Generic или cross-model независимый review
принадлежит `1codex`; подключай оба маршрута только когда отдельно нужны
model-family и professional lenses.

## Lens Chooser

| Strongest defeater | `Agent` subagent_type |
|---|---|
| viability, adoption, economics, trust | `business-critic` |
| feasibility, dependencies, tests, DX | `developer-critic` |
| boundaries, ownership, conceptual integrity | `architecture-critic` |
| sequence, opportunity cost, done-state trajectory | `smith` |
| acceptance and stated evidence | `auditor` |
| broad Markdown retrieval and coverage | `md-scout` |

Artifact type does not choose the lens. Ask: what can make this result wrong
even if its local checks pass? Add a second profile only when another independent
domain judgment can also change the decision.

## Default Path

1. **Verify runtime.** Confirm the exact named profile is visible to the native
   `Agent` tool. Do not impersonate a missing profile through
   `general-purpose`.
2. **Choose the smallest independent lens.** Give exact artifact paths and the
   decision that depends on review. If split is unclear, read
   [`references/split-patterns.md`](references/split-patterns.md).
3. **Brief without priming.** State desired result, why it matters, sources,
   evidence/unknowns, scope and forbidden side effects. Do not restate the
   agent's role, prescribe its method or suggest a verdict. Read
   [`references/brief-templates.md`](references/brief-templates.md).
4. **Spawn through `Agent`.** Use the exact `subagent_type`. Run several
   profiles concurrently only for different lenses or disjoint artifacts;
   same-lens duplicate votes are noise.
5. **Repair input, not judgment.** Correct facts or scope through
   `SendMessage(to: agent_id|name)` in the same retained agent stream; a changed
   question, lens or independence requirement needs a new clean agent. Details:
   [`references/steering-and-dialogue.md`](references/steering-and-dialogue.md).
6. **Verify and synthesize.** Preserve native verdicts, disagreement, evidence
   strength and alternatives. Do not vote or silently filter. Classification:
   [`references/synthesis-and-evidence.md`](references/synthesis-and-evidence.md).
7. **Act from main context.** Accept a finding only after its cited evidence
   supports the claim; edits and final validation stay with the main owner.

## Invariants

- Fresh eyes here means native Claude `Agent`, not CLI/MCP review.
- Installed agent files do not prove runtime-visible identity; callable schema
  wins.
- Briefs define the decision and boundaries, not the expected conclusion.
- Steering changes input, never the native role, method or desired verdict.
- `md-scout` owns evidence packets, not IA/canon/business decisions.
- Consensus is not proof; minority evidence can be the strongest signal.

## Готово / Стоп

Готово, когда lens выбрана по strongest defeater, brief не подсказывает вывод,
evidence и alternatives проверены, disagreement сохранён и owner action явен.
Остановись, если `Agent` недоступен; точный requested profile не виден; два
follow-up не сужают решение; либо outputs уже синтезированы.
