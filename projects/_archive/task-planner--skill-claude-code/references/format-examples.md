# Format Examples

Worked examples of `task-contract` output. Use them for shape, not content.

Three public shapes:

- `task` mode — task-file written to `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` (three sections: Цель / Подшаги / Критерии приёмки) + compact `Task-file receipt` in chat.
- `strategy-trace` mode — compact chain from `_ops/` to the checked target, verdict, one next move.
- `pulse-check` mode — dialog-time memory probe: cold `Recalled` block emitted before reading `_ops/`, then `Actual` quoted from `_ops/`, 3-step `Trace`, verdict, `Delta` only when not `remembered`.

In task mode the visible contract inside the file stays thin: usually 2-4 `Must`, 0-2 `Must not`, 1-3 verification steps.

Every `Must` carries `Anchored in:`. `local-only — <reason>` is allowed only for criteria **about the code itself** (diff shape, local invariant, naming) after Plan-Anchor Gate has already passed at the task level. Anchors **never** point to paths inside `_ops/plans/` — that layer is ephemeral.

## Example 1: Task mode — code bugfix (on-plan)

**Input:**
> Пользователь жалуется, что при экспорте CSV пропадают строки. Почини.

Step in PROJECT-PLAN: `[~] починить CSV-экспорт` под Stage `3. Стабилизировать экспорт данных`.

**File written: `_ops/plans/phase-03-stabilize-export/task-02-csv-export-loss.md`**

```markdown
# Починить CSV-экспорт

## Цель
Строки больше не теряются при экспорте и регрессия закрыта целевым тестом.

## Подшаги
- [ ] Локализовать root cause в `src/exports/csv.ts`
- [ ] Написать failing regression test
- [ ] Исправить баг, убедиться, что тест проходит
- [ ] Проверить ближайший no-regression check

## Критерии приёмки

### Must
- [ ] Root cause локализован в текущем кодовом пути — **Evidence**: строка вида `src/exports/csv.ts:LINE — <причина>`.
  **Anchored in**: `_ops/PROJECT-PLAN.md#stage-3-стабилизировать-экспорт-данных`
- [ ] Баг зафиксирован целевой регрессией и больше не воспроизводится после исправления — **Evidence**: failing-then-passing test output.
  **Anchored in**: `_ops/PROJECT-PLAN.md#goal`
- [ ] Фикс остаётся узким и не даёт соседней регрессии — **Evidence**: focused diff + ближайший no-regression check.
  **Anchored in**: `local-only — критерий о diff-форме, не о задаче`

### Must not
- [ ] Не скрывать симптом ранним `return`, swallowed error или косметическим rename — **Why this would be bypassed**: баг станет тише, но причина потери строк останется.

### Verification protocol
1. Показать focused diff по целевому участку.
   Expected: меняется только зона, связанная с экспортом.
2. Запустить целевую регрессию и ближайший no-regression check.
   Expected: баг больше не воспроизводится и рядом не появилось новых failure.
```

**Receipt in chat:**

```md
## Task-file receipt

- Path: `_ops/plans/phase-03-stabilize-export/task-02-csv-export-loss.md`
- Intent: починить потерю строк в CSV-экспорте с регрессией и без соседних падений.
- Anchors: `_ops/PROJECT-PLAN.md#goal`, `_ops/PROJECT-PLAN.md#stage-3-стабилизировать-экспорт-данных`
- Refs applied: `references/task-file-lifecycle.md`, `references/failure-modes.md#symptom-suppression`
- Draft: 3 Must · 1 Must-not · 2 Verify
- Gate: 7/7 passed · bypasses closed: symptom-suppression, overscope
- Ready: yes
```

Plus 1-3 строки простым русским: «Goal — стабильный экспорт; активный Stage — починка экспорта; anti-goal — косметика вместо root cause». Агент сразу продолжает работу под этим контрактом.

## Example 2: Task mode — research (on-plan)

**Input:**
> Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас.

**File written: `_ops/plans/phase-02-choose-compression/task-01-survey-2026.md`**

```markdown
# Обзор prompt compression 2026

## Цель
Выбрать 1-2 техники 2026 года, применимые к текущему agentic-стеку, с обоснованием.

## Подшаги
- [ ] Собрать минимум 5 техник 2026 с первичными источниками
- [ ] Построить сравнительную таблицу по reduction / complexity / infra dependency
- [ ] Вынести вердикт: внедрять / отложить / мимо — для каждой

## Критерии приёмки

