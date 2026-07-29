# Composite tools: 4 handlers (workflows уже в navigator/workflows/)

## Цель
Реализовать **4 thin CLI handlers** для composite tools (md_orient, md_edit_context, md_refactor_candidates, md_query_by_type). Workflow logic уже implemented в `src/navigator/workflows/` из task-202a. Здесь — только handlers (Layer 3), которые вызывают workflow functions и возвращают ToolResult.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-202a закрыт (navigator/workflows/* функции готовы)
- task-101 закрыт (runner + ToolResult)
- task-104 закрыт (catalog с workflow_function references)
- task-106 закрыт (architecture lock — handlers без envelope/print)
- task-201 параллельно (не блокирует — handlers independent)

## Navigator public API — закрыто в **task-202a**

Это работа выделена в отдельный prerequisite task `task-202a-navigator-public-api-refactor.md` (audit cycle-2 Implementation G7). Composites используют public functions из `navigator/`, не subprocess.

**Dependency**: task-202a должен быть закрыт ДО старта task-202.

## Status — 2026-05-22

completed. `md_orient`, `md_edit_context`, `md_refactor_candidates`, and
`md_query_by_type` are Layer 2 workflows under `src/navigator/workflows/` with
thin Layer 3 handlers. Verification: `tests/test_composite_tools.py` and
`tests/test_composite_mcp_parity.py` passed; full suite 169 passed.

## Composite error semantics (audit Implementation #5)

**Decision: fail-fast.** Если один из 3 internal calls в composite падает → весь composite returns error envelope, не partial. Это matches existing MCP behavior (composite-tools.js uses Promise.all которые reject on first error).

Документировать в `navigator/workflows/__init__.py` docstring как architectural rule. Test на error propagation.

## Подшаги

## Architectural position

Workflows (`src/navigator/workflows/`) — implemented in task-202a (Layer 2). Здесь — только thin CLI handlers (Layer 3). Никаких реализаций workflow logic в `md_cli/`. Layer 4 (runner) делает envelope.

## Подшаги

- [ ] **Verify** что 4 workflow functions готовы в task-202a:
  - `from navigator.workflows import orient, edit_context, refactor_candidates, query_by_type` — все importable
  - Если что-то отсутствует — task-202a не закрыт, не продолжать

- [ ] **Workflow logic specifics** (документация для верификации task-202a — если detail отсутствует, return в task-202a):
  
  **navigator.workflows.orient** (md_orient):
  - Composition: navigator.status + navigator.ls/map + navigator.importance
  - Compact mode: top=3, max_heading_level=1, slim status, ~80% token reduction
  - Returns: `{workflow: "md_orient", corpus, status, files, importance, next}`
  
  **navigator.workflows.edit_context** (md_edit_context):
  - Composition: navigator.preflight + navigator.read_related (+ optional navigator.search if mode=full + query)
  - Modes: preview / full / strict
  - graphBlockers() helper — portировать BLOCKER_CODES set
  
  **navigator.workflows.refactor_candidates** (md_refactor_candidates):
  - Wraps navigator.refactor_candidates with compact mode logic
  - Sentinel `no_automation: true`
  
  **navigator.workflows.query_by_type** (md_query_by_type):
  - Wraps navigator.query_by_type with compact + filter
  - Validates types argument

- [ ] Handler shape `src/md_cli/handlers/md_orient.py` (ToolResult pattern, NO envelope import, NO JSON print):
  ```python
  from md_cli.result import ToolResult
  from navigator.workflows import orient
  
  TOOL_NAME = "md_orient"
  
  def add_argparse(subparser):
      ...
  
  def run(args) -> ToolResult:
      payload = orient(
          corpus=args.corpus, 
          top=args.top, 
          max_heading_level=args.max_heading_level,
          compact=args.compact,
      )
      return ToolResult(payload=payload, exit_code=0)
  ```
  Runner делает envelope + JSON + exit.

- [ ] **Архитектурное правило в `navigator/workflows/__init__.py`**:
  - Workflows import ONLY navigator atomic (library), never друг друга
  - Workflows НЕ import `md_cli.*` (one-way dependency: md_cli depends on navigator, не наоборот)
  - Workflows возвращают dict, не печатают JSON, не делают envelope
  - Это enforced через `tests/test_architecture_invariants.py`

- [ ] Tests `tests/test_composite_tools.py`:
  - test: md_orient compact vs full — payload size diff ~80%
  - test: md_edit_context preview vs full — bodies differ
  - test: md_edit_context strict — only blockers field
  - test: md_refactor_candidates — `no_automation: true` always present
  - test: md_query_by_type — invalid type → exit 2

- [ ] Parity test `tests/test_composite_mcp_parity.py`:
  - Для всех 4 composites — diff CLI vs MCP output (ignoring volatile envelope fields)

## Готово
- [ ] `src/navigator/workflows/{orient,edit_context,refactor_candidates,query_by_type}.py` существуют (Layer 2)
- [ ] `src/md_cli/handlers/{md_orient,md_edit_context,md_refactor_candidates,md_query_by_type}.py` существуют (Layer 3, thin wrappers)
- [ ] Каждый handler ≤30 LOC, возвращает ToolResult, не импортирует envelope
- [ ] `tests/test_workflow_orient.py`, ... — 5+ tests зелёные per workflow
- [ ] `tests/test_composite_mcp_parity.py` (snapshot-based) — 4/4 matches
- [ ] Architecture invariants: workflows не импортируют md_cli, handlers не импортируют envelope

## Красные линии
- [ ] Не вызывать composite из atomic handlers (anti-pattern).
- [ ] Не дублировать env переменные / API setup в каждом composite — общая логика в navigator/.
- [ ] Не реализовывать workflow logic в `md_cli/`. Composite workflow — Layer 2 в `navigator/workflows/`; CLI handler — только Layer 3 wrapper.

## Проверка
1. `md orient --corpus /tmp/test-corpus --json | jq '.workflow'` → "md_orient"
2. `md edit-context --path /tmp/file.md --mode strict --json | jq '.blockers'` → есть
3. `md refactor-candidates --corpus /tmp/test-corpus --json | jq '.no_automation'` → true
4. `cd experiments/md-embedding-server && uv run pytest tests/test_composite_tools.py tests/test_composite_mcp_parity.py -v` → all green
5. `grep -r "from md_cli\|import md_cli" src/navigator/workflows/` → 0 (workflows не depend на md_cli — architecture boundary test)
6. `find src/md_cli/composites src/md_cli/hybrid 2>/dev/null` → не существуют (workflows только в navigator/workflows/)
