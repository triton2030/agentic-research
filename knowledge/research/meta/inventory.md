# Meta — Инвентарь

Снимок после cleanup 18 мая 2026.

Инвентарь перечисляет meta/control handles и gaps. Если нужен код live skill,
проверять установленный handle: Claude Code через marketplace/cache, Codex через
`/Users/triton/.codex/skills`.

## Shared

### Evidence-closeout

- Тип: рабочий момент, не отдельный live skill
- Где есть: Claude Code, Codex через текущего execution owner-а
- Что делает: сверяет результат с просьбой, owner-документами, evidence и
  остаточным риском перед claim "готово".

### 1skill-architect

- Тип: skill
- Где есть: Claude Code, Codex
- Что делает: проектирует skill trigger surfaces, descriptions, references и
  validation.

### instruction-layer / 1instruction-layer

- Тип: skill
- Где есть: Claude Code, Codex
- Что делает: отвечает за language-quality и placement текста инструкций:
  wording, links-over-inline, lost-in-middle, literal scope и duplicated prose.

### 1folder-contract

- Тип: skill
- Где есть: Codex; Claude-side mirror ведётся отдельно.
- Что делает: держит Owner Decision Map, `_ops/project-graph.md`, folder graph,
  criteria delivery chain, system coherence, structural guardrails и Goal-quote
  sync.

### 1step-back

- Тип: skill
- Где есть: Claude Code, Codex
- Что делает: короткий zoom-out / reframe при reasoning drift.

### 1cli-tools

- Тип: skill
- Где есть: Claude Code, Codex
- Что делает: fast CLI evidence для code/docs/package/security work. Старое
  имя `repo-power-tools` встречается только как historical/probe-banner alias,
  не live route.

### Retired Pre-Work Gate

- Тип: retired skill
- Где есть: historical
- Что делает теперь: standalone layer удалён; discipline распределена между
  strategy/planning, owner/criteria checks и review.

## Claude Code

### project-roadmap

- Тип: skill
- Что делает: legacy roadmap owner; сверять с live planning/strategy split.

### domain-clarifier

- Тип: skill
- Что делает: задаёт consequential domain questions, когда scope или criteria
  зависят от доменных знаний.

### user-interview

- Тип: skill
- Что делает: legacy/reference handle для user-signal capture; durable signals
  сейчас идут в owner-инструкции, `_ops/rules/`, planning surfaces или memory
  layer по явной просьбе пользователя.

### ops-sync

- Тип: skill
- Что делает: legacy helper для `_ops/plans/`; использовать только для
  реальной ephemeral execution surface.

### task-contract

- Тип: skill
- Что делает: создаёт empty phase task skeletons и детализирует текущий task-файл.

## Codex

### 1roadmap

- Тип: legacy/renamed skill reference
- Что делает: старый Codex owner для roadmap-level framing; текущая модель
  разделяет `1strategy`, `1strategy-docs` и `1planning`.

### 1strategy

- Тип: skill
- Что делает: раскрывает approach branches, hidden tradeoffs и questions до
  planning/execution.

### owner-truth routing

- Тип: рабочий маршрут, не отдельный live skill
- Что делает: durable user signals закрепляются только у правильного owner-а:
  instruction layer, GOAL/roadmap/task, findings или memory layer по явной
  просьбе пользователя.

### 1tasks

- Тип: legacy/renamed skill reference
- Что делает: task skeletons и текущий task detail; сверять с live `1planning`.

### 1md-graph

- Тип: skill
- Что делает: проверяет Markdown graph hygiene, frontmatter links, wikilinks и
  dependency radius.

### 1fresh-eyes

- Тип: skill
- Что делает: запускает или готовит fresh-context проверку через Codex subagents.

## Missing

- Явное соответствие legacy Claude handles текущему compact owner model.
- Единый freshness check для installed handles перед обновлением inventories.