### Must
- [ ] Минимум 5 техник именно 2026 года с первичными источниками — **Evidence**: датированный список source links.
  **Anchored in**: `_ops/PROJECT-PLAN.md#stage-2-выбрать-компрессию`
- [ ] Все техники сравнены по одним и тем же осям — **Evidence**: таблица `technique | reduction | complexity | infra dependency`.
  **Anchored in**: `_ops/INTERVIEW.md#research-deliverables`
- [ ] Итог заканчивается рабочим вердиктом для нашего стека — **Evidence**: раздел `внедрять / отложить / мимо` с причиной.
  **Anchored in**: `_ops/PROJECT-PLAN.md#goal`

### Must not
- [ ] Не добирать объём материалом старше 2026 или вторичными пересказами без первичного источника — **Why this would be bypassed**: получится видимость полноты без ответа.
```

**Receipt in chat:** (тот же шаблон, Path + Intent + Anchors + Refs + Draft + Gate + Ready.)

## Example 3: Strategy-trace (with strategic map)

**Input:**
> Сделай `strategy-trace`: я хочу добавить четвёртый owner-skill в chain, чтобы он проверял finished drafts.

**Output** (read-only, ничего в файл не пишется):

```md
## Trace target
Я хочу добавить четвёртый owner-skill в chain, чтобы он проверял finished drafts.

## Strategic chain
1. Goal: репо должно оставаться компактной operating system для authoring-работы.
   **Anchored in**: `_ops/PROJECT-PLAN.md` — `Goal`
2. Active stage: owner-chain зафиксирован как `project-strategy → instruction-layer → task-contract`.
   **Anchored in**: `_ops/PROJECT-PLAN.md` — `Stage <owner-chain>`
3. Anti-goal: не расширять owner-chain без доказанного leverage.
   **Anchored in**: `_ops/PROJECT-PLAN.md` — `Anti-goals`
4. Observed target: запрос предлагает добавить четвёртого owner'а.
   **Anchored in**: user request

## Verdict
drift

## Why
- Запрос расширяет зафиксированную тройку вместо того, чтобы ужесточить одного из существующих.
- Нет baseline или leverage-proof, которого требует текущая стратегия перед ростом owner-chain.

## Do now
- Оставить owner-chain из трёх слоёв и встроить проверку в существующего owner'а, либо эскалировать в `project-strategy`.
```

## Example 4: Pulse-check (with strategic map)

**Input:**
> Pulse check — мы уже третий час про agent-creator разговариваем, ты ещё помнишь ради чего?

**Output** (read-only):

```md
## Pulse check

### Recalled
- North Star: репо остаётся компактной operating system для authoring-работы.
- Active line: owner-chain зафиксирован тройкой `project-strategy → instruction-layer → task-contract`.
- This dialog: третий час проектируем agent-creator без привязки к тройке owner'ов.

### Actual
- Goal: "lean operating system for authoring, where a short _ops/ plan directs downstream framing" — _ops/PROJECT-PLAN.md#Goal
- Active stage: "owner-chain stays a tight triple; no fourth owner without proven leverage" — _ops/PROJECT-PLAN.md#Stage <owner-chain>

### Trace
compact _ops/ truth-layer → tight owner triple → dialog is designing a fourth owner outside that triple

### Verdict
drift

### Delta
Recall на North Star и активную линию правильный, но три часа ушли в проектирование agent-creator без baseline-проверки. Активная линия требует сначала доказать leverage одного из существующих owner'ов.
```

## Shape Guide

- `task` mode file: три секции — Цель (одна строка), Подшаги (2-5 action-lines), Критерии приёмки (2-4 `Must`, 0-2 `Must not`, 1-3 verification). Никаких лишних секций.
- `task` mode receipt: ≤ 10 строк, обязательны `Path:` и `Refs applied:`. После receipt — 1-3 строки простым языком, что держать в голове, и агент продолжает работу.
- `strategy-trace` mode: 3-4 chain steps, один verdict, ≤ 2 `Why` bullets, один `Do now`. Файл не пишется.
- `pulse-check` mode: 3-line `Recalled`, 2-line `Actual`, 1-line `Trace` с 3 arrow-separated steps, verdict из `remembered | drift | forgotten`, `Delta` только когда verdict не `remembered`. ≤ 15 строк total. Файл не пишется.
- Два буллета защищают один failure mode → объединить.
- Короткие evidence-rich строки > explanatory mini-paragraphs.
- `Anchored in:` **никогда** не ссылается на путь внутри `_ops/plans/` или на другой task-файл.
