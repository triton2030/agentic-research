# PROJECT-PLAN

## Goal

Корневые инструкции, `knowledge/`, `projects/` и `_ops/` читаются fresh-session'ом без переобъяснения: любой агент или сессия за одно прочтение видит, где truth layer, где research, где живой artifact, и попадает в правильный слой по root docs + релевантному `knowledge/wisdom-*.md` без ручного роутинга.

## Approach & Why

Опираемся на уже сложившуюся форму репы: `knowledge/` как слой канона и research, `projects/` как слой артефактов, `_ops/` как минимальный стратегический owner-layer. Фокус не в расширении каталога, а в доведении текущей миграции и meta-стека до fail-closed формы, в которой fresh-session-агент не дрейфует. Когда этот слой стабилен, новые control surfaces могут авторизоваться отдельными PROJECT-PLAN'ами, не ломая общий shape.

## Anti-goals

- Не превращать `_ops/` в backlog, inbox или общий склад заметок.
- Не дублировать живые skill contracts в `AGENTS.md`, `CLAUDE.md` и побочных explainers.
- Не добавлять новые control surfaces ради полноты каталога в рамках этого плана — запуск новой линии требует собственного PROJECT-PLAN.

## Stages

### 1. Стабилизировать живую форму репы [~]

- [x] Зафиксировать repo-level Goal и owner-layer в `_ops/`.
- [~] Перевести стратегический слой на модель `_ops/PROJECT-PLAN.md` / `_ops/INTERVIEW.md` и не возвращать старый `ops/`.
- [ ] Сверить корневые инструкции, inventories и активные project folders с фактической живой поверхностью репы.
- [ ] Зафиксировать в `AGENTS.md` правила placement для research vs guides vs wisdom vs shipped skills, чтобы `knowledge/` не дрейфовал.
- [ ] Переписать `criteria-generator` (Codex + Claude Code) как primer + check, не hard gate; финальный блок — короткое резюме `_ops/` на русском; глобальный `~/.claude/CLAUDE.md` подтянуть.
- [ ] Закрыть явные stale surfaces и архивные хвосты так, чтобы новая сессия читала один и тот же truth layer.

### 2. Довести meta-стек до platform-parity [ ]

- [ ] Удержать `main-strategy`, `system-architect`, `criteria-generator`, `step-back` и соседние meta artifacts одинаковыми по сути между Codex и Claude Code.
- [ ] Оставлять только platform-necessary differences: packaging, tool invocation, pathing и metadata.
- [ ] Держать inventories и repo docs в синхроне с реальным набором живых control surfaces.

### 3. Fresh-session check [ ]

Финальный этап: симулировать чистую сессию (новый агент, без памяти предыдущих разговоров) и пройти по root docs → `knowledge/` → `projects/` → `_ops/`. Если за одно прочтение видно truth layer и roadmap роутинга новой работы без переспроса — Goal достигнут. Если нет — дельта в `learnings.md`, возврат к Stage 1 или 2.
