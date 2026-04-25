# Meta — Инвентарь Codex

Снимок на 25 апреля 2026.

Инвентарь смешанный: здесь перечислены repo-local project artifacts и globally installed handles, которые реально доступны в рабочей среде. Если локальная проектная папка ушла в `projects/_archive/`, сначала проверяй installed handle; archive сам по себе не делает capability живой.

## Split Meta Skills

### before-work
- Тип: skill
- Что делает: освежает Stage / цель / Must-not / next step перед нетривиальной работой.

### before-write
- Тип: skill
- Что делает: проверяет write scope прямо перед `apply_patch`, bulk rewrite или generated file creation.

### work-review
- Тип: skill
- Что делает: сверяет результат с goal / criteria / evidence перед финальным closeout.

### preference-sync
- Тип: skill
- Что делает: владеет durable preference capture в `_ops/INTERVIEW.md`.

### contradiction-hold
- Тип: skill
- Что делает: держит конфликт между новым запросом и stored plan/preference truth до ясной мотивации.

### plan-drift-watch
- Тип: skill
- Что делает: ловит chat/git/task/artifact evidence, показывающий drift между планом и реальностью.

### task-contract
- Тип: skill
- Что делает: владеет task-файлом `_ops/plans/phase-NN-*/task-MM-*.md` — Цель / Подшаги / Критерии приёмки.

### strategy-trace
- Тип: skill
- Что делает: read-only alignment trace артефакта или запроса против Goal / Stage / intent.

### pulse-check
- Тип: skill
- Что делает: read-only probe того, держит ли сессия цель и активную линию в памяти.

### project-strategy
- Тип: skill
- Что делает: владеет `_ops/PROJECT-PLAN.md` и `_ops/learnings.md`.

### ops-sync
- Тип: skill
- Что делает: синхронизирует `_ops/plans/` phase folders с Stages из PROJECT-PLAN.

### skill-architect
- Тип: skill
- Что делает: проектирует Codex skill trigger surfaces, descriptions, references, validation и `agents/openai.yaml`.

### instruction-layer
- Тип: skill
- Что делает: решает placement правил в AGENTS/CLAUDE/subtree instructions и routing.

### repo-shape
- Тип: skill
- Что делает: проектирует folders, plugins, MCP/apps, subagents, validators, scripts, config и tool boundaries.

## Utility Skills / Capabilities

### step-back
- Тип: skill
- Что делает: короткий zoom-out / reframe при reasoning drift.

### screenshot-design
- Тип: skill
- Что делает: visual critique UI screenshots.

### pitch-coherence-audit
- Тип: skill
- Что делает: narrative coherence audit для investor pitch materials.

### playwright
- Тип: skill
- Что делает: re-runnable browser automation flows.

### subagents (native)
- Тип: agent
- Источник: OpenAI
- Что делает: отдельные контексты для критики, проверки или делегирования при явном запросе пользователя.

### guide-subagents
- Тип: skill
- Что делает: готовит запуск native Codex subagents через чат и держит owner boundaries.

### skills
- Тип: system feature
- Источник: OpenAI
- Что делает: повторяемый workflow-слой поверх обычного поведения Codex.

### plugins
- Тип: plugin
- Источник: OpenAI
- Что делает: упаковывают skills, app integrations и MCP в расширяемый слой Codex.

## Чего Не Хватает

- Sync script source↔installed для Codex skills.
- Trigger smoke на свежих Codex sessions после split rollout.
- Promotion rule: когда знание остаётся в research, а когда переходит в устойчивые rules.
