# Tool catalog: `md tools --json` заменяет MCP listTools

## Цель
`md tools --json` — single source of truth для всех 29 tool descriptions (WHEN/WHY/INPUT/OUTPUT/ALT/COST + input_schema + annotations). Заменяет MCP `listTools` discovery механизм. Используется skills (через generated `references/tool-catalog.md`) и `md doctor`.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-000 закрыт (tool-signatures-snapshot.json = source)
- task-001 закрыт (canonical signatures)
- task-101 закрыт (есть `md_cli/`)

## Size budget (audit Implementation #8)

- Полный `md tools --json` должен быть **≤50KB**. Это входит в attention budget когда skill load каталог.
- Human-readable `md tools` (one-liners) — **≤5KB**. Это primary discovery path.
- Full per-tool descriptions — `md tools <name>` on-demand, не bulk.

## Codex agent discovery (audit Codex #7 + cycle-2 G8)

Codex не имеет `listTools` mechanism. Discovery идёт через `agents/openai.yaml.default_prompt` где должно быть явно:
- «Полный каталог инструментов: `md tools --json`»
- «Описание конкретного tool: `md tools <name>`»
- **Примеры наиболее частых invocations** (audit cycle-2 Codex G8): включить 3-5 common patterns inline в default_prompt — `md orient`, `md search`, `md status`, `md preflight`, `md changed`. Без примеров Codex агент может не вызвать `md tools --json` каждой сессии (catalog как sole guidance — lossy против Claude's listTools).

Этот hint живёт в `default_prompt`, обновляется в task-302/305.

## Contract guarantee (architectural review)

`catalog.py` — **the single source of truth для 29-tool contract**. Из catalog можно за один lookup получить:
- Какой Python function tool вызывает (library_function для atomic / workflow_function для workflow)
- Где живёт handler (handler_module)
- Где живёт test (tests_module)
- Какие argparse flags принимает (cli_signature + input_schema)
- Описание для агента (description.when/why/input/output)
- Метаданные (annotations, category)

Test `tests/test_catalog_contract.py` verifies для каждого entry: handler_module importable, library_function или workflow_function importable (точно один из двух), tests_module exists.

**Tool count contract**:
- 24 atomic: 16 navigator + 8 graph (см. README §Tool count contract для полного списка)
- 5 workflow: 4 composite (orient, edit_context, refactor_candidates, query_by_type) + 1 hybrid (section_blast_radius)
- Total: 29 — matches MCP `TOOL_ANNOTATION_ALLOWLIST` в `mcp/src/server.js`
- Catalog enforces этот count: assert `len(TOOLS) == 29` в `__init__`

## Подшаги

- [x] Дизайн каталога как **contract map** (architectural review — single source of truth для всех 29 tools). Один Python модуль `src/md_cli/catalog.py`:
  ```python
  TOOLS = {
      "md_orient": {
          "name": "md_orient",
          "cli_name": "orient",                     # CLI subcommand (kebab-case)
          "category": "workflow",                   # atomic | workflow | mutating
          "library_function": None,                 # для atomic — "navigator.status"
          "workflow_function": "navigator.workflows.orient",  # для workflow
          "handler_module": "md_cli.handlers.md_orient",
          "tests_module": "tests.test_workflow_orient",
          "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
          "description": {
              "when": "...",
              "why": "...",
              "input": "...",
              "output": "...",
              "alt": "...",
              "cost": "..."
          },
          "input_schema": {  # JSON Schema
              "type": "object",
              "properties": {...},
              "required": [...]
          },
          "cli_signature": "md orient --corpus PATH [--top N] [--compact]",
      },
      "md_status": {
          "name": "md_status",
          "cli_name": "status",
          "category": "atomic",
          "library_function": "navigator.status",
          "workflow_function": None,
          "handler_module": "md_cli.handlers.md_status",
          ...
      },
      ...  # 29 entries total
  }
  ```
  
  **Contract guarantee**: для любого tool можно через one lookup определить какой Python function он вызывает, какой handler где живёт, какой test покрывает. Это устраняет drift через 6 месяцев.

- [x] Содержимое — портировать из текущего MCP contract, не из старых hand-counts:
  - `mcp/src/server.js` — allowlist annotations + inline `md_ping`
  - `mcp/src/tools/navigator-tools.js` — navigator registrations, including `md_profile_sections`
  - `mcp/src/tools/graph-tools.js` — graph registrations, including current `md_init` / `md_strip` locality
  - `mcp/src/tools/composite-tools.js` — 4 workflow tools
  - `mcp/src/tools/hybrid-tools.js` — `md_section_blast_radius`
  - `mcp/test/mcp-contract-check.js` — expected 29 names + annotations as validation source
  - Zod-схемы переводить в JSON Schema (без потери констрейнтов)

- [x] Создать handler `src/md_cli/handlers/tools.py`:
  - `md tools` без args → human-readable list (name + одна строка WHEN)
  - `md tools --json` → handler returns `ToolResult(payload={"tools": ...})`; runner wraps envelope
  - `md tools <tool_name>` → full description одного tool
  - `md tools <tool_name> --json` → один tool entry

- [x] Декоратор `@from_catalog(name)` для других handlers:
  - Использует catalog как single source of truth для argparse:
    - argparse parser строится из `input_schema` (типы, required, choices)
    - help text берётся из `description.when` (короткая) + `description.input`
  - Это гарантирует что catalog и actual CLI flags не расходятся

- [x] Создать `scripts/generate_tool_catalog_md.py`:
  - Читает catalog, генерирует Markdown table для `references/tool-catalog.md`
  - Output формат:
    ```md
    # md CLI tools — каталог
    
    Сгенерировано автоматически. Не править руками.
    
    | Tool | Category | WHEN | CLI signature |
    |---|---|---|---|
    | md_orient | composite | New corpus orientation | `md orient --corpus PATH` |
    ...
    
    ## Полные описания
    ### md_orient
    **WHEN**: ...
    **WHY**: ...
    ...
    ```

- [x] Tests `tests/test_catalog_contract.py`:
  - test: catalog содержит ровно 29 entries
  - test: catalog names match `tests/golden/mcp-tool-snapshot.json`
  - test: каждый entry имеет required keys (name, category, description.when/why/input/output, input_schema)
  - test: `md tools --json` returns valid JSON with envelope
  - test: `md tools md_orient` returns details
  - test: `md tools nonexistent` returns exit 2 + error

- [x] Создать `tests/test_catalog_signature_match.py`:
  - Для каждого tool в catalog — assert что argparse parser генерирует те же flags что описаны в `cli_signature`
  - Это catches drift между catalog declaration и actual handler implementation

## Готово
- [x] `src/md_cli/catalog.py` содержит 29 entries
- [x] `src/md_cli/handlers/tools.py` реализован (subcommand `md tools`)
- [x] `scripts/generate_tool_catalog_md.py` существует, выдаёт valid Markdown
- [x] `tests/test_catalog_contract.py` — 6 тестов зелёные
- [x] `tests/test_catalog_signature_match.py` — все 29 совпадений проходят
- [x] `md tools --json` возвращает все 29 tools с envelope

## Красные линии
- [ ] Не выдумывать новые tool descriptions. Берём как есть из MCP `*.js` files.
- [ ] Не дублировать argparse-config в handlers; используем catalog как source of truth.
- [ ] Не делать catalog runtime mutable (после load).

## Проверка
1. `md tools --json | jq '.tools | length'` → 29
2. `md tools --json | jq '._envelope.tool'` → `md_tools`
3. `md tools md_orient | grep "WHEN"` → есть
4. `cd experiments/md-embedding-server && uv run pytest tests/test_catalog_contract.py tests/test_catalog_signature_match.py -v` → all green
5. `python3 scripts/generate_tool_catalog_md.py > /tmp/cat.md && wc -l /tmp/cat.md` → значительно больше 29 строк (с table + full descriptions)

## Evidence

- `md tools --json | jq '{len:(.tools|length), tool:._envelope.tool}'` → `len=29`, `tool=md_tools`.
- `md tools --json | wc -c` → 48,524 bytes (under 50 KiB).
- `md tools | wc -c` → 3,914 bytes (under 5 KiB).
- `python3 scripts/generate_tool_catalog_md.py | wc -l` → 443 lines.
- `uv run pytest tests/test_catalog_contract.py tests/test_catalog_signature_match.py -q` → 7 passed.
- `uv run pytest tests/ -q` → 133 passed.
