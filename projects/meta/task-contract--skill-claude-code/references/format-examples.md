# Format Examples

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


## Shape Guide

Task mode only: write Цель / Подшаги / Критерии приёмки, then emit a compact receipt.
