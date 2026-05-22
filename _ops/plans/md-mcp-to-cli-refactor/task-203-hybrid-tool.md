# Hybrid tool: md_section_blast_radius

## Цель
Реализовать единственный hybrid tool — `md_section_blast_radius`. Hybrid = graph слой (hard, contracts) + semantic слой (soft, candidates) в параллельном вызове через `concurrent.futures` или asyncio. Это где совмещаются два домена в одном tool.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-201 закрыт (preflight + search handlers готовы)
- task-202 закрыт (composite patterns установлены)
- task-102 закрыт (envelope)

## Подшаги

- [ ] Создать `src/md_cli/hybrid/__init__.py` пустой.

- [ ] Реализовать `src/md_cli/hybrid/section_blast_radius.py`:
  - Inputs: path, corpus, query, heading_id (optional), scan, depth, limit, path_include, path_exclude
  - Two parallel calls:
    1. `graph.preflight(path, scan, depth, path_filters)` — hard layer
    2. `navigator.search(corpus, query, limit, path_filters)` — soft layer
  - Run via `concurrent.futures.ThreadPoolExecutor` (Python GIL не блокер для I/O-bound: subprocess + HTTP)
  - Return dict: `{path, heading_id, query, graph, semantic, usage_note}`

- [ ] Handler `src/md_cli/handlers/md_section_blast_radius.py`:
  - Standard wrap pattern
  - Validate query non-empty (это REQUIRED для smart soft layer)
  - Pass через envelope.wrap()

- [ ] Tests `tests/test_hybrid_section_blast.py`:
  - test: оба слоя выполнены — graph и semantic поля присутствуют
  - test: без query — exit 2 (argparse required violation)
  - test: с cold corpus — semantic возвращает `index_warmup_required`; graph всё ещё выполняется
  - test: parallel execution — total time ≤ slowest single call × 1.3 (sanity для real parallelism)

- [ ] Parity test `tests/test_hybrid_mcp_parity.py`:
  - CLI vs MCP same args → same graph + semantic shape

- [ ] **Documentation**: добавить в catalog `description.input.heading_id` — clarification что heading_id используется только для annotation, soft layer queries corpus-wide. Это nuanced поведение которое skill должен знать (раunhinged в SKILL.md 1md-graph).

## Готово
- [ ] `src/md_cli/hybrid/section_blast_radius.py` существует
- [ ] `src/md_cli/handlers/md_section_blast_radius.py` существует
- [ ] `tests/test_hybrid_section_blast.py` — 4 tests зелёные
- [ ] `tests/test_hybrid_mcp_parity.py` — 1 match зелёный
- [ ] Parallel execution timing verified

## Красные линии
- [ ] Не использовать asyncio если subprocess не async-aware. ThreadPoolExecutor подходит лучше для синхронных library calls.
- [ ] Не deduplicate с composite — hybrid это другая концепция (parallel + heterogeneous slices, composite — sequential + homogeneous slices).
- [ ] Не запускать оба слоя последовательно — теряем speedup.

## Проверка
1. `md section-blast-radius --path /tmp/file.md --corpus /tmp --query "owner rule" --json | jq 'keys'` → contains graph, semantic
2. `md section-blast-radius --path /tmp/file.md --corpus /tmp --json` (без query) → exit 2
3. `cd experiments/md-embedding-server && uv run pytest tests/test_hybrid_section_blast.py tests/test_hybrid_mcp_parity.py -v` → all green
4. Time `md section-blast-radius ...` vs `md preflight ...` + `md search ...` separately — hybrid ≤ slowest single × 1.3
