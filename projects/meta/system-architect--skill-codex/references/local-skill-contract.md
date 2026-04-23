# Local Skill Contract

Открывай этот файл только если вывод реально включает "нужен local skill" или "этот skill надо переписать".

## Сначала Опровергни Три Альтернативы

Новый local skill допустим только если failure не может чисто владеться через:

- `AGENTS.md` или другой durable instruction layer;
- runtime guardrail: hook, validator, approval, narrower tool policy;
- `task-planner`, если проблема по природе task-specific.

Если хотя бы один из этих слоёв может честно владеть проблемой, новый skill не default answer.

## Proof Gate

Перед рекомендацией skill докажи:

- это повторяемый workflow, а не разовая жалоба;
- у него есть distinct trigger;
- failure pattern повторяется;
- без skill модель реально плавает, shortcut'ит или теряет качество;
- skill не дублирует уже существующий owner-layer.

## Authoring Contract

- `Description`
  Одна короткая routing-формулировка в стиле `Use when ...` с boundaries и skip-cases.

- `Ядро`
  В `SKILL.md` оставлять только trigger, boundaries, default path, ключевые развилки и `done when`.

- `Progressive disclosure`
  Длинные варианты и примеры -> `references/`; хрупкие детерминированные операции -> `scripts/`.

- `Shape`
  Repo-local skill должен звучать как короткий operational contract, а не как essay.

- `Проверка`
  После правки нужны хотя бы быстрые routing и validation checks.

## Канон

Опирайся на:

- `knowledge/guides/perfect-skills.md`
- `knowledge/practical-guides/skill-authoring-checklist.md`
- `knowledge/practical-guides/codex-skills.md`
- `knowledge/guides/official-codex-skills-patterns.md`

Но в ответе пересказывай только сжатую выжимку, а не весь канон.
