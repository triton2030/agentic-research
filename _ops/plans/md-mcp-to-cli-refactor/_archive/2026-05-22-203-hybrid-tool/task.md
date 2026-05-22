# Hybrid tool: md_section_blast_radius — handler

## Цель
Реализовать **thin CLI handler** для `md_section_blast_radius`. Workflow function уже implemented в `src/navigator/workflows/section_blast_radius.py` из task-202a (Layer 2). Здесь — handler (Layer 3) который вызывает workflow и returns ToolResult.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-201 закрыт (preflight + search handlers готовы)
- task-202 закрыт (composite patterns установлены)
- task-102 закрыт (envelope)

## Status — 2026-05-22

completed. `md_section_blast_radius` is a workflow in
`src/navigator/workflows/section_blast_radius.py`, the handler is thin, and
parallel graph+semantic execution is covered. Verification:
`tests/test_hybrid_section_blast.py` and `tests/test_hybrid_mcp_parity.py`
passed; full suite 169 passed.

## Подшаги

## Architectural position

`navigator.workflows.section_blast_radius` (Layer 2) — implemented in task-202a. Handler `md_cli/handlers/md_section_blast_radius.py` (Layer 3) — thin wrapper. Никаких `md_cli/hybrid/` модулей не создаётся.

## Зависимости
- task-202a закрыт (`navigator.workflows.section_blast_radius` готов)
- task-101 закрыт (runner)
- task-106 закрыт (architecture lock)

## Подшаги

- [ ] **Verify** workflow готов в task-202a:
  - `from navigator.workflows import section_blast_radius` — importable
  - Workflow function реально parallelizes preflight + search через `concurrent.futures.ThreadPoolExecutor`
  - Returns dict: `{path, heading_id, query, graph, semantic, usage_note}`
  - Если что-то отсутствует — task-202a не закрыт

- [ ] Handler `src/md_cli/handlers/md_section_blast_radius.py` (ToolResult pattern):
  ```python
  from md_cli.result import ToolResult
  from navigator.workflows import section_blast_radius
  
  def run(args) -> ToolResult:
      if not args.query or not args.query.strip():
          return ToolResult(payload={"error": "query_required"}, exit_code=2)
      payload = section_blast_radius(
          path=args.path, corpus=args.corpus, query=args.query, ...
      )
      return ToolResult(payload=payload, exit_code=0)
  ```
  Никакого envelope import, никакого JSON print.

- [ ] Tests `tests/test_hybrid_section_blast.py`:
  - test: оба слоя выполнены — graph и semantic поля присутствуют
  - test: без query — exit 2 (argparse required violation)
  - test: с cold corpus — semantic возвращает `index_warmup_required`; graph всё ещё выполняется
  - test: parallel execution — total time ≤ slowest single call × 1.3 (sanity для real parallelism)

- [ ] Parity test `tests/test_hybrid_mcp_parity.py`:
  - CLI vs MCP same args → same graph + semantic shape

- [ ] **Documentation**: добавить в catalog `description.input.heading_id` — clarification что heading_id используется только для annotation, soft layer queries corpus-wide. Это nuanced поведение которое skill должен знать (раunhinged в SKILL.md 1md-graph).

## Готово
- [ ] `src/navigator/workflows/section_blast_radius.py` существует (из task-202a)
- [ ] `src/md_cli/handlers/md_section_blast_radius.py` существует
- [ ] `src/md_cli/hybrid/` не существует
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
