---
name: 1skill-architect
description: >
  Use when designing or substantially revising a Claude skill/control surface
  before implementation: decide owner, trigger, collisions, and
  outcome-vs-workflow shape. Create/update/validate → `skill-creator`.
---

# Skill Architect

## Результат

Нужная экспертиза возвращается в момент действия через один правильный surface,
а его contract меняет наблюдаемое поведение агента без лишнего process
scaffolding. **Moment-fit** — surface найден и активирован в нужный момент —
корневая добродетель: сильное содержимое, которое не загрузилось, не существует
для агента.

Точные значения **bold-терминов** бери из [`GLOSSARY.md`](GLOSSARY.md) только
при ambiguity или правке vocabulary.

## Surface И Admission

Surface type и owner должны быть определены до wording:

- `skill` возвращает повторяемое профессиональное суждение или tool workflow;
- `agent` изолирует независимую роль или context stream;
- `hook-as-code` детерминированно наблюдает или ограничивает runtime event;
- `instruction-text` задаёт устойчивое default-правило;
- "не новый surface" — правильный результат, если ближайший owner уже достаточен.

Новый или существенно переписанный surface оправдан только когда есть
повторяемый момент, отдельный trigger, наблюдаемый failure pattern и **Delta**,
которую агент не выводит надёжно из задачи, текущего контекста и ближайшего
owner. Generic competence prompt budget не получает.

## Body Shape

**Outcome/decision contract — default** для judgment, design и quality skills.
Он держит желаемое состояние, главный decision standard, материальные
boundaries, falsifiable evidence, условные routes и stop/handoff. Модель сама
выбирает путь.

**Workflow contract — исключение** для хрупкой, необратимой, safety-critical или
tool-bound работы, где порядок сам является частью корректности. Оставляй только
последовательность, отсутствие которой воспроизводит конкретный failure.

**Micro-router** означает компактный contract и conditional disclosure, а не
обязательный алгоритм рассуждения. Не превращай `SKILL.md` в учебник и не
маршрутизируй к чтению всех references.

## Discovery Contract

Для model-invoked Claude skill `description` участвует в discovery до загрузки
body:

- opening называет observable condition и важную Delta;
- trigger описывает момент, не каталог capabilities;
- adjacent near-miss принадлежит одному owner-у;
- description остаётся указателем к body, не его конспектом.

Полный live candidate canvas и фактически видимый prompt surface сильнее
изолированной формулировки. Shared trigger phrase — collision/ownership signal,
не задача literal dedupe. Соседей обозначай bare pointer-ом.

## Evidence Gate

Evidence должен быть способен опровергнуть материальный claim изменения.
Global, broad, frequent, risky, collision-prone или already-regressed surface
повышает требуемую различающую силу, но не создаёт фиксированный test package.
Baseline нужен для relative-improvement claim, near-miss cases — для routing
claim, projection sync — для реально существующих copies, observable output
assertion — для behavior claim. Structural validity и prompt visibility не
доказывают полезное поведение.

Для Opus 5 и Fable 5 сначала удаляй obsolete scaffolding, повторы и generic
brevity. Жёсткий workflow возвращай только под order-sensitive failure;
model/effort/long-run правила остаются в model и platform owners, не в portable
skill core.

## Failure Modes — Brooks Lens

Быстрый self-check (полный каталог — [`references/anti-patterns.md`](references/anti-patterns.md)):

- **Central model violation** — `description` перечисляет capabilities вместо
  trigger surface.
- **Shallow abstraction** — `description` пересказывает body и не экономит
  чтение реализации.
- **Procedure by default** — judgment skill навязывает стадии без
  order-sensitive failure mode.
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
  при создании / существенной правке Claude skill или `description`.
- [`references/local-skill-contract.md`](references/local-skill-contract.md) —
  когда вывод включает "нужен локальный skill" или "этот skill переписать".
- [`references/anti-patterns.md`](references/anti-patterns.md) — широкий аудит
  или surface расползается в систему.
- [`references/deep-audit.md`](references/deep-audit.md) — только для глубокого
  аудита skill-ландшафта / runtime / control surface: восемь шагов, lenses,
  output shape.

## Boundaries And Handoff

- `skill-creator` owns creation/scaffolding, packaging, structural validation,
  forward testing, measured benchmark и prompt eval; его tool-specific steps не
  становятся обязательной формой skill body.
- `1skill-architect` owns design-time: surface, trigger, body shape,
  candidate-canvas/collision, owner и evidence gate до реализации.
- Task contract / current path -> `1planning`.
- Prose, folder placement, instruction wording -> `1instruction-layer`.
- Runtime settings, permissions, hooks, CLI wiring -> live settings/hook pass.
- Independent context-free structural critique -> `1fresh-eyes` when the change
  is load-bearing.
