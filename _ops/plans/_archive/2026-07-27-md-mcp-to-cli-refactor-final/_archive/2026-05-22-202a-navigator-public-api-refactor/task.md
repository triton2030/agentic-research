# Navigator public API: full 24 atomic + 5 workflows

## Цель
Превратить `src/navigator/` в **настоящую importable library** с полным public API. Каждое из 29 capabilities (24 atomic + 5 workflows) — importable Python function с typed args и dict return. Handlers (task-201/202/203) и workflows импортируют эти functions; никаких subprocess вызовов старого CLI или stdout parsing.

Это **prerequisite для всего Phase 2**. Без full public API получится не настоящая library, а Python-обёртка вокруг argparse cmd_* handlers — что превращает refactor в косметический.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-101 закрыт (`src/navigator/` moved, layout зафиксирован)
- task-104 закрыт (contract map определяет точные signatures)

## 4-layer position

Layer 1 (atomic) + Layer 2 (workflows). Обе importable. Handlers (Layer 3) импортируют отсюда.

## Status — 2026-05-22

completed-for-codex-cli-implementation. `src/navigator/api.py` exposes the 24
atomic functions, `src/navigator/workflows/` exposes 5 workflows, compatibility
scripts still run, and `docs/navigator-public-api.md` exists. Fresh-eyes P1s
around warm-index kwargs and transaction-scope bypass were accepted and fixed.
Envelope corpus-state now uses the public API path instead of stdout capture.
Verification: `uv run pytest tests/ -q` → 174 passed; `bash scripts/run-tests.sh
-q` → 174 passed.

## Подшаги

- [ ] **Phase A — Atomic library functions (24 шт)**. Каждая в отдельном модуле (или одном по теме), с typed signature, dict return:

  **Navigator atomic (16)**:
  - `navigator.ping() -> dict` — простой health check
  - `navigator.status(corpus: str) -> dict`
  - `navigator.ls(path: str, *, max_depth: int = None) -> dict`
  - `navigator.toc(path: str, *, max_heading_level: int = None) -> dict`
  - `navigator.read_related(path: str, *, scan: str = None, mode: str = "preview", token_budget: int = 1200, anchor_aware: bool = True, semantic_radius: bool = False, check_links: bool = False) -> dict`
  - `navigator.importance(corpus: str, *, top: int = 10, mode: str = "pagerank") -> dict`
  - `navigator.extract(corpus: str, *, headings: list = None, paths: list = None, map_data: dict = None) -> dict`
  - `navigator.search(corpus: str, query: str, *, limit: int = 8, scope: str = None, rerank: bool = False, path_include: list = None, path_exclude: list = None) -> dict`
  - `navigator.overlaps(corpus: str, *, threshold: float = 0.85, top: int = 10, path_include: list = None) -> dict`
  - `navigator.repeated_concepts(corpus: str, *, path_include: list = None) -> dict`
  - `navigator.audit(corpus: str) -> dict`
  - `navigator.index(corpus: str, *, dry_run: bool = False, transaction_id: str = None, fingerprint: str = None) -> dict`
  - `navigator.init(path: str, *, dry_run: bool = False, transaction_id: str = None) -> dict`  
    Note: `md_init` лексически граф-операция, но MCP regisrered под navigator-tools — оставить как есть в semantic group.
  - `navigator.strip(path: str, *, also_related_section: bool = False, dry_run: bool = False, transaction_id: str = None) -> dict`
  - `navigator.profile_sections(corpus: str, *, mode: str = "heuristic", dry_run: bool = False, transaction_id: str = None) -> dict`
  - `navigator.corpus_scan(root: str) -> dict`

  **Graph atomic (8)**:
  - `navigator.preflight(path: str, *, scan: str = None, depth: int = 2, path_include: list = None) -> dict`
  - `navigator.impact(path: str) -> dict`
  - `navigator.deps(path: str, *, depth: int = 2) -> dict`
  - `navigator.check(scan: str) -> dict`
  - `navigator.scan(paths: list) -> dict`
  - `navigator.health(scan: str = None) -> dict`
  - `navigator.cycles(scan: str = None) -> dict`
  - `navigator.changed(*, base: str = None, staged: bool = False) -> dict`

- [ ] **Phase B — Workflow functions (5 шт)** в `src/navigator/workflows/`:

  - `navigator.workflows.orient(corpus: str, *, top: int = 10, max_heading_level: int = 2, compact: bool = False) -> dict`
    Composition: status + map + importance. Compact mode: top=3, level=1, slim status.
  
  - `navigator.workflows.edit_context(path: str, *, mode: str = "full", scan: str = None, depth: int = 2, query: str = None, corpus: str = None) -> dict`
    Composition: preflight + read_related (+ optional search if mode=full + query).
  
  - `navigator.workflows.refactor_candidates(corpus: str, *, top: int = 10, uniqueness_threshold: float = 0.35, owner_confidence_threshold: float = 0.45, path_include: list = None, path_exclude: list = None, compact: bool = False) -> dict`
    Single navigator.refactor_candidates() call (если уже atomic) или composition если требует profile_sections priming.
  
  - `navigator.workflows.query_by_type(corpus: str, types: list, *, filter: str = None, limit: int = 50, path_include: list = None, path_exclude: list = None, compact: bool = False) -> dict`
    Single navigator.query_by_type() call или composition с profile_sections priming.
  
  - `navigator.workflows.section_blast_radius(path: str, corpus: str, query: str, *, heading_id: str = None, scan: str = None, depth: int = 2, limit: int = 8, path_include: list = None, path_exclude: list = None) -> dict`
    Hybrid: parallel preflight + search via `concurrent.futures`.

