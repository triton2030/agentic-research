# Navigator public API refactor (prerequisite для composites)

## Цель
Refactor `navigator/` library чтобы expose **importable Python functions** для status/map/importance/search/etc. — не только argparse CLI handlers. Composites (task-202) и hybrid (task-203) вызывают эти functions in-process, не через subprocess.

Audit cycle-2 (Implementation G7) выделил это в отдельный task — hidden balloon в task-202 substep «navigator public API audit» мог скрыть 1-2 дня дополнительной работы. Лучше явно расколоть.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-101 закрыт (`src/navigator/` moved)

## Подшаги

- [ ] Audit current public surface `src/navigator/`:
  - `grep -rE "^def [a-z_]+" src/navigator/` — список всех top-level functions
  - Какие используются `cli.py` argparse handlers vs внутренними частями
  - Identify те что должны стать public для composites/hybrid

- [ ] Required public functions (минимум для composites + hybrid):
  - `navigator.status(corpus: str) -> dict`
  - `navigator.map(corpus: str, **kwargs) -> dict`
  - `navigator.importance(corpus: str, top: int = 10, mode: str = "pagerank") -> dict`
  - `navigator.read_related(path: str, **kwargs) -> dict`
  - `navigator.search(corpus: str, query: str, **kwargs) -> dict`
  - `navigator.overlaps(corpus: str, **kwargs) -> dict`
  - `navigator.refactor_candidates(corpus: str, **kwargs) -> dict`
  - `navigator.query_by_type(corpus: str, types: list, **kwargs) -> dict`
  - `graph.preflight(path: str, **kwargs) -> dict`
  - `graph.impact(path: str) -> dict`

- [ ] Pattern:
  - Если function уже exists и public — verify signature matches expected
  - Если internal — refactor: вытащить core logic в public function, argparse handler становится thin wrapper:
    ```python
    # navigator/search.py
    def search(corpus: str, query: str, *, limit: int = 8, ...) -> dict:
        """Public API for composites + hybrid."""
        ...  # core logic
    
    def cmd_search(args):
        """argparse CLI handler — wrapper over search()."""
        return search(args.corpus, args.query, limit=args.limit, ...)
    ```
  - Это keeps argparse как surface, но composites используют function directly

- [ ] Update `src/navigator/__init__.py`:
  ```python
  from .status import status
  from .search import search
  from .importance import importance
  # ... etc
  
  __all__ = ["status", "search", "importance", ...]
  ```

- [ ] Tests `tests/test_navigator_public_api.py`:
  - `from navigator import search` — importable
  - `search("/tmp/fixture", "test query")` — returns dict
  - Каждая из 10 required functions — importable + minimal smoke

- [ ] Update existing tests если они ссылались на private internals:
  - `tests/run-tests.sh` всё ещё зелёный

- [ ] Document в `experiments/md-embedding-server/docs/navigator-public-api.md`:
  - Список public functions с signatures
  - Architectural rule: composites/hybrid вызывают public API, не argparse subprocess
  - Internal functions не gainto leak

## Готово
- [ ] `src/navigator/__init__.py` экспортирует все required public functions
- [ ] `tests/test_navigator_public_api.py` — 10 imports + 10 smoke calls зелёные
- [ ] `docs/navigator-public-api.md` существует с docs
- [ ] Existing `tests/run-tests.sh` зелёный (нет regression)

## Красные линии
- [ ] Не менять external behavior CLI handlers (только internal refactor)
- [ ] Не делать functions «too public» — только те 10 что нужны composites/hybrid
- [ ] Не делать subprocess wrappers в navigator/ (composites вызывают functions directly)

## Проверка
1. `python3 -c "from navigator import status, search, importance, read_related; print('ok')"` → "ok"
2. `cd experiments/md-embedding-server && uv run pytest tests/test_navigator_public_api.py -v` → 20+ green
3. `bash scripts/run-tests.sh` → зелёный
