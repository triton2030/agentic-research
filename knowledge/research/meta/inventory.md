# Meta — Инвентарь

Снимок после cleanup 18 мая 2026.

Инвентарь перечисляет meta/control handles и gaps. Если нужен код live skill,
проверять установленный handle: Claude Code через marketplace/cache, Codex через
`/Users/triton/.codex/skills`.

## Shared

### 1work-review

- Тип: skill
- Где есть: Claude Code, Codex
- Что делает: сверяет результат с criteria/evidence и держит repair loop до
  качественного закрытия.

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

### repo-power-tools

- Тип: skill
- Где есть: Claude Code, Codex
- Что делает: fast CLI evidence для code/docs/package/security work.

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
  сейчас идут в instructions, `_ops/criteria/` или planning surfaces.

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

### user-truth

- Тип: skill
- Что делает: маршрутизирует durable user signals в instruction layer,
  criteria, strategy или task detail.

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
