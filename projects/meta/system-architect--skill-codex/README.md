# System Architect — Codex

Codex-версия `system-architect`.

## Что Это

Opinionated системный архитектор instruction layer. Его spine:

`telos -> as-is map -> forces -> failure classes -> leverage analysis -> prescriptions -> minimize -> handoff`

Он не начинает с чеклиста симптомов и не заканчивает `Force Fields` как красивым приложением. Сначала смотрит, что система должна обслуживать, что реально уже стоит на машине, какие силы давят на дизайн, и только потом выбирает leverage.

## Чем Эта Версия Отличается От Старой

- capability inventory поднят в first-order шаг;
- forces стали design input, не epilogue;
- leverage выделен как отдельный обязательный этап;
- minimize pass стал обязательным, а не ценностью "где-то в тексте";
- `1 failure -> 1 fix` перестал быть default формой мышления.

## Что Важно

- reuse before invention;
- runtime guardrail сильнее local skill, local skill сильнее instruction text;
- новый skill не default answer;
- ответ без `Minimize pass` считается неполным.

## Файлы

- `SKILL.md` — ядро скилла
- `references/workflow.md` — rigid spine
- `references/output-shape.md` — финальная форма audit result
- `references/audit-lenses.md` — глубокие линзы
- `references/anti-patterns.md` — типовые ошибки мышления
- `references/system-building-principles.md` — короткий системный канон
- `agents/openai.yaml` — metadata для Codex
