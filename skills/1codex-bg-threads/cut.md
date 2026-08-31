# Вырезано и поглощено

## Accepted candidate compression 2026-08-30

Core сокращён с минимум `23`, затем `20`, до `5` независимо действующих
единиц. Model, environment, reuse, verification и lifecycle остаются только в
нативной поверхности; prompt-форма — только в receiver surface.

Из receiver surface удалены перечисления полей и восьмичастная карточка:
commander intent владеет формой `# Контекст` → `# Цель`, а дополнительная секция
появляется только при concrete omission harm.

Из native surface удалены per-command checklist и повторяющиеся state rules.
Остались пять самостоятельных текущих решений: mode, route, reuse, launch и
managed closure; максимальный active set — `20`.

## Снято осознанно

- Typed `THREAD_CARD` и `THREAD_DONE`.
- Predicate architecture и отдельные stage-files ради budget.
- Дубли native decisions между core и reference.
- Фиксированные waves, retries, verifier fleet и универсальные terminal enums.
- Installation, projection и approval procedures.

Exact preservation и conservative semantic counts находятся в
[`preservation-map-2026-08-30.md`](preservation-map-2026-08-30.md).
