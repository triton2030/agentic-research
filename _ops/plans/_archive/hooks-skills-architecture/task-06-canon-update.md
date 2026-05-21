# Обновление канона репо под новую архитектуру

## Цель

Привести `_ops/criteria/*.md`, `knowledge/practical-guides/*.md`,
`AGENTS.md`, `CLAUDE.md` в соответствие с реальностью после миграции.
Зафиксировать паттерн session-state как baseline для stateful
enforcement. Удалить drift между criteria и реализацией (например,
`init_project_shape.py` → `init-three-level.sh`).

## Применимые критерии и инструкции

- [_ops/criteria/repo-structure-and-runtime-guards.md](../../criteria/repo-structure-and-runtime-guards.md) — owner, обновляется.
- [_ops/criteria/skill-authoring.md](../../criteria/skill-authoring.md) — owner, обновляется.
- [_ops/criteria/instruction-layer.md](../../criteria/instruction-layer.md) — owner, обновляется.
- [_ops/criteria/criteria-routing-and-naming.md](../../criteria/criteria-routing-and-naming.md) — naming rules.
- `AGENTS.md`, `CLAUDE.md` (root) — synchronize.

## Контекст

Финальный шаг миграции. Должен закрыть `_ops/GOAL.md` Definition of done
через `1work-review` audit. Без этой задачи criteria и реализация
расходятся, и следующая сессия наследует drift.

## Подшаги

1. Обновить `repo-structure-and-runtime-guards.md`.
   EN: Update Rule on UserPromptSubmit to match new behavior (threshold-
   based, `turn_id == 1` only). Add new Rule documenting session-state as
   canonical cross-hook/skill shared structure with file path. Fix drift —
   replace any `init_project_shape.py` reference with `init-three-level.sh`.

2. Обновить `skill-authoring.md`.
   EN: Add Rule "detect-not-remind" — hooks detect structural facts (file
   change, criteria edit, anchor read); cognitive work (citation,
   classification, decision) lives in skill body. Add Rule for trigger
   surface auto-fire patterns from Task 05.

3. Обновить `instruction-layer.md`.
   EN: Update hooks section if present. Add reference to session-state
   schema as canonical shared state.

4. Обновить `knowledge/practical-guides/hooks-runtime-guardrails.md`.
   EN: Expand Decision Check with "knowledge (skill) vs invariant (hook)?"
   decision tree. Add session-state pattern as baseline architecture for
   stateful enforcement.

5. Обновить root `AGENTS.md` и `CLAUDE.md`.
   EN: Synchronize references to hooks-mechanism with new reality. Update
   task-level anchor rule if anchor docs section changed in Task 03.

6. Closeout audit через `1work-review`.
   EN: Run `1work-review` on entire migration (all six tasks). Compare
   against `_ops/GOAL.md` Definition of done. Generate evidence summary.

7. Archive observability shims.
   EN: Move `~/.claude/skills/1start-here/scripts/_observability/` to
   `_retired/` once data has been captured and per-hook decisions made.

## Готово

- [ ] Все 4 criteria-файла отражают новую архитектуру и не содержат drift.
- [ ] `hooks-runtime-guardrails.md` обновлён с session-state pattern.
- [ ] `AGENTS.md`, `CLAUDE.md` синхронизированы.
- [ ] `1work-review` closeout audit миграции пройден.
- [ ] Observability shims archived в `_retired/`.

## Красные линии

- [ ] Не додумывать criteria за пользователя — только observed reality из миграции.
- [ ] Не удалять старые Rule'ы без явной замены или routing к новому owner.
- [ ] Не создавать новых owner-surface'ов — всё в существующих файлах.
- [ ] Не закрывать миграцию пока есть open substeps в Task 02-05.

## Stop rule

Если `1work-review` audit находит regression vs baseline (Task 01
counters) — open new task для rollback вместо silent closeout.

## Проверка

1. `rg "init_project_shape" /Users/triton/Documents/GitHub/agentic-research/_ops/criteria/`
   Ожидаемо: 0 hits (drift fixed).
2. `rg "session-state" /Users/triton/Documents/GitHub/agentic-research/_ops/criteria/ /Users/triton/Documents/GitHub/agentic-research/knowledge/practical-guides/`
   Ожидаемо: hits в `repo-structure-and-runtime-guards.md` и `hooks-runtime-guardrails.md`.
3. `1work-review` verdict.
   Ожидаемо: пройдено, нет open substeps, evidence saved.

## Handoff

Миграция закрыта. Все task-files папки `hooks-skills-architecture/`
архивируются через `1planning` archive workflow в `_archive/`.
Финальный отчёт пишется через `1findings` если выявлены побочные находки.
