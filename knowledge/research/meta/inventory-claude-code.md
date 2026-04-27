# Meta — Инвентарь Claude Code

Снимок на 25 апреля 2026.

Инвентарь перечисляет repo-local project artifacts и globally installed handles,
которые реально доступны в рабочей среде. Если локальная проектная папка ушла
в `projects/_archive/`, сначала проверяй installed handle.

## Core Meta Skills

### project-roadmap

- Тип: skill
- Что делает: владеет `_ops/PROJECT-ROADMAP.md` и `_ops/learnings.md`;
  строит domain-grounded Stage-chain.

### domain-clarifier

- Тип: skill
- Что делает: задаёт consequential domain questions, когда prerequisites,
  Stage order, task scope или criteria зависят от доменных знаний.

### user-interview

- Тип: skill
- Что делает: владеет `_ops/INTERVIEW.md`; хранит предпочтения, видение,
  ограничения и ответы пользователя.

### ops-sync

- Тип: skill
- Что делает: синхронизирует `_ops/plans/` phase folders со Stages из
  `PROJECT-ROADMAP.md`.

### task-contract

- Тип: skill
- Что делает: создаёт empty phase task skeletons и детализирует только текущий
  task-файл.

### before-work

- Тип: skill
- Что делает: перед работой извлекает execution lesson из strategy, task и
  user truth.

### before-write

- Тип: skill
- Что делает: перед write проверяет scope, current substep и execution lesson.

### work-review

- Тип: skill
- Что делает: сверяет результат с task criteria/evidence и продолжает repair
  loop до качественного завершения.

## Control / Utility Skills

### skill-architect

- Тип: skill
- Что делает: проектирует Claude/Codex skill trigger surfaces и references.

### instruction-layer

- Тип: skill
- Что делает: решает placement правил в AGENTS/CLAUDE/subtree instructions.

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
