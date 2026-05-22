# Composite tools: md_orient, md_edit_context, md_refactor_candidates, md_query_by_type

## Цель
Реализовать 4 composite tools. Каждый — composition нескольких navigator/graph library calls. Critical: composite live в **отдельном** `src/md_cli/composites/` namespace (S1 раunhinged: «conceptual integrity composite-vs-atomic»).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-201 закрыт (atomic handlers готовы)
- task-202a закрыт (navigator public API exposed)
- task-102 закрыт (envelope)
- task-104 закрыт (catalog)

## Navigator public API — закрыто в **task-202a**

Это работа выделена в отдельный prerequisite task `task-202a-navigator-public-api-refactor.md` (audit cycle-2 Implementation G7). Composites используют public functions из `navigator/`, не subprocess.

**Dependency**: task-202a должен быть закрыт ДО старта task-202.

## Composite error semantics (audit Implementation #5)

**Decision: fail-fast.** Если один из 3 internal calls в composite падает → весь composite returns error envelope, не partial. Это matches existing MCP behavior (composite-tools.js uses Promise.all которые reject on first error).

Документировать в `composites/__init__.py` docstring как architectural rule. Test на error propagation.

## Подшаги

- [ ] Создать `src/md_cli/composites/__init__.py` пустой.

- [ ] Реализовать `src/md_cli/composites/orient.py` (md_orient):
  - Composition: navigator.status + navigator.map (with link counts) + navigator.importance (top N)
  - Compact mode: top=3, max_heading_level=1, slim status fields, files limited to path+description (~80% token reduction)
  - Full mode: status + files (с link counts) + importance + `next` hint string
  - Все 3 internal calls идут через library API directly (не subprocess), thus shared cache, fast
  - Returns dict с keys `{workflow: "md_orient", corpus, status, files, importance, next}`

- [ ] Реализовать `src/md_cli/composites/edit_context.py` (md_edit_context):
  - Modes: preview / full / strict
  - Composition: graph.preflight + navigator.read_related (+ optional navigator.search if mode=full + query)
  - Strict: returns только blockers (preflight projected)
  - Preview: short related (token_budget=1200)
  - Full: long related (token_budget=6000) + optional search
  - graphBlockers() helper — портировать из composite-tools.js (set BLOCKER_CODES, compute has_blockers)

- [ ] Реализовать `src/md_cli/composites/refactor_candidates.py` (md_refactor_candidates):
  - Single call to navigator.refactor_candidates() with flags
  - Compact mode: top 3 only, minimal evidence (drop heading_chain/confidence in проprietary), `compact: true` flag в response
  - Sentinel field `no_automation: true` — never auto-applies

- [ ] Реализовать `src/md_cli/composites/query_by_type.py` (md_query_by_type):
  - Single call to navigator.query_by_type() with types array
  - Compact mode: limit≤10, drop heading_chain/confidence
  - Validate types argument (one of allowed enum values)

- [ ] Handler shape `src/md_cli/handlers/md_orient.py`:
  ```python
  from md_cli.composites.orient import run_orient
  from md_cli.envelope import wrap
  
  def run(args) -> int:
      result = run_orient(corpus=args.corpus, top=args.top, ...)
      print(json.dumps(wrap(result, tool_name="md_orient", args=vars(args))))
      return 0
  ```

- [ ] **Архитектурное правило в `composites/__init__.py`**:
  - Composites import ONLY navigator (library), never друг друга
  - Composites не import md_cli.handlers
  - Это запретит accidental coupling через 6 месяцев

- [ ] Tests `tests/test_composite_tools.py`:
  - test: md_orient compact vs full — payload size diff ~80%
  - test: md_edit_context preview vs full — bodies differ
  - test: md_edit_context strict — only blockers field
  - test: md_refactor_candidates — `no_automation: true` always present
  - test: md_query_by_type — invalid type → exit 2

- [ ] Parity test `tests/test_composite_mcp_parity.py`:
  - Для всех 4 composites — diff CLI vs MCP output (ignoring volatile envelope fields)

## Готово
- [ ] `src/md_cli/composites/{orient,edit_context,refactor_candidates,query_by_type}.py` существуют
- [ ] `src/md_cli/handlers/{md_orient,md_edit_context,md_refactor_candidates,md_query_by_type}.py` существуют
- [ ] `tests/test_composite_tools.py` — 5+ tests зелёные
- [ ] `tests/test_composite_mcp_parity.py` — 4/4 matches
- [ ] Composite module dependency rule следуется (нет cross-composite imports)

## Красные линии
- [ ] Не вызывать composite из atomic handlers (anti-pattern).
- [ ] Не дублировать env переменные / API setup в каждом composite — общая логика в navigator/.
- [ ] Не делать composite слой в navigator/ library. Composite — это presentation concern (CLI слой), не library concern.

## Проверка
1. `md orient --corpus /tmp/test-corpus --json | jq '.workflow'` → "md_orient"
2. `md edit-context --path /tmp/file.md --mode strict --json | jq '.blockers'` → есть
3. `md refactor-candidates --corpus /tmp/test-corpus --json | jq '.no_automation'` → true
4. `cd experiments/md-embedding-server && uv run pytest tests/test_composite_tools.py tests/test_composite_mcp_parity.py -v` → all green
5. `grep -r "from md_cli.composites" src/md_cli/composites/` — empty (no cross-composite imports)
