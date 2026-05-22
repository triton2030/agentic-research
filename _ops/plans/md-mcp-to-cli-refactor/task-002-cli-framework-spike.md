# CLI framework spike: argparse vs Typer

## Цель
Cheaper reversible probe **до** commit на framework (task-101). Собрать 3 hardest tool signatures как proof-of-concept на двух фреймворках. Решить какой использовать в Phase 1 на основе реального impl, не теории.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-001 закрыт (canonical signatures для 3 hardest tools зафиксированы)

## Подшаги

- [ ] Выбрать 3 hardest tools для spike (variety of edge cases):
  - `md_section_blast_radius` — hybrid с required query + optional heading_id + array filters
  - `md_query_by_type` — array of enum values как input (`--types`)
  - `md_edit_context` — mode enum (preview/full/strict) + optional query/corpus с branching behavior

- [ ] Implement spike в `experiments/md-embedding-server/spike/argparse_version.py`:
  - argparse + subparsers
  - Build parsers from canonical signatures (task-001 output)
  - Type validation, choices, defaults
  - `--help` для каждого работает
  - Return JSON output to stdout

- [ ] Implement spike в `experiments/md-embedding-server/spike/typer_version.py`:
  - Typer commands (3 functions с decorators)
  - Same signatures, type validation through Python type hints
  - Auto-generated help
  - JSON output

- [ ] Implement spike в `experiments/md-embedding-server/spike/catalog_driven.py`:
  - Catalog JSON Schema → argparse parser builder
  - Same 3 tools driven by JSON Schema descriptors
  - Test что это actually работает с nested objects / arrays

- [ ] Benchmark startup time:
  - `time python3 spike/argparse_version.py md_section_blast_radius --help`
  - same для typer
  - same для catalog_driven
  - Note cold vs warm (`__pycache__` warm)

- [ ] Verdict criteria (audit cycle-2 Smith G6 — catalog_driven это слой, не альтернатива):
  - **Phase A** — выбор framework (argparse vs Typer):
    - **Help quality**: которое `--help` output читабельнее для агента?
    - **Code volume**: сколько LOC для 3 tools в каждом подходе?
    - **Nested handling**: насколько чисто обрабатывают `md_section_blast_radius`?
    - **Maintenance**: добавить 4-й tool — насколько easy?
    - **Startup overhead**: ms cold start
  - **Phase B** — на победителе из A: catalog-driven vs hand-written tool registration
    - **Catalog integration**: насколько easy single source of truth?
    - **Drift risk**: вероятность что catalog и actual handler signature разойдутся

- [ ] Tie-breaker (audit cycle-2 Implementation G2):
  - Если все 3 фреймворка показали одинаковую quality:
    1. Lowest startup time <50ms wins
    2. Если близко — catalog-driven integration ease wins
    3. Если ещё близко — help quality для agent reader wins
    4. Если ещё близко — lowest LOC wins
  - Если **все 3 fail** на nested objects в `md_section_blast_radius`:
    - НЕ закрывать task-002 как «done»
    - Escalate в `1strategy` — possibly need different abstraction (custom DSL?) или сужение semantic equivalence (drop some MCP nested args)

- [ ] Document decision в `experiments/md-embedding-server/docs/cli-framework-decision.md`:
  - Verdict (argparse / Typer / catalog-driven)
  - Rationale (per criterion)
  - Trade-offs принимаются явно

- [ ] Clean up spike code:
  - `experiments/md-embedding-server/spike/` сохраняется как evidence для closeout
  - Не оставлять spike code в `src/` после verdict

## Готово
- [ ] 3 spike реализации существуют (argparse, typer, catalog_driven)
- [ ] Benchmark numbers зафиксированы
- [ ] `docs/cli-framework-decision.md` существует с явным verdict
- [ ] task-101 может использовать decision как input

## Красные линии
- [ ] Не делать spike production-ready (no tests, no envelope, no edge cases beyond 3 tools)
- [ ] Не строить полный CLI в spike — это reversible probe, не impl
- [ ] Не оставлять spike в `src/` permanent
- [ ] Не делать verdict без 3 real tool impls — на абстрактных шаблонах оба фреймворка одинаковые

## Проверка
1. `ls experiments/md-embedding-server/spike/` → 3 файла
2. `cat experiments/md-embedding-server/docs/cli-framework-decision.md | grep "Verdict:"` → has answer
3. Manual: запустить `python3 spike/argparse_version.py md_section_blast_radius --help` — work
4. Manual: запустить `python3 spike/typer_version.py md-section-blast-radius --help` — work
