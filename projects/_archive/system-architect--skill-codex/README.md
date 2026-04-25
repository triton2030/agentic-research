# System Architect — Codex

Codex-версия `system-architect`.

## Что Это

Opinionated системный архитектор durable control surfaces.

Он не стартует с редактуры `AGENTS.md`. Сначала понимает проект, его траекторию и какую работу здесь должен делать ИИ. Только потом выводит из этого instruction architecture.

Его причинная цепочка:

`project reality -> AI job map -> pressure and failure map -> control surfaces -> leverage -> instruction architecture -> minimize -> handoff`

## Чем Эта Версия Отличается От Старой

- `SKILL.md` стал короче и работает как router;
- центр тяжести перенесён в `workflow.md` и `output-shape.md`;
- порядок мышления стал project-first, а не instruction-first;
- pressure / failure / control surfaces теперь читаются как одна инженерная цепочка;
- `AGENTS.md` и соседние surfaces трактуются как выход системы, а не как стартовая точка.

## Что Важно

- сначала проект и карта работы ИИ, потом control surfaces;
- reuse before invention;
- runtime guardrail сильнее local skill, local skill сильнее instruction text;
- root instructions должны явно роутить частый `task-planner` для task discussion, edits, criteria checks и closeout;
- новый skill не default answer;
- ответ без `Minimize pass` считается неполным.

## Файлы

- `SKILL.md` — ядро скилла
- `references/workflow.md` — полная инженерная последовательность
- `references/output-shape.md` — форма финального audit result
- `references/audit-lenses.md` — глубокие линзы
- `references/anti-patterns.md` — типовые ошибки мышления
- `references/system-building-principles.md` — короткий системный канон
- `agents/openai.yaml` — metadata для Codex
