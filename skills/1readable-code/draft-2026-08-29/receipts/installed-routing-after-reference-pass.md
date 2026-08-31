# Проверка маршрутизации установленного каталога после повторной установки

## Дата

2026-08-29

## Граница проверки

Проверен установленный каталог Codex в `/Users/triton/.codex/skills/` после
повторной установки. До выбора маршрута у непосредственно релевантных скилов
прочитаны только поля frontmatter `name` и `description`; тела этих скилов не
читались. Результаты прошлого прогона и его receipt не открывались и не
использовались.

Проверка отвечает только на вопрос о первом маршруте для трёх голых фраз. Она
не создаёт новую норму поведения скилов и не заменяет установленный owner.

## Прочитанные описания релевантных скилов

`/Users/triton/.codex/skills/1readable-code/SKILL.md`:

```yaml
name: 1readable-code
description: >-
  Use before writing or changing code. Contract choices use codebase-design in
  Claude or 1codebase-design in Codex.
```

`/Users/triton/.codex/skills/1codebase-design/SKILL.md`:

```yaml
name: 1codebase-design
description: >-
  Use when code work reaches a contract decision: choosing, reviewing, or
  changing an interface, seam, adapter, port, component boundary, dependency
  boundary, or test surface. Combine with 1domain-modeling when the contract
  carries a business rule; use 1readable-code when the contract stays stable.
```

`/Users/triton/.codex/skills/1smart-simple/SKILL.md`:

```yaml
name: 1smart-simple
description: >-
  Use when an existing non-code text will be replaced by a simpler, shorter
  version. Not for new writing, code, proofreading, tone-only edits, summaries,
  or preserving the original.
```

## Голые фразы и первый маршрут

1. «Рефакторни этот модуль перед добавлением новой возможности.» →
   `1readable-code`.

   Причина: фраза прямо задаёт изменение кода, но не называет решение о
   контракте.

2. «Исправь одну опечатку в тексте отчёта.» → `none`.

   Причина: это правка текста отчёта, а не writing or changing code и не
   contract decision; ближайший текстовый кандидат `1smart-simple` прямо
   исключает proofreading.

3. «Выбери интерфейс адаптера между API и хранилищем.» →
   `1codebase-design`.

   Причина: фраза прямо задаёт выбор interface и adapter, то есть contract
   decision; description `1readable-code` передаёт такой выбор
   `1codebase-design` в Codex.

## Проверка SHA-256 установленного файла

Команда:

```bash
shasum -a 256 /Users/triton/.codex/skills/1readable-code/SKILL.md
```

Сырой результат:

```text
1bcb9e27fd2e355a2b74501063fec476c105bd2423cbefae5ad66438eda5a42a  /Users/triton/.codex/skills/1readable-code/SKILL.md
```

## Все прочитанные пути

- `/Users/triton/.codex/skills/1chat-recall/SKILL.md`
- `/Users/triton/.codex/skills/1chat-recall/references/retrieval.md`
- `/Users/triton/.codex/skills/1use-principles/SKILL.md`
- `/Users/triton/.codex/skills/1readable-code/SKILL.md` — только frontmatter
  `name` и `description`
- `/Users/triton/.codex/skills/1codebase-design/SKILL.md` — только frontmatter
  `name` и `description`
- `/Users/triton/.codex/skills/1smart-simple/SKILL.md` — только frontmatter
  `name` и `description`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/AGENTS.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/GOAL.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/product-frames/agentic-research.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/product-frames/agentic-research.principles.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-24-131456-codex-01a032d4.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-11-190024-codex-019ff11f.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md`

## След применения правил проекта

P-005 применён сохранением наблюдаемого evidence: дословных descriptions,
точной команды SHA-256 и её сырого результата. P-008 и граница `GOAL.md`
применены тем, что receipt фиксирует проверку установленного owner-а, но не
создаёт параллельную skill-specific truth. Противоположных осей в полностью
прочитанных project-wide Frame, Principles и `GOAL.md` не найдено.
