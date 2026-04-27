# Meta — Инвентарь Codex

Снимок на 27 апреля 2026.

Инвентарь перечисляет repo-local project artifacts и globally installed handles,
которые реально доступны в рабочей среде. Если локальная проектная папка ушла
в `projects/_archive/`, сначала проверяй installed handle.

## Core Meta Skills

### project-strategy

- Тип: skill
- Что делает: владеет `_ops/PROJECT-ROADMAP.md` и `_ops/learnings.md`;
  держит top-level Goal, Approach, Stage-chain и Anti-goals.

### 1strategy-discussion

- Тип: skill
- Что делает: раскрывает approach branches, hidden tradeoffs и consequential
  domain questions до планирования или исполнения.

### user-truth

- Тип: skill
- Что делает: владеет `_ops/INTERVIEW.md`; хранит предпочтения, видение,
  ограничения и ответы пользователя.

### 1task-contract

- Тип: skill
- Что делает: создаёт empty phase task skeletons и детализирует только текущий
  task-файл.

### 1before-work

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
- Что делает: проектирует skill trigger surfaces, descriptions, references,
  validation и `agents/openai.yaml`.

### 1instruction-layer

- Тип: skill
- Что делает: решает placement правил в AGENTS/CLAUDE/subtree instructions.

### 1repo-shape

- Тип: skill
- Что делает: проектирует folders, plugins, MCP/apps, subagents, validators,
  scripts, config и tool boundaries.

### 1step-back

- Тип: skill
- Что делает: короткий zoom-out / reframe при reasoning drift.

### 1guide-subagents

- Тип: skill
- Что делает: ограничивает и оформляет Codex subagent delegation, когда
  пользователь явно просит parallel workers или delegation.

### repo-power-tools

- Тип: skill
- Что делает: fast CLI evidence для code/docs/package/security work.

### guide-subagents

- Тип: skill
- Что делает: guide для real parallel split и проверки evidence.