- [ ] **Refactor existing `cmd_*` handlers в `scripts/md_navigator.py` / `scripts/md_graph.py`**:
  - Каждый existing `cmd_<name>(args)` функция становится thin wrapper:
    ```python
    def cmd_search(args):
        result = navigator.search(args.corpus, args.query, limit=args.limit, ...)
        if args.json:
            print(json.dumps(result))
        return 0
    ```
  - Это keeps backward compat scripts/md_navigator.py живым во время Phase 1/2

- [ ] **Update `src/navigator/__init__.py`**:
  ```python
  # 24 atomic
  from .status import status
  from .search import search
  # ... 22 more
  
  # workflows as namespace
  from . import workflows
  
  __all__ = [
      "status", "search", "ls", "toc", "read_related", "importance", "extract",
      "overlaps", "repeated_concepts", "audit", "index", "init", "strip",
      "profile_sections", "corpus_scan", "ping",
      "preflight", "impact", "deps", "check", "scan", "health", "cycles", "changed",
      "workflows",
  ]
  ```

- [ ] **Update `src/navigator/workflows/__init__.py`**:
  ```python
  from .orient import orient
  from .edit_context import edit_context
  from .refactor_candidates import refactor_candidates
  from .query_by_type import query_by_type
  from .section_blast_radius import section_blast_radius
  
  __all__ = ["orient", "edit_context", "refactor_candidates", 
             "query_by_type", "section_blast_radius"]
  ```

- [ ] **Tests `tests/test_navigator_public_api.py`**:
  - `from navigator import status, search, importance, ...` — все 24 importable
  - `from navigator.workflows import orient, edit_context, ...` — все 5 importable
  - `navigator.status("/tmp/fixture")` — returns dict
  - Каждая function — minimal smoke на fixture corpus

- [ ] **Architectural invariant test** `tests/test_architecture_invariants.py`:
  - `grep -r "subprocess" src/navigator/` → 0 (kроме allowed: HTTP, embedding API calls которые не Python CLI)
  - `grep -r "from md_cli" src/navigator/workflows/` → 0 (workflows не depend on CLI)
  - `grep -r "json.dumps\|json.dump(" src/navigator/` → 0 (library returns dict, не serializes)
  - `grep -r "print(" src/navigator/` → 0 (за исключением legitimate debug в `__main__` блоках)

- [ ] **Documentation** `experiments/md-embedding-server/docs/navigator-public-api.md`:
  - Полный список 29 functions с signatures
  - Architectural rule: handlers + workflows + tests импортируют отсюда; никакой stdout parsing
  - Internal/private helpers — `_underscore_prefix`, не leaked

## Готово
- [ ] `src/navigator/__init__.py` экспортирует 24 atomic functions + `workflows` namespace
- [ ] `src/navigator/workflows/__init__.py` экспортирует 5 workflows
- [ ] `tests/test_navigator_public_api.py` — 29 imports + 29 minimal smoke calls зелёные
- [ ] `tests/test_architecture_invariants.py` — все 4 checks зелёные
- [ ] `docs/navigator-public-api.md` существует
- [ ] Existing `bash scripts/run-tests.sh` зелёный (regression check)
- [ ] Existing `scripts/md_navigator.py` / `md_graph.py` всё ещё работают (thin wrappers)

## Красные линии
- [ ] Не оставлять `cmd_*` функции с реальной логикой — они должны стать ≤5 LOC wrappers
- [ ] Не leaking private internals в `__all__`
- [ ] Не importing `md_cli` из `navigator/` (one-way dependency direction)
- [ ] Не делать workflows зависимыми друг от друга (только от atomic)
- [ ] Не subprocess-ить старый CLI internally — composites/workflows вызывают functions directly

## Проверка
1. `python3 -c "from navigator import status, search, ping; from navigator.workflows import orient; print('ok')"` → "ok"
2. `cd experiments/md-embedding-server && uv run pytest tests/test_navigator_public_api.py -v` → 29+ зелёных
3. `cd experiments/md-embedding-server && uv run pytest tests/test_architecture_invariants.py -v` → 4 зелёных
4. `bash scripts/run-tests.sh` → зелёный
5. `experiments/md-embedding-server/scripts/md_navigator.py status .` → работает (backward compat)
