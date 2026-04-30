# Meta — Инвентарь Codex

Снимок на 28 апреля 2026.

Инвентарь перечисляет globally installed Codex handles и живые знания о них.
`projects/` больше не является repo-local source surface; если нужен код
скилла, проверяй installed handle в `/Users/triton/.codex/skills`.

## Core Meta Skills

### 1project-strategy

- Тип: skill
- Что делает: владеет `_ops/PROJECT-ROADMAP.md`; держит top-level Goal,
  Approach, Stage-chain и Anti-goals.

### 1strategy-discussion

- Тип: skill
- Что делает: раскрывает approach branches, hidden tradeoffs и consequential
  domain questions до планирования или исполнения.

### user-truth

- Тип: skill
- Что делает: маршрутизирует durable user signals: стиль/defaults/criteria в
  `1instruction-layer`, стратегию в `1project-strategy`, task detail в
  `1task-contract`.

### 1task-contract

- Тип: skill
- Что делает: создаёт empty phase task skeletons и детализирует только текущий
  task-файл.

### 1before-work

- Тип: skill
- Что делает: перед работой выбирает релевантные `_ops/criteria/*.md`,
  коротко цитирует 1-3 Rule/Why и сверяет work scope со стратегией.

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
- Что делает: проектирует skill trigger surfaces, descriptions, references,
  validation и `agents/openai.yaml`.

### 1instruction-layer

- Тип: skill
- Что делает: решает placement правил в AGENTS/CLAUDE/subtree instructions и
  владеет `_ops/criteria/*.md`.

### 1repo-shape

- Тип: skill
- Что делает: проектирует folders, plugins, MCP/apps, subagents, validators,
  scripts, config и tool boundaries.

### 1step-back

- Тип: skill
- Что делает: короткий zoom-out / reframe при reasoning drift.

### 1criteria-council

- Тип: skill
- Что делает: запускает 2-3 read-only Codex subagents как council критериев,
  когда пользователь явно хочет разные роли для многокритериального решения.

### repo-power-tools

- Тип: skill
- Что делает: fast CLI evidence для code/docs/package/security work.
