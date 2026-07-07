# Task 01 — Консолидировать criteria-pipeline

Статус: закрыто.

Применимые критерии:

* [`instruction-layer`](https://github.com/triton2030/agentic-research/blob/main/_ops/plans/criteria/instruction-layer.md) — routing, placement, criteria links.
* [`skill-authoring`](https://github.com/triton2030/agentic-research/blob/main/_ops/plans/criteria/skill-authoring.md) — `SKILL.md`, triggers, model-delta cleanup.
* [`repo-structure-and-runtime-guards`](https://github.com/triton2030/agentic-research/blob/main/_ops/plans/criteria/repo-structure-and-runtime-guards.md) — base shape, runtime boundaries, `1start-here` / `1instruction-layer`.
* [`work-review-and-evidence`](https://github.com/triton2030/agentic-research/blob/main/_ops/plans/criteria/work-review-and-evidence.md) — observable closeout evidence.

## Цель

Сделать `_ops/criteria/*.md` рабочим слоем приёмки: meta-скилы читают criteria до действий, durable signals пишутся через `1user-truth`, а `1instruction-layer` становится общим входом для вопроса “куда живёт правило”.

## Подшаги

* [x] Закрепить `1user-truth` как owner criteria-протокола. EN: Make `1user-truth` the canonical owner of the criteria acquire-write-read-apply cycle and durable-signal handoffs.
* [x] Подключить criteria-handoff к strategy, Write Gate, review и task scope. EN: Point `1strategy`, `1before-work` Write Gate, `1work-review`, and the planning/task-scope owner to the criteria cycle without duplicating its body.
* [x] Сделать `1instruction-layer` entry-point для rule placement. EN: Route instruction/runtime/skill-placement signals through `1instruction-layer`, with `1start-here` and `1skill-architect` as narrowed delegates.
* [x] Синхронизировать root-инструкции, rename и SessionStart onboarding. EN: Update `AGENTS.md`, `CLAUDE.md`, skill handles, Claude global settings, and the fail-safe `1start-here` SessionStart hook.
* [x] Почистить criteria-файлы от старой owner-модели. EN: Align `instruction-layer`, `repo-structure-and-runtime-guards` criteria type, and `skill-authoring` criteria with the current criteria ownership model.

## Критерии приёмки

* [x] Полный criteria-cycle описан только в `1user-truth`; соседние скилы дают короткие handoff-ссылки.
* [x] `1strategy` имеет один routing-хвост в `1instruction-layer`, без прямого ухода в delegate-скилы.
* [x] Planning/task-scope owner читает relevant criteria до freeze scope.
* [x] `1instruction-layer` покрывает три типа placement: instruction text, runtime guardrail, skill matcher.
* [x] `1start-here` и `1skill-architect` сужены до прямых вызовов и не спорят с common entry.
* [x] Root-инструкции отражают routing, но не копируют тела live skills.
* [x] Не создан новый control surface, не восстановлены `INTERVIEW.md` / `LEARNINGS.md`, не заведён отдельный criteria-файл про criteria-cycle.

## Evidence

* Skill changes: `1user-truth`, `1strategy`, `1before-work`, `1work-review`, planning/task-scope owner, `1instruction-layer`, `1start-here`, `1skill-architect`.
* Instruction/runtime changes: `AGENTS.md`, project `CLAUDE.md`, global `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/skills/1start-here/scripts/session-start.sh`.
* Rename cleanup: 4 skill directories moved; word-boundary replacement applied across relevant `*.md`, excluding Codex copies.
* Verification recorded: all 14 `SKILL.md` descriptions < 1536 chars (max 1497); stale skill-name/path scans empty outside excluded Codex paths; 10 reference files present; `1user-truth` remains the only canonical criteria-cycle owner; `Rule:` / `Why:` counts match across `_ops/criteria/*.md`; Claude settings JSON validated.
