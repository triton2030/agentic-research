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

## Подшаги

- [ ] Дизайн каталога. Один Python модуль `src/md_cli/catalog.py` с явной структурой:
  ```python
  TOOLS = {
      "md_orient": {
          "name": "md_orient",
          "category": "composite",  # atomic | composite | hybrid | mutating
          "annotations": {"readOnlyHint": True, "destructiveHint": False, ...},
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
          "handler_module": "md_cli.handlers.orient"
      },
      ...
  }
  ```

- [ ] Содержимое — портировать из текущих MCP tool registrations:
  - `mcp/src/tools/navigator-tools.js` (22 tools)
  - `mcp/src/tools/graph-tools.js` (8 tools)
  - `mcp/src/tools/composite-tools.js` (4 tools)
  - `mcp/src/tools/hybrid-tools.js` (1 tool)
  - Зод-схемы переводить в JSON Schema (без потери констрейнтов)

- [ ] Создать handler `src/md_cli/handlers/tools.py`:
  - `md tools` без args → human-readable list (name + одна строка WHEN)
  - `md tools --json` → весь каталог в JSON через envelope.wrap()
  - `md tools <tool_name>` → full description одного tool
  - `md tools <tool_name> --json` → один tool entry

- [ ] Декоратор `@from_catalog(name)` для других handlers:
  - Использует catalog как single source of truth для argparse:
    - argparse parser строится из `input_schema` (типы, required, choices)
    - help text берётся из `description.when` (короткая) + `description.input`
  - Это гарантирует что catalog и actual CLI flags не расходятся

- [ ] Создать `scripts/generate_tool_catalog_md.py`:
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

- [ ] Tests `tests/test_catalog.py`:
  - test: catalog содержит ровно 29 entries
  - test: каждый entry имеет required keys (name, category, description.when/why/input/output, input_schema)
  - test: `md tools --json` returns valid JSON with envelope
  - test: `md tools md_orient` returns details
  - test: `md tools nonexistent` returns exit 2 + error

- [ ] Создать `tests/test_catalog_signature_match.py`:
  - Для каждого tool в catalog — assert что argparse parser генерирует те же flags что описаны в `cli_signature`
  - Это catches drift между catalog declaration и actual handler implementation

## Готово
- [ ] `src/md_cli/catalog.py` содержит 29 entries
- [ ] `src/md_cli/handlers/tools.py` реализован (subcommand `md tools`)
- [ ] `scripts/generate_tool_catalog_md.py` существует, выдаёт valid Markdown
- [ ] `tests/test_catalog.py` — 5 тестов зелёные
- [ ] `tests/test_catalog_signature_match.py` — все 29 совпадений проходят
- [ ] `md tools --json` возвращает все 29 tools с envelope

## Красные линии
- [ ] Не выдумывать новые tool descriptions. Берём как есть из MCP `*.js` files.
- [ ] Не дублировать argparse-config в handlers; используем catalog как source of truth.
- [ ] Не делать catalog runtime mutable (после load).

## Проверка
1. `md tools --json | jq '.tools | length'` → 29
2. `md tools --json | jq '.tools[0]._envelope'` → есть envelope
3. `md tools md_orient | grep "WHEN"` → есть
4. `cd experiments/md-embedding-server && uv run pytest tests/test_catalog.py tests/test_catalog_signature_match.py -v` → all green
5. `python3 scripts/generate_tool_catalog_md.py > /tmp/cat.md && wc -l /tmp/cat.md` → значительно больше 29 строк (с table + full descriptions)
