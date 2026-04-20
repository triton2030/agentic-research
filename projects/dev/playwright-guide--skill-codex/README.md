# Playwright Guide — Codex

Рабочая папка по Codex-скиллу `playwright-guide`.

## Что Это Закрывает

Когда задача касается браузера, живой страницы или проверки визуальной логики интерфейса, агенту легко сделать лишнее:

- пойти в самодельный browser-flow вместо официального installed skill;
- раскрыть слишком много контекста до выбора правильного пути;
- смешать сбор evidence, визуальный разбор и написание скрипта в один шумный проход.

`playwright-guide` нужен как тонкий routing-layer.

Он не заменяет официальные browser-skills. Он помогает:

- выбрать между `$playwright` и `$playwright-interactive`;
- понять, когда live browser вообще не нужен и достаточно `$screenshot-design`;
- раскрыть только тот контекст, который меняет способ проверки;
- собрать evidence для layout/design checks до выводов;
- перевести проверку в понятный сценарий: разовый проход, интерактивное исследование, section audit или authoring Playwright script.

## Чем Он Не Является

Это не ещё один browser automation skill.

Он не должен подменять собой:

- `$playwright` — когда нужен обычный официальный Playwright path;
- `$playwright-interactive` — когда нужна живая длительная сессия;
- `$screenshot-design` — когда главное evidence уже в статичном скриншоте;

Коротко: `playwright-guide` выбирает путь и рамку. Исполнение делает официальный или более узкий skill.

## На Что Опирается

- official installed skills: `$playwright`, `$playwright-interactive`
- adjacent local skills: `$screenshot-design`
- [knowledge/wisdom-agents.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-agents.md)
- [knowledge/wisdom-skills-plugins.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-skills-plugins.md)
- [knowledge/wisdom-codex.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-codex.md)
- [knowledge/practical-guides/codex-skills.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/practical-guides/codex-skills.md)
- [knowledge/research/dev/learnings.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/research/dev/learnings.md)

## Файлы

- `SKILL.md` — тонкое ядро: trigger, routing, workflow, done when
- `references/routing-matrix.md` — какой skill брать для какого случая
- `references/context-packs.md` — какой контекст раскрывать по типу задачи
- `references/live-flow.md` — как вести разовый browser-pass через `$playwright`
- `references/interactive-flow.md` — как вести persistent-pass через `$playwright-interactive`
- `references/design-audit-handoff.md` — как передавать evidence в визуальный review
- `references/layout-signals.md` — сигналы для spacing, block order и visual weight
- `references/red-flags.md` — паттерны дрейфа и слабые ходы
