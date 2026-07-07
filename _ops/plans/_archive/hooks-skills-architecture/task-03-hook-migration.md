# Миграция трёх существующих hooks

## Цель

Привести SessionStart, UserPromptSubmit и Stop hooks в соответствие с правильной архитектурой:

* SessionStart инжектит ≤500 строк вместо 1500.
* UserPromptSubmit threshold-based, активен только на `turn_id == 1`.
* Stop Stage 1 — composability check (вызывался ли `1work-review`), не marker-grep; warn-not-block на первом игнорировании.
* Stop Stage 2 — короткое сообщение блока, главная защита переезжает в `1user-truth` Confabulation Stop.
* Stop Stage 3 — удалить из hook, перенести требование цитаты в `1work-review` skill body.

## Применимые критерии и инструкции

* [\_ops/criteria/repo-structure-and-runtime-guards.md](/broken/pages/QwzQ0cLtKIkYIVyLwG1X) — UserPromptSubmit lightweight reminder.
* [\_ops/criteria/skill-authoring.md](/broken/pages/kqzBNg5rfgUwBptEqmGD) — UserPromptSubmit не write-gate, `1work-review` проверяет факт применения.
* [\_ops/criteria/instruction-layer.md](/broken/pages/gm24WNIfQ3REVOMpf3f9) — placement.
* `AGENTS.md`, `CLAUDE.md` (root).

## Контекст

Требуется `session-state` CLI из Task 02. Counter-таблица из Task 01 указывает per-hook decisions.

## Подшаги

1. Inject markers в `1start-here/SKILL.md`. EN: Add `<!-- session-start-inject:begin -->` and `<!-- session-start-inject:end -->` markers around orientation map + first-response contract + anti-patterns sections. Target ≤500 lines between markers.
2. Update `session-start.sh`. EN: Modify script to extract only content between inject markers. Full SKILL.md remains readable via Read tool. Add `session-state.py gc` call.
3. Update `prompt-submit-reminder.py`. EN: Read session-state turn\_id. If turn\_id > 1, exit silently. Remove "перед каждым write прочитай applicable файл из `_ops/criteria/`" from output — write-gate moves to Task 04 PreToolUse. Keep intent-grounding only for turn\_id == 1.
4. Rewrite Stop Stage 1 (work-review marker). EN: Replace marker-grep with check — did `session-state.skill_invocations[turn_id]` include "1work-review"? Yes → allow. No → inject directive "Был substantive write — прогони `1work-review`" and increment `skipped_review_count` in session-state. Block only when counter ≥ 2.
5. Simplify Stop Stage 2 (user-truth marker). EN: Keep block as safety net but shorten message significantly. Reference `1user-truth` Confabulation Stop as primary defense.
6. Remove Stop Stage 3 (verbatim citation). EN: Delete `has_verbatim_quote_from`, `find_anchor_doc_reads`, and the Stage 3 branch from `stop-work-review.py`. Move citation requirement to `1work-review/SKILL.md` Output template instead.

## Готово

* [ ] `session-start.sh` инжектит ≤500 строк.
* [ ] `prompt-submit-reminder.py` silent при `turn_id > 1`.
* [ ] `stop-work-review.py` Stage 1 — composability check.
* [ ] `stop-work-review.py` Stage 2 — короткое сообщение.
* [ ] `stop-work-review.py` без Stage 3.
* [ ] `1work-review/SKILL.md` содержит citation requirement в Output.

## Красные линии

* [ ] Не удалять existing hooks полностью до подтверждения через subagent test.
* [ ] Не менять wire в `settings.json` в этой задаче — только behavior скриптов.
* [ ] Не ломать fail-safe — любая ошибка hook → silent exit 0.

## Stop rule

Если bare-prompt subagent baseline regress в `legit-catch` ratio — rollback per stage. Если Stage 1 composability check срабатывает false-positive

> 20% (skill вызвался, но не задетектился) — переоценить detection logic.

## Проверка

1. Bare-prompt subagent: "сделай мелкое изменение в README". Ожидаемо: на Stop hook нет ритуального verbatim-блокинга.
2. Bare-prompt subagent: "поправь criteria файл". Ожидаемо: `1user-truth` skill auto-вызывается, Stage 2 не блокирует если skill отработал.
3. Bare-prompt subagent с многоходовым диалогом. Ожидаемо: "одной фразой что услышал" появляется только в 1-м ходу.

## Handoff

После закрытия → Task 04 wires PreToolUse в `settings.json` для real write-gate.
