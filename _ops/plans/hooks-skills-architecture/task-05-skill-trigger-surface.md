# Усиление триггеров skills для авто-запуска

## Цель

`1work-review` и `1user-truth` должны срабатывать на структурные факты
(file change, criteria edit) без hook-страховки. Расширить descriptions в
frontmatter, валидировать через `1skill-architect` audit и bare-prompt
subagent тесты.

## Применимые критерии и инструкции

- [_ops/criteria/skill-authoring.md](../../criteria/skill-authoring.md) — trigger surface, Anthropic discipline, `description < 1024 chars`.
- [_ops/criteria/repo-structure-and-runtime-guards.md](../../criteria/repo-structure-and-runtime-guards.md) — owner-surface boundaries.

## Контекст

После Task 03+04 hooks стали тоньше; skill triggers нужно усилить чтобы
они срабатывали сами, а не только через hook directive.

## Подшаги

1. Audit current descriptions.
   EN: Review current frontmatter description of `1work-review` and
   `1user-truth`. Identify which triggers are manual-only ("review",
   "готово") versus auto-fire ("file change", "criteria edited").

2. Усилить `1work-review` trigger surface.
   EN: Add to frontmatter description trigger phrases — «после Edit/Write
   turn», «file changes detected», «substantive правка завершена»,
   «auto-fire after substantive write». Keep total under 1024 chars.

3. Усилить `1user-truth` trigger surface.
   EN: Add — «правка `_ops/criteria/*.md`», «criteria edited», «criteria
   touched», «criteria file modified». Keep total under 1024 chars.

4. Sanity-check через `1skill-architect`.
   EN: Invoke `1skill-architect` to audit new descriptions. Validate
   front-loading, third-person POV, no overlap between skills, no
   over-trigger on conversational mentions.

5. Validate через bare-prompt subagent.
   EN: Subagent prompt "я сделал правку файла, что дальше?" → should find
   `1work-review`. Subagent prompt "я поправил criteria" → should find
   `1user-truth`. Neither should trigger on conversational paraphrase.

## Готово

- [ ] `1work-review` description содержит auto-fire triggers, <1024 chars.
- [ ] `1user-truth` description содержит criteria-edit triggers, <1024 chars.
- [ ] `1skill-architect` audit passes.
- [ ] Bare-prompt subagent тесты проходят.

## Красные линии

- [ ] Не делать description >1024 chars (Anthropic loader silent cut).
- [ ] Не дублировать trigger phrases между skills (overlap → undertrigger).
- [ ] Не убирать существующие manual triggers («review», «готово»).

## Проверка

1. `wc -m <(python3 -c "import re,sys; m=re.search(r'description: >\s*\n((?:  .*\n)+)', open(sys.argv[1]).read()); print(m.group(1) if m else '')" ~/.claude/skills/1work-review/SKILL.md)`
   Ожидаемо: < 1024.
2. То же для `1user-truth/SKILL.md`.
   Ожидаемо: < 1024.
3. Bare-prompt subagent runs — правильные skill triggers.

## Handoff

После закрытия → Task 06 закрывает миграцию обновлением canon в репо
под новую архитектуру.
