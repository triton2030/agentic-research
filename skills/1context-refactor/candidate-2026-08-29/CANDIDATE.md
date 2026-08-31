# Exact candidate — 1context-refactor — 2026-08-29

Этот каталог — candidate-overlay, не tracked owner и не installed projection.
Девять файлов ниже образуют изменяемые байты.

- `SKILL.md`
- `references/failure-signals.md`
- `references/preservation.md`
- `references/refactor.md`
- `references/coherence.md`
- `references/simplify.md`
- `references/audit.md`
- `references/check.md`
- `platforms/codex/agents/openai.yaml`

Gate: `check-instructions` + `check-trajectory` + неизменный causal/behavioral
probe. Только положительный verdict разрешает применить overlay к tracked owner
и запустить projection sync.
