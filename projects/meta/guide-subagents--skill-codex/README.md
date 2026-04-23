# Guide Subagents — Codex

Рабочая папка по Codex-скиллу `guide-subagents`.

## Что Это Закрывает

`guide-subagents` — не общий meta-layer и не owner в цепочке. Это тонкий execution helper для узкого момента, когда пользователь явно хочет native Codex subagents и качество зависит от хорошего split-а, аккуратного launch-а и жёсткой post-launch integration hygiene.

Скилл держит четыре вещи:

- решить, стоит ли вообще делегировать;
- оставить у main agent blocking step, integration surfaces и dirty/hotspot файлы;
- дать worker-ам короткие owned-scope briefs с жёсткой reporting discipline;
- после возврата проверить on-disk diff и отделить scoped truth от repo-level или preexisting failures.

Форма результата при этом не фиксирована как "короткий ответ". Для code-workers это часто короткий scoped delta. Для business / strategy / marketing / analysis workers нормальным owned deliverable может быть развёрнутый вывод в чат, если он не выходит за границы scope.

## Важные Границы

- Upstream owners остаются upstream: `main-strategy`, `system-architect`, `task-planner`.
- `guide-subagents` не компенсирует отсутствующий план, не придумывает критерии и не превращается в mini-orchestrator.
- Native Codex launch mechanics и post-launch verification считаются частью самого workflow, а не “деталями исполнения”.

## Файлы

- `SKILL.md` — тонкое ядро workflow.
- `references/launch-brief-template.md` — шаблон brief-а и reporting contract.
- `references/red-flags.md` — coordination и verification anti-patterns.
- `references/output-shape.md` — компактный chat shape.
