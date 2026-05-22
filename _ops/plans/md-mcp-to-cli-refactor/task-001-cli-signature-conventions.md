# Зафиксировать CLI signature conventions

## Цель
Единый стиль CLI flags по всем 29 tools, выработанный и зафиксированный **до** начала миграции. Без этого 60% migration cost — это переписывание сигнатур задним числом (riski от субагента S3).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` — repo-wide правила
- `experiments/md-embedding-server/AGENTS.md` (subtree, если есть)

## Подшаги

- [ ] Решить convention для **nested objects**. Сейчас MCP принимает `filter: { type: ["decision"], depth: 2 }`. Варианты:
  - (a) JSON string в одном flag: `--filter '{"type":["decision"],"depth":2}'`
  - (b) Flat flags: `--filter-type decision --filter-depth 2`
  - **Default рекомендация**: (b) для tools где nested ≤2 уровней (читабельнее), (a) только если nested структура динамическая (как `path_include`/`path_exclude` — массивы строк).

- [ ] Решить convention для **arrays**. Варианты:
  - (a) Multiple flags: `--path-include foo --path-include bar`
  - (b) Comma-separated: `--path-include foo,bar`
  - **Default рекомендация**: (a) для path filters (могут содержать `,`), (b) для enums типа `--types open-question,decision`.

- [ ] Решить convention для **booleans**.
  - Presence-based: `--compact` (no value) → True; absent → default
  - Для negation если нужно: `--no-compact`
  - Никаких `--compact true` / `--compact=1`

- [ ] Решить convention для **optional params**.
  - Skip — просто не передавать
  - Никогда не `--limit ""` или `--limit null`
  - В коде: `argparse` без `required=True`, default `None`

- [ ] Решить convention для **JSON output**.
  - Все 29 tools: `--json` flag → structured JSON в stdout c `_envelope`
  - Без `--json` — human-readable summary (для CLI debugging)
  - Skills всегда передают `--json`

- [ ] Решить convention для **subcommand names + multi-word**:
  - MCP tool `md_orient` → CLI subcommand `orient` (без префикса `md_`)
  - **Multi-word** (audit Implementation #1): existing `md_navigator.py` использует kebab-case (`read-related`, `repeated-concepts`). MCP tools — snake_case (`md_read_related`). Decision: **CLI subcommands в kebab-case** (`md read-related`, `md repeated-concepts`) — matches Unix CLI conventions + existing `md_navigator.py`. Mapping MCP `md_X_Y` → CLI `md x-y` живёт в `catalog.py` explicitly.
  - Группировки нет (29 в плоском namespace). `md <tool> <flags>`
  - Документировать как mapping table в `cli-signatures-canonical.md`

- [ ] Решить convention для **paths**.
  - Все path args — positional или `--path` named arg (consistent across tools)
  - `corpus` — positional первый (если есть), как сейчас в `md_navigator.py status <corpus>`

- [ ] Записать все decisions в `experiments/md-embedding-server/docs/cli-conventions.md` как **rationale + canonical example** для каждого правила.

- [ ] Создать `experiments/md-embedding-server/docs/cli-signatures-canonical.md`: таблица **MCP tool → CLI subcommand → точная сигнатура с flags + типы + дефолты** для каждого из 29. Это input для task-201/202/203/204.

## Готово
- [ ] `docs/cli-conventions.md` существует, перечисляет 7 conventions выше с явным выбором и rationale.
- [ ] `docs/cli-signatures-canonical.md` существует, содержит 29 строк (по одной на tool), каждая с полной CLI signature.
- [ ] Минимум одна edge case для каждой convention документирована (когда convention рушится / исключение).

## Красные линии
- [ ] Не начинать писать код (`md_cli/`) до закрытия этой задачи.
- [ ] Не дробить convention по tools "case-by-case" — single ruleset для всех 29.
- [ ] Не копировать MCP JSON Schema as-is; CLI signatures это другой стиль (flags, не nested objects).
- [ ] **Не committing на framework без task-002 spike**: argparse-vs-Typer-vs-catalog-driven решается в task-002 на основе реального impl 3 hardest tools. Это task — about flag conventions; task-002 — about framework. Не путать.

## Проверка
1. `cat experiments/md-embedding-server/docs/cli-conventions.md | wc -l` — не пустой
2. `grep -c "^|" experiments/md-embedding-server/docs/cli-signatures-canonical.md` — минимум 30 строк (29 tools + header)
3. Manual: 3 случайных tool — sigatures в canonical.md имеют все flags из original MCP schema
