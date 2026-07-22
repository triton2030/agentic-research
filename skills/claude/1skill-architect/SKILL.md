---
name: 1skill-architect
description: >
  До реализации skill/control surface: owner, trigger/invocation, collision,
  body topology. Create/update/validate — `skill-creator`.
---

Скил существует, чтобы вернуть нужную экспертизу в момент действия. **Moment-fit**
— surface найден и активирован в нужный момент — корневая добродетель; каждый ход
ниже служит ей. Скил с верным содержанием, но не найденный в свой момент, не
существует. Точные значения **bold-терминов** бери из
[`GLOSSARY.md`](GLOSSARY.md) только при ambiguity или правке vocabulary. Этот
скил применяет к себе то, что предписывает: trigger surface в `description`,
micro-router в теле, depth в references.

Начинай с минимального hot path: результат, критерии успеха, scope/authority,
evidence, нужные reference routes, validation и stop. Явно фиксируй authority,
required output и side-effect boundary только там, где они меняют поведение.
Перед добавлением правила удаляй obsolete scaffolding, повторы и generic
brevity. Порядок фиксируй лишь там, где он сам является требованием: surface до
текста, proof/reuse до нового surface, description до body.

## Default Path — Спроектировать / Починить Один Surface

1. **Surface первым.** Выбери `skill`, `agent`, `hook-as-code`,
   `instruction-text` или "не новый surface". У них разный runtime, owner и
   validation; ошибка surface не лечится хорошим письмом. Если выбран не skill,
   зафиксируй owner и передай реализацию его live surface.
2. **Reuse + proof + Delta gate.** Новый или существенно переписанный surface
   требует:
   повторяемый ход, отдельный trigger, реальный паттерн сбоя, почему это не
   закрывают существующие instructions/criteria/runtime/script, и чем
   недостаточно ближайшее покрытие. В skill входит только **Delta** —
   неочевидное правило, failure mode или профессиональный ход, который агент не
   выведет надёжно из задачи, текущего контекста и ближайшего owner. Generic
   competence не является Delta.
3. **Description = discovery contract.** Для model-invoked Claude skill
   `description` — discovery contract: body ещё не виден, а runtime может усечь
   discovery metadata. Поэтому первая фраза
   держит use case и boundary. Пиши в две фазы: архитектура
   (**Condition x Delta**, trigger-surface-not-capability, near-miss) ->
   compression (указатель к телу, не выжимка).
4. **Canvas audit.** На authoring-time читай полный live candidate set и отдельно
   проверяй видимый prompt surface; full co-presence не гарантирована. Не
   пересказывай соседей: bare pointer (`1planning`, `1instruction-layer`) обычно
   лучше. Повтор trigger-фразы = collision, а не дубль, решай ownership.
5. **Body = micro-router.** `SKILL.md` держит root virtue, default path, важные
   branches, conditional reference routes, validation и stop. Не превращай body
   в учебник и не делай маршрут "читать все references".
6. **Evidence gate по риску.** Minimum для малой правки; strict для global,
   broad, frequent, risky, collision-prone или already-regressed surfaces. Здесь
   выбери bar и acceptance criteria; measurement mechanics передай
   `skill-creator`.

Детали шагов 2–6 (двухфазный method, canvas audit, limits, eval gates, checks,
source discipline) — [`references/claude-skill-authoring.md`](references/claude-skill-authoring.md).
Контракт локального skill — [`references/local-skill-contract.md`](references/local-skill-contract.md).

## Failure Modes — Brooks Lens

Быстрый self-check (полный каталог — [`references/anti-patterns.md`](references/anti-patterns.md)):

- **Central model violation** — `description` перечисляет capabilities вместо
  trigger surface.
- **Shallow abstraction** — `description` пересказывает body и не экономит
  чтение реализации.
- **Configuration explosion** — несколько surfaces делят один момент без owner.
- **Cargo-cult creation** — новый surface "по аналогии" без proof/reuse gate.
- **Description-in-vacuum** — правка одного `description` без audit полного live
  candidate set и видимого prompt surface.

**Stop-rule:** не можешь назвать trigger surface одной фразой — это находка, не
дописывай `description`.

## Routes

- [`GLOSSARY.md`](GLOSSARY.md) — только если термин неоднозначен или меняется
  vocabulary.
- [`references/claude-skill-authoring.md`](references/claude-skill-authoring.md) —
  default при создании / существенной правке Claude skill или `description`.
- [`references/local-skill-contract.md`](references/local-skill-contract.md) —
  когда вывод включает "нужен локальный skill" или "этот skill переписать".
- [`references/anti-patterns.md`](references/anti-patterns.md) — широкий аудит
  или surface расползается в систему.
- [`references/deep-audit.md`](references/deep-audit.md) — только для глубокого
  аудита skill-ландшафта / runtime / control surface: восемь шагов, lenses,
  output shape.

## Boundaries And Handoff

- `skill-creator` owns creation/scaffolding, packaging, structural validation,
  forward testing, measured benchmark и prompt eval.
- `1skill-architect` owns design-time: surface, trigger, body shape,
  candidate-canvas/collision, owner и evidence gate до реализации.
- Task contract / current path -> `1planning`.
- Prose, folder placement, instruction wording -> `1instruction-layer`.
- Runtime settings, permissions, hooks, CLI wiring -> live settings/hook pass.
- Independent context-free structural critique -> `1fresh-eyes` when the change
  is load-bearing.
