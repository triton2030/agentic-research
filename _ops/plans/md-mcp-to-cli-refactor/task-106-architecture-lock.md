# Architecture lock — gate перед tool-specific implementation

## Цель
Прежде чем писать handler/workflow/library код 29 tools — зафиксировать architectural invariants через generated artifacts + tests. Без этой gate существует риск построить две параллельные архитектуры (старые cmd_* + новый layered design) что превратит refactor в косметический.

Это **gate**, не just task. Phase 2 не стартует пока tests здесь не зелёные.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-101 закрыт (package skeleton, runner, ToolResult dataclass)
- task-102 закрыт (envelope module)
- task-103 закрыт (transactions module)
- task-104 закрыт (catalog.py skeleton с 29 entries)

## Подшаги

- [ ] **MCP tool snapshot — generated, не hand-written**:
  - Script `experiments/md-embedding-server/scripts/generate-mcp-tool-snapshot.py`:
    - Запускает live MCP server через subprocess
    - Вызывает `listTools` RPC
    - Сохраняет normalized output в `tests/golden/mcp-tool-snapshot.json` (29 entries, each имеет: name, description, inputSchema, annotations)
    - Volatile fields (если есть) — placeholdered
  - Этот snapshot — frozen contract. Любая правка catalog.py должна проходить validation против него.

- [ ] **catalog.py validation** против snapshot:
  - `tests/test_catalog_contract.py`:
    - Load `tests/golden/mcp-tool-snapshot.json`
    - For каждый snapshot entry:
      - `TOOLS[entry.name]` существует в catalog.py
      - `TOOLS[entry.name].input_schema` matches snapshot schema (or compatible JSON Schema)
      - `TOOLS[entry.name].annotations` matches
      - `TOOLS[entry.name].description.when/why/...` non-empty
    - Assert `len(TOOLS) == 29` (точно matches snapshot count)
    - Assert каждый entry имеет либо `library_function` ЛИБО `workflow_function` (exclusive)
    - Assert importability: `importlib.import_module(TOOLS[name].handler_module)` works
    - Assert `library_function` или `workflow_function` resolvable: `getattr(navigator, ...)` works

- [ ] **Architecture boundary tests** `tests/test_architecture_boundaries.py`:
  
  **Handlers boundary**:
  - `grep -rn "print(json" src/md_cli/handlers/` → 0 (handlers не печатают JSON)
  - `grep -rn "json.dumps" src/md_cli/handlers/` → 0
  - `grep -rn "from md_cli.envelope" src/md_cli/handlers/` → 0 (handlers не импортируют envelope)
  - `grep -rn "from md_cli import envelope" src/md_cli/handlers/` → 0
  - `grep -rn "sys.exit" src/md_cli/handlers/` → 0 (handlers не делают sys.exit)
  - Каждый handler module имеет: `def run(args) -> ToolResult` signature (assert через AST inspection)
  
  **Workflows boundary**:
  - `grep -rn "from md_cli" src/navigator/workflows/` → 0 (workflows не зависят от md_cli)
  - `grep -rn "import md_cli" src/navigator/workflows/` → 0
  - `grep -rn "subprocess" src/navigator/workflows/` → 0 (workflows вызывают functions directly, не CLI)
  - `grep -rn "json.dumps" src/navigator/workflows/` → 0 (workflows return dict, не serialize)
  - Workflow functions return dict (assert через AST inspection)
  
  **Runner ownership**:
  - `grep -rn "envelope.wrap\|envelope_wrap" src/` → only matches в `src/md_cli/runner.py` (1 file, единственный envelope owner)
  - `grep -rn "print(json" src/` → only matches в `src/md_cli/runner.py` (1 file)
  - `grep -rn "sys.exit" src/` → only matches в `src/md_cli/main.py` и `src/md_cli/runner.py`
  
  **Library boundary**:
  - `grep -rn "from md_cli\|import md_cli" src/navigator/` (вне workflows/) → 0 (atomic library НЕ depends на CLI)

