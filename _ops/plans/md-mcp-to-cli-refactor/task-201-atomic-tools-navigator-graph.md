# Atomic tools migration: 22 navigator + 8 graph

## Цель
Реализовать handlers для 30 atomic tools (22 navigator + 8 graph). Это самая объёмная (по количеству), но самая механическая часть: каждый handler — тонкая обёртка над `navigator/` library с argparse → keyword args → envelope.wrap().

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-101 закрыт (dispatch)
- task-102 закрыт (envelope)
- task-104 закрыт (catalog с canonical signatures)
- task-001 закрыт (CLI conventions)

## Подшаги

- [ ] Зафиксировать список handlers (30 файлов в `src/md_cli/handlers/`):
  - **Navigator atomic (22)**: md_ping, md_status, md_ls, md_toc, md_map, md_headings, md_pick, md_read, md_read_related, md_importance, md_extract, md_index, md_search, md_overlaps, md_repeated_concepts, md_cluster, md_audit, md_profile_sections, md_originality, md_owner_candidates, md_corpus_scan, md_manifest
  - **Graph atomic (8)**: md_scan, md_check, md_health, md_cycles, md_deps, md_impact, md_preflight, md_changed
  - Mutating (md_init, md_strip, md_index с dry-run/confirm) → task-204, не здесь

- [ ] Для каждого handler — шаблон файла `handlers/md_<name>.py`:
  ```python
  from md_cli.envelope import wrap
  from md_cli.catalog import TOOLS
  from navigator import <relevant_module>
  
  TOOL = TOOLS["md_<name>"]
  
  def add_argparse(subparsers):
      """Generated from catalog input_schema."""
      ...
  
  def run(args) -> int:
      """argparse Namespace → JSON result via wrap()."""
      result = navigator.<relevant_module>.<func>(args.corpus, ...)
      envelope_result = wrap(result, tool_name="md_<name>", args=vars(args))
      print(json.dumps(envelope_result))
      return 0 if result.get("ok", True) else 1
  ```

- [ ] **Не дублировать логику** в handlers. Library functions в `navigator/` уже реализованы. Handler:
  - Парсит args → kwargs для library function
  - Вызывает library function
  - Оборачивает result через `envelope.wrap()`
  - Печатает JSON и возвращает exit code

- [ ] Для **8 mutating-проверочных** scenarios (md_overlaps, md_audit, md_repeated_concepts, md_cluster, md_search, md_query_by_type, md_refactor_candidates) — те что требуют warm index:
  - Если index cold → handler возвращает `{"error": "index_warmup_required", "corpus": ...}` без HTTP call
  - Envelope.next_step тогда заполняет 3 directives (md_index dry-run, md_index confirm, retry original)

- [ ] Lazy imports per handler:
  - `from navigator.search import ...` — только внутри `run()`, не на module-load
  - Это держит cold start light для tools которые не нуждаются в heavy deps

- [ ] Tests: `tests/test_atomic_handlers.py`:
  - Один параметризованный test для всех 30 handlers:
    - Spawn `md <tool> --json <minimal valid args>`
    - Assert: exit code 0 ИЛИ известный exit code (1=empty, 2=path, 3=dep, 4=warmup)
    - Assert: stdout — valid JSON, contains `_envelope` field
  - Per-tool тесты для специфичных edge cases (опционально, не все 30)

- [ ] **Goldensnap parity test** `tests/test_mcp_cli_parity.py` (audit Smith #5 + Implementation #7):
  - **Source of truth**: `tests/golden/mcp-responses/<tool>.json` (snapshot созданный в task-000), НЕ live MCP server
  - Для каждого из 30 atomic tools:
    - Load expected response from golden fixture
    - Запустить `md <tool> --json` с canonical args (same args что использовались для snapshot)
    - Diff JSON outputs (volatile fields из task-000 уже replaced на `"__VOLATILE__"` placeholders, ignore их при compare)
  - Это устраняет lifecycle conflict: parity tests survive Phase 5 removal of MCP

- [ ] Verify exit codes match canonical MCP behavior:
  - 0 — success
  - 1 — empty/no-result
  - 2 — usage/path error
  - 3 — dependency/API failure
  - 4 — index warmup refusal

## Готово
- [ ] 30 файлов в `src/md_cli/handlers/md_*.py` существуют
- [ ] Каждый handler ≤80 LOC (thin wrapper)
- [ ] `md <tool> --help` работает для всех 30 (argparse правильный)
- [ ] `tests/test_atomic_handlers.py` — все 30 passes
- [ ] `tests/test_mcp_cli_parity.py` — все 30 parity matches проходят
- [ ] Lazy imports verified (е.g. `md ping` не подгружает NetworkX)

## Красные линии
- [ ] Не копировать логику из `navigator/` в handlers. Handler — только argparse + wrap.
- [ ] Не делать handler `>100 LOC` — если нужно больше, значит логика должна жить в `navigator/`.
- [ ] Не нарушать lazy-imports — не делать `from networkx import ...` на module top.
- [ ] Не дрейфовать exit codes от canonical mapping.

## Проверка
1. `ls src/md_cli/handlers/md_*.py | wc -l` → 30
2. `md ping --json | jq '._envelope.tool'` → "md_ping"
3. `cd experiments/md-embedding-server && uv run pytest tests/test_atomic_handlers.py -v` → 30/30 green
4. `cd experiments/md-embedding-server && uv run pytest tests/test_mcp_cli_parity.py -v` → 30/30 green
5. `md selftest --tool md_status` → pass (sanity check)
