# Exact candidate — 1index — 2026-08-29

Этот каталог — candidate-overlay, не tracked owner и не installed projection.
Пять файлов ниже образуют изменяемые байты.

- `SKILL.md`
- `references/admission.md`
- `references/writing.md`
- `references/upkeep.md`
- `platforms/codex/agents/openai.yaml`

Gate: `check-instructions` + `check-trajectory` + неизменный causal/behavioral
probe. Только положительный verdict разрешает применить overlay к tracked owner
и запустить projection sync.