- [ ] **Adversarial transaction tests** `tests/test_transactions_adversarial.py`:
  - **Args mismatch**: dry_run с args={path:"A"} → confirm с args={path:"B"} + transaction_id → `intent_mismatch` error (не silent accept)
  - **Double confirm**: confirm с transaction_id → consume; повтор confirm с тем же id → `unknown_or_expired`
  - **Concurrent confirm race**: 2 параллельных confirm с тем же id (semaphore синхронизация) → ровно один выигрывает, второй получает `unknown_or_expired` или `drift_detected`
  - **Corrupt txn file**: cache file существует но invalid JSON → `unknown_or_expired` (не uncaught exception)
  - **PermissionError**: cache directory read-only → graceful fallback к stateless `--fingerprint` mode (или явный error если no fingerprint)
  - **Confirm без transaction_id и без fingerprint**: → `confirm_required` (нельзя получить runnable confirm в next_step без dry-run сначала)
  - **Cost bounds check**: dry_run estimated_cost = $0.50; confirm выполняется но реальный cost > $0.55 (10% over) → record + warning в payload (не блокер, но visible)
  - **Affected set re-verify**: dry_run identified 5 files; между dry-run и confirm 6-й файл создан (would be affected) → `affected_set_drift` (не just content fingerprint mismatch)

- [ ] **Lazy imports tests** `tests/test_lazy_imports.py`:
  - `md --help` — не загружает `networkx`, `numpy`, `scipy`, `pymorphy3`, `requests` (через `sys.modules` check after subprocess)
  - `md tools --help` — не загружает heavy deps
  - `md tools` (list) — не загружает heavy deps
  - `md ping --help` — не загружает heavy deps  
  - `md status --help` — не загружает heavy deps
  - `md status .` (atomic, simple) — может загрузить sqlite3 + frontmatter, но НЕ networkx unless actually needed для graph operations
  - **Target**: cold startup `md status` <300ms (audit cycle-1 perf goal)

- [ ] **Snapshot mismatch CI gate**:
  - Если snapshot обновляется (regenerate из live MCP), catalog.py диfference → CI fails
  - Это catches «catalog drift» — кто-то поменял MCP source без обновления catalog
  - Documented в `experiments/md-embedding-server/docs/architecture-lock.md`

## Готово
- [ ] `tests/golden/mcp-tool-snapshot.json` — 29 entries, generated from live MCP
- [ ] `scripts/generate-mcp-tool-snapshot.py` существует
- [ ] `tests/test_catalog_contract.py` — все assertions зелёные (29 entries + importability)
- [ ] `tests/test_architecture_boundaries.py` — 4 sections (handlers/workflows/runner/library) все зелёные
- [ ] `tests/test_transactions_adversarial.py` — 8 scenarios зелёные
- [ ] `tests/test_lazy_imports.py` — 6 scenarios зелёные
- [ ] `docs/architecture-lock.md` существует с invariants documentation

## Красные линии
- [ ] **Этот task — GATE**. Phase 2 (tool-specific implementation) НЕ начинается пока tests здесь не green.
- [ ] Не writing tool handlers / workflows / library functions в этой задаче. Только architectural gates + skeletons.
- [ ] Не loosenить boundary tests «временно потому что mn нужно implement». Если тест fails — fix architecture, не test.
- [ ] Snapshot — frozen artifact. Никаких manual правок. Только regenerate из live MCP.

## Проверка
1. `cat tests/golden/mcp-tool-snapshot.json | jq '. | length'` → 29
2. `cd experiments/md-embedding-server && uv run pytest tests/test_catalog_contract.py tests/test_architecture_boundaries.py tests/test_transactions_adversarial.py tests/test_lazy_imports.py -v` → all green
3. `time md --help` → <300ms cold
4. Sanity: добавить «дырку» в handler (`print(json.dumps({...}))` в фейковом handler) → `test_architecture_boundaries.py` ловит
