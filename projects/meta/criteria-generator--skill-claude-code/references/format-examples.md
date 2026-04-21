# Format Examples

Worked examples of `criteria-generator` output. Use them for shape, not content.

There are two public shapes:

- `contract` mode — thin augmented prompt with `Must`, optional `Must not`, and `Verification protocol`.
- `strategy-trace` mode — compact chain from `_ops/` to the checked target, plus a verdict and one next move.

The visible contract should stay thin: usually 2-4 `Must`, 0-2 `Must not`, and 1-3 verification steps.

Every `Must` carries `Anchored in:`. When the task has no strategic map to anchor against, use `local-only — <reason>` instead of silently dropping the field. The examples below have no attached `_ops/` by design, so they use `local-only` — in a real repo with `_ops/1-NORTH-STAR.md` prefer anchors like `_ops/1-NORTH-STAR.md#acceptance-criteria` or `_ops/3-CURRENT-STRATEGY.md#strategic-lines`.

## Example 1: Code bugfix (no strategic map)

**Input:**
> Пользователь жалуется, что при экспорте CSV пропадают строки. Почини.

**Output:**

```md
## Original task
Пользователь жалуется, что при экспорте CSV пропадают строки. Почини.

## Understood intent
Найти и устранить причину потери строк в CSV-экспорте. "Починено" означает: баг локализован в текущем коде, исправлен и подтверждён целевой проверкой без соседней регрессии.

## Assumptions (not verified with user)
- Речь про функцию `exportToCSV` в `src/exports/csv.ts`, потому что это единственный близкий матч по поиску.

## Acceptance criteria

### Must (blocks completion)
- [ ] Root cause локализован в текущем кодовом пути — **Evidence**: строка вида `src/exports/csv.ts:LINE - <причина>`.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.
- [ ] Баг зафиксирован целевой регрессией и больше не воспроизводится после исправления — **Evidence**: failing-then-passing test output или эквивалентный command output.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.
- [ ] Фикс остаётся узким и не даёт соседней регрессии — **Evidence**: focused diff плюс ближайший no-regression check.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.

### Must not (anti-patterns)
- [ ] Не скрывать симптом ранним `return`, swallowed error или косметическим переписыванием — **Why this would be bypassed**: баг станет тише, но причина потери строк останется.

### Verification protocol
1. Показать focused diff по целевому участку.
   Expected: меняется только зона, связанная с экспортом.
2. Запустить целевую регрессию и ближайший no-regression check.
   Expected: баг больше не воспроизводится и рядом не появилось новых failure.
```

## Example 2: Research (no strategic map)

**Input:**
> Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас.

**Output:**

```md
## Original task
Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас.

## Understood intent
Собрать только действительно новые техники 2026 года, сравнить их по общим осям и закончить не обзором, а решением: что внедрять, что отложить, что не подходит текущему стеку.

## Assumptions (not verified with user)
- "У нас" означает текущий набор agentic workflows и сопутствующих инструментов.

## Acceptance criteria

### Must (blocks completion)
- [ ] Названы минимум 5 техник именно 2026 года с первичными источниками — **Evidence**: датированный список source links.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.
- [ ] Все техники сравнены по одним и тем же осям — **Evidence**: одна сравнительная таблица `technique | reduction | complexity | infra dependency`.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.
- [ ] Итог заканчивается рабочим вердиктом для нашего стека — **Evidence**: раздел `внедрять / отложить / мимо` с краткой причиной для каждой техники.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.

### Must not (anti-patterns)
- [ ] Не добирать объём материалом старше 2026 года или вторичными пересказами без первичного источника — **Why this would be bypassed**: получится видимость полноты без ответа на вопрос о новом и применимом.

### Verification protocol
1. Проверить, что у каждой техники есть первичный источник 2026 года.
   Expected: нет undated или secondary-only entries.
2. Сверить выборочно один механизм и один итоговый verdict с полным чтением источника.
   Expected: формулировка точная и вывод действительно следует из материала.
```

## Example 3: Skill or agent creation (no strategic map)

**Input:**
> Сделай мне скилл для ревью пулл-реквестов.

**Output:**

```md
## Original task
Сделай мне скилл для ревью пулл-реквестов.

## Understood intent
Создать reusable skill, который анализирует pull request и возвращает структурированный review вместо общих советов.

## Assumptions (not verified with user)
- Источник PR может быть URL или локальный diff.

## Acceptance criteria

### Must (blocks completion)
- [ ] Создан валидный каталог скилла с `SKILL.md` и только реально нужными supporting files — **Evidence**: listing файлов плюс успешная валидация.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.
- [ ] `SKILL.md` явно задаёт trigger и workflow review — **Evidence**: frontmatter и раздел `Process` или эквивалентный рабочий ход.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.
- [ ] Скилл проверен на одном реалистичном PR-сценарии — **Evidence**: краткий smoke-test output.
  **Anchored in**: local-only — нет приложенного `_ops/` для этого примера.

### Must not (anti-patterns)
- [ ] Не сводить скилл к общим правилам ревью без рабочего хода — **Why this would be bypassed**: получится справка, а не инструмент.

### Verification protocol
1. Проверить структуру каталога и прогнать валидатор.
   Expected: skill is valid и без лишних файлов.
2. Прогнать один реалистичный PR-сценарий.
   Expected: вывод соответствует обещанной структуре review.
```

## Example 4: Strategy-trace (with strategic map)

**Input:**
> Сделай `strategy-trace`: я хочу добавить четвёртый owner-skill в chain, чтобы он проверял finished drafts.

**Output:**

```md
## Trace target
Я хочу добавить четвёртый owner-skill в chain, чтобы он проверял finished drafts.

## Strategic chain
1. Goal: репо должно оставаться компактной operating system для authoring-работы, а не расти быстрее собственного leverage.
   **Anchored in**: `_ops/1-NORTH-STAR.md` — `Цель`
2. Active line: owner-chain зафиксирован как `main-strategy -> system-architect -> criteria-generator`.
   **Anchored in**: `_ops/3-CURRENT-STRATEGY.md` — `Опорные стратегические линии`
3. Anti-goal: не расширять owner-chain без доказанного leverage.
   **Anchored in**: `_ops/3-CURRENT-STRATEGY.md` — `Anti-goals`
4. Observed target: запрос предлагает добавить четвёртого owner'а для review finished drafts.
   **Anchored in**: user request

## Verdict
drift

## Why
- Запрос расширяет зафиксированную тройку owner'ов вместо того, чтобы ужесточить одного из уже существующих.
- В запросе нет baseline или leverage-proof, который текущая стратегия требует перед ростом owner-chain.

## Do now
- Оставить owner-chain из трёх слоёв и встроить проверку в существующего owner'а, либо эскалировать в `main-strategy`, если тройка больше не держит ставку.
```

## Shape Guide

- `contract` mode target: 2-4 `Must`, 0-2 `Must not`, 1-3 verification steps.
- `strategy-trace` mode target: 3-4 chain steps, one verdict, up to 2 `Why` bullets, one `Do now`.
- If two bullets protect the same failure mode, merge them.
- Prefer short evidence-rich lines over explanatory mini-paragraphs.
