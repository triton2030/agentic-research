# Local Skill Contract

Открывай этот файл только если вывод реально включает "нужен local skill" или "этот skill надо переписать".

## Короткий Authoring Contract

- `Proof gate`
  Есть повторяемый workflow, distinct trigger, реальный failure pattern и явная причина, почему это не чинится системным промптом, `AGENTS.md`, acceptance criteria или runtime guardrail.
- `Нужен ли skill вообще`
  Почему это именно skill, а не системный промпт, `AGENTS.md`, `reference` или `script`.
- `Trigger и границы`
  Для какого повторяемого workflow он нужен и когда его не надо вызывать.
- `Description`
  Одна короткая routing-формулировка в стиле `Use when ...`, потому что при progressive disclosure модель сначала видит metadata.
- `Что должно остаться в ядре`
  Только trigger, boundaries, default path, ключевые развилки, `done when`.
- `Как работает progressive disclosure`
  Если у skill есть дополнительные файлы, он сам должен быть устроен как metadata -> `SKILL.md` -> `references/` и `scripts/` по мере надобности.
- `Что вынести`
  Длинные варианты и примеры -> `references/`; хрупкие детерминированные операции -> `scripts/`.
- `Насколько коротко`
  Repo-local skill должен быть скорее коротким operational contract, чем essay.
- `Чем проверить`
  Быстрая проверка routing и валидации после правки.

## Канон, На Который Можно Опереться

Если речь о Claude Code-скилле:

- `knowledge/guides/perfect-skills.md`
- `knowledge/practical-guides/skill-authoring-checklist.md`
- `knowledge/practical-guides/claude-code-skills.md`
- `knowledge/guides/official-claude-skills-patterns.md`

Если речь о Codex-скилле:

- `knowledge/guides/perfect-skills.md`
- `knowledge/practical-guides/skill-authoring-checklist.md`
- `knowledge/practical-guides/codex-skills.md`
- `knowledge/guides/official-codex-skills-patterns.md`

Но в ответе пересказывай только сжатую выжимку, а не полный канон.
