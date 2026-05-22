# Atomic tools migration: 16 navigator + 8 graph = 24 handlers

## Цель
Реализовать handlers для **24 atomic tools** (16 navigator + 8 graph). Это самая объёмная (по количеству) часть. Каждый handler — тонкая обёртка (≤30 LOC) над `navigator/` library с argparse → keyword args → `ToolResult`. **Никакого envelope/print в handlers** — runner владеет этим.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости (ORDER: 202a сначала, потом 201)
- task-101 закрыт (dispatch + runner + ToolResult)
- task-102 закрыт (envelope — wrapped by runner only)
- task-104 закрыт (catalog с canonical signatures)
- task-001 закрыт (CLI conventions)
- **task-106 (architecture lock) closed — gate**
- **task-202a closed — public navigator/* functions exist before handlers wrap them**

Reasoning: если task-201 идёт до task-202a, handlers начнут оборачивать старые `cmd_*` функции из `scripts/md_navigator.py` (stdout parsing antipattern), и public library появится задним числом. Правильный порядок: skeleton → architecture lock → public API → handlers → workflows → mutating.

## Подшаги

- [ ] Зафиксировать список atomic handlers (24 файла в `src/md_cli/handlers/`) — точная сверка с MCP `TOOL_ANNOTATION_ALLOWLIST` минус 5 workflows:
  - **Navigator atomic (16)**: md_ping, md_status, md_ls, md_toc, md_read_related, md_importance, md_extract, md_search, md_overlaps, md_repeated_concepts, md_audit, md_corpus_scan, md_index, md_init, md_strip, md_profile_sections
  - **Graph atomic (8)**: md_scan, md_check, md_health, md_cycles, md_deps, md_impact, md_preflight, md_changed
  - **Mutating** (md_init, md_strip, md_index, md_profile_sections с dry-run/confirm/fingerprint) — handler skeleton здесь, transaction protocol в task-204
  - **Tool count correction** (architectural review): previous plan said «22 navigator + 8 graph = 30» — это **ошибка**. Реально 16 navigator + 8 graph = 24 atomic. Composite (4) + hybrid (1) = 5 workflows = task-202/203. Total 24 + 5 = 29 = matches MCP listTools.

- [ ] Для каждого handler — шаблон файла `handlers/md_<name>.py` (после architectural review — ToolResult pattern, no JSON printing):
  ```python
  from md_cli.result import ToolResult
  from md_cli.catalog import TOOLS
  import navigator
  
  TOOL_NAME = "md_<name>"
  
  def add_argparse(subparser):
      """Configure argparse subparser from catalog input_schema."""
      ...
  
  def run(args) -> ToolResult:
      """argparse Namespace → ToolResult. NO JSON printing, NO envelope, NO sys.exit."""
      try:
          payload = navigator.<library_function>(args.corpus, ...)
          exit_code = 0 if not payload.get("empty") else 1
          return ToolResult(payload=payload, exit_code=exit_code)
      except FileNotFoundError:
          return ToolResult(payload={"error": "path_not_found"}, exit_code=2)
      except DependencyError:
          return ToolResult(payload={"error": "dependency_failed"}, exit_code=3)
  ```
  
  **Архитектурные правила handler**:
  - Handler ≤30 LOC
  - НЕ импортирует `envelope` module
  - НЕ печатает JSON
  - НЕ вызывает `sys.exit`
  - Только: argparse parse → call library function → return ToolResult
  - Runner (`md_cli/runner.py`) делает envelope.wrap() + print + exit

- [ ] **Handler boundary (architectural lock — task-106)**: handler НЕ:
  - не импортирует `envelope` module
  - не печатает JSON
  - не вызывает `envelope.wrap()` сам
  - не вызывает `sys.exit`
  - Handler ТОЛЬКО: parse args → call library function → return ToolResult(payload, exit_code)
  - Runner (`src/md_cli/runner.py`) — единственный точка envelope.wrap() + print(json.dumps()) + exit

- [ ] Для **handlers требующих warm index** (md_overlaps, md_audit, md_repeated_concepts, md_search, md_query_by_type, md_refactor_candidates):
  - Если library function raises `IndexWarmupRequired` exception → handler returns `ToolResult(payload={"error": "index_warmup_required", "corpus": ...}, exit_code=4)`
  - Runner intercepts exit_code=4 → envelope.next_step заполняет 3 directives (md_index dry-run, md_index confirm, retry original)
  - Handler сам next_step не строит — это runner's job

- [ ] Lazy imports per handler:
  - `from navigator import search` — только внутри `run()`, не на module-load
  - Это держит cold start light для tools которые не нуждаются в heavy deps
  - Verified в `tests/test_lazy_imports.py` (task-106)

- [ ] Tests: `tests/test_atomic_handlers.py`:
  - Один параметризованный test для всех 24 handlers:
    - Call handler.run(args) directly (in-process, не subprocess)
    - Assert: returns `ToolResult` instance с правильным payload type
    - Assert: exit_code в {0, 1, 2, 3, 4}
  - End-to-end test через CLI (subprocess) для sanity на 5-6 representative tools — full pipeline (argparse + handler + runner + envelope)

- [ ] **Goldensnap parity test** `tests/test_mcp_cli_parity.py` (snapshot-based из task-106):
  - Source of truth: `tests/golden/mcp-tool-snapshot.json` (frozen contract из task-106) + `tests/golden/mcp-responses/<tool>.json` (sample outputs из task-000)
  - Для каждого из 24 atomic tools:
    - Spawn `md <tool> --json` с canonical args (same args что использовались для snapshot)
    - Diff JSON outputs (volatile fields stripped to `"__VOLATILE__"`)
  - Этот test runs **без живого MCP** — survives Phase 5 deletion полностью
  - Phase 5 (task-501/502) только verifies test green; не создаёт parity tests

- [ ] Verify exit codes match canonical MCP behavior:
  - 0 — success
  - 1 — empty/no-result
  - 2 — usage/path error
  - 3 — dependency/API failure
  - 4 — index warmup refusal

## Готово
- [ ] 24 файла в `src/md_cli/handlers/md_*.py` существуют (atomic)
- [ ] Каждый handler ≤30 LOC (thin) — enforced через test
- [ ] Каждый handler возвращает `ToolResult`, не печатает JSON, не импортирует envelope
- [ ] `md <tool> --help` работает для всех 24 (argparse правильный)
- [ ] `tests/test_atomic_handlers.py` — все 24 passes
- [ ] `tests/test_mcp_cli_parity.py` (snapshot-based) — все 24 parity matches проходят
- [ ] Lazy imports verified (например `md ping` не подгружает NetworkX)
- [ ] Architecture invariant tests passes: handlers не импортируют envelope, не печатают JSON

## Красные линии
- [ ] Не копировать логику из `navigator/` в handlers. Handler — только argparse + library call.
- [ ] Не делать handler `>30 LOC` — если нужно больше, значит логика должна жить в `navigator/`.
- [ ] **Handler не импортирует envelope, не печатает JSON, не вызывает sys.exit**. Architecture lock (task-106) enforces.
- [ ] Не нарушать lazy-imports — не делать `from networkx import ...` на module top.
- [ ] Не дрейфовать exit codes от canonical mapping (0/1/2/3/4).

## Проверка
1. `ls src/md_cli/handlers/md_*.py | wc -l` → 24 (НЕ 30 — точное число atomic = 16 navigator + 8 graph)
2. `md ping --json | jq '._envelope.tool'` → "md_ping" (envelope wrapped runner-ом, не handler-ом)
3. `cd experiments/md-embedding-server && uv run pytest tests/test_atomic_handlers.py -v` → 24/24 green
4. `cd experiments/md-embedding-server && uv run pytest tests/test_mcp_cli_parity.py -v` → 24/24 green (snapshot-based)
5. `cd experiments/md-embedding-server && uv run pytest tests/test_architecture_boundaries.py -v` → all green (handlers без envelope/print/sys.exit)
6. `md selftest --tool md_status` → pass
