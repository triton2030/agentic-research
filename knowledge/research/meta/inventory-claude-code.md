# Meta — Инвентарь Claude Code

Снимок на 25 апреля 2026.

Инвентарь перечисляет globally installed Claude Code handles и живые знания о
них. `projects/` больше не является repo-local source surface; если нужен код
скилла, проверяй installed handle в Claude marketplace/cache.

## Core Meta Skills

### project-roadmap

- Тип: skill
- Что делает: владеет `_ops/PROJECT-ROADMAP.md`; строит domain-grounded
  Stage-chain.

### domain-clarifier

- Тип: skill
- Что делает: задаёт consequential domain questions, когда prerequisites,
  Stage order, task scope или criteria зависят от доменных знаний.

### user-interview

- Тип: skill
- Что делает: legacy/reference handle для user-signal capture; в текущей repo
  model durable signals маршрутизируются в root instructions, `_ops/criteria/`
  или `_ops/PROJECT-ROADMAP.md` через соответствующего owner.

### ops-sync

- Тип: skill
- Что делает: legacy installed helper для `_ops/plans/` phase folders; в
  compact repo использовать только когда активная задача реально требует
  эфемерную execution surface.

### task-contract

- Тип: skill
- Что делает: создаёт empty phase task skeletons и детализирует только текущий
  task-файл.

### before-work

- Тип: skill
- Что делает: перед работой сверяет strategy/task и релевантные criteria by
  task meaning.

### before-write

- Тип: skill
- Что делает: перед write проверяет scope, current substep и execution lesson.

### 1work-review

- Тип: skill
- Что делает: сверяет результат с task criteria/evidence и продолжает repair
  loop до качественного завершения.

## Control / Utility Skills

### 1skill-architect

- Тип: skill
- Что делает: проектирует Claude/Codex skill trigger surfaces и references.

### instruction-layer

- Тип: skill
- Что делает: решает placement правил в AGENTS/CLAUDE/subtree instructions и
  criteria layer.

### repo-shape

- Тип: skill
- Что делает: проектирует folders, hooks, permissions, MCP/apps, validators,
  scripts, config и tool boundaries.

### step-back

- Тип: skill
- Что делает: короткий zoom-out / reframe при reasoning drift.

### repo-power-tools

- Тип: skill
- Что делает: fast CLI evidence для code/docs/package/security work.
