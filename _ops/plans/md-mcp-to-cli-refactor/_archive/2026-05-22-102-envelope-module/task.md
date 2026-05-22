# Envelope module: single wrap point + golden test

## Цель
`src/md_cli/envelope.py` — единая точка обёртки любого CLI output в `_envelope`-shape, идентичную текущему MCP envelope. Все handlers выходят через wrap(); никакой handler envelope сам не собирает. Goldensnap test против реального MCP envelope гарантирует zero drift.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-000 закрыт (envelope-shape-snapshot.md = golden reference)
- task-101 закрыт (есть пакет `md_cli/`)

## Подшаги

- [x] Скопировать `envelope-shape-snapshot.md` (from task-000) → `experiments/md-embedding-server/tests/golden/envelope_shape.json` как golden artifact.

- [x] Реализовать `src/md_cli/envelope.py`:
  - `wrap(result, *, tool_name, args, corpus_state=None) -> dict` — main API
  - Fields в `_envelope`: `version` (1), `tool`, `corpus_root` (resolved), `corpus_state`, `lock` (None for now), `cost`, `size_estimate`, `next_step`
  - `compute_size_estimate(result)` — bytes + items_returned + counted_fields + large_reply if >10KB
  - `derive_next_step(result, tool_name, args, corpus_root)` — mirrors current envelope shape, but applies the stricter CLI transaction contract:
    - `index_warmup_required` → 2 directives: md_index dry-run + retry original after successful confirm (NO runnable confirm without transaction_id)
    - `confirm_required` → 1 directive: dry-run only (confirm is suggested only after dry-run returns transaction_id/fingerprint)
    - `empty: True` for md_search → broader scope directive
  - `resolve_corpus_root(args)` — args.corpus or args.scan → resolve()
  - Top-level merge if result is dict (preserve original keys + add `_envelope`)

- [x] Реализовать `src/md_cli/cost_ledger.py` (audit Implementation #3 + Codex #9):
  - File-based: `~/.cache/md-tools/cost-{session_id}.json`
  - **Session_id resolution chain** (cross-platform):
    1. `CLAUDE_CODE_SESSION_ID` env (Claude Code)
    2. `CODEX_SESSION_ID` env (Codex if exists)
    3. `MD_CLI_SESSION_ID` env (manual override)
    4. Generated uuid stored in `~/.cache/md-tools/session-id` (process group based)
  - **Atomic write** против race conditions при concurrent CLI invocations:
    - Append-only JSONL format: каждый `record_cost(usd)` пишет one line `{"ts": ..., "usd": ...}`
    - Read: aggregate all lines on demand
    - Append использует `O_APPEND` flag (POSIX atomic для single line)
    - `fcntl.flock` для multi-line writes (на macOS / Linux works)
  - `record_cost(usd)` — atomic append
  - `get_cost_snapshot()` → reads JSONL, aggregates → `{turn_usd, session_usd}`
  - Turn boundary detection: file mtime delta ≥30s OR explicit `--turn-boundary` flag
  - Tests: spawn 4 concurrent processes append costs, verify all 4 recorded
  - **Rotation** (audit cycle-2 Implementation G8): при `record_cost` если file >1MB OR mtime >24h — rename to `cost-{session_id}-{timestamp}.archive.jsonl` and start fresh. Opportunistic GC старых archive files (>30 дней) на `get_cost_snapshot()` call. Amortized cleanup без отдельного cron.
  - **CODEX_SESSION_ID verification** (audit cycle-2 Codex G6): в spike или test — `printenv | grep CODEX` в реальной Codex session. Если env var не existes — оставить в chain как defensive no-op, но в `_ops/findings/2026-MM-DD-codex-env-vars.md` зафиксировать, что effective fallback для Codex — generated uuid file. Это влияет на cost attribution accuracy.

- [x] Реализовать `src/md_cli/corpus_state.py`:
  - `quick_corpus_state(corpus_root) -> dict | None`
  - Caches in `~/.cache/md-tools/corpus-state-cache.json` с 30-second TTL (mimics JS behavior)
  - Underlying call: `navigator.status_cli_equivalent(corpus_root, json=True)`
  - Слим shape: state/model/index_exists/last_touched/added_sections/removed_sections/pending_chunks/drift_count/metadata_mismatch/delta_too_large/recommended_action
  - Silent fail → return None (envelope сохраняет corpus_state: None)

- [x] Создать `tests/test_envelope_golden.py`:
  - Загрузить `golden/envelope_shape.json`
  - Для каждого field в golden — assert structure (keys, types, optional nullable) в `wrap({}, tool_name="md_ping", args={})._envelope`
  - test: known error pattern → `next_step` соответствует CLI safety contract (`index_warmup_required` = dry-run + retry, `confirm_required` = dry-run only)
  - test: size_estimate.bytes большим object → `large_reply: True`
  - test: empty md_search result → broader scope directive

- [x] Создать `tests/test_envelope_drift.py`:
  - Запустить MCP `md_ping` через subprocess (живой server)
  - Запустить новый CLI `md ping --json` (без handlers ещё — но envelope module можно вызвать напрямую)
  - Сравнить shape `_envelope` field-by-field
  - Ошибка если есть drift

## Готово
- [x] `src/md_cli/envelope.py` существует, реализован полностью
- [x] `src/md_cli/cost_ledger.py` существует с file-based persistence
- [x] `src/md_cli/corpus_state.py` существует с 30s TTL cache
- [x] `tests/golden/envelope_shape.json` зафиксирован
- [x] `tests/test_envelope_golden.py` — все assertions проходят
- [x] `tests/test_envelope_drift.py` — проходит, или явно skipped с reason (если drift expected на этом этапе)

## Красные линии
- [ ] Не размазывать envelope build по handlers. ONLY через `envelope.wrap()`.
- [ ] Не добавлять новые поля в envelope сверх golden snapshot. Это refactor, не feature.
- [ ] Не использовать in-memory cost ledger в primary path — он должен переживать между invocations.

## Проверка
1. `cd experiments/md-embedding-server && uv run pytest tests/test_envelope_golden.py -v` → all green
2. `cd experiments/md-embedding-server && uv run pytest tests/test_envelope_drift.py -v` → green
3. `uv run python -c "from md_cli.envelope import wrap; import json; print(json.dumps(wrap({'ok':True}, tool_name='md_ping', args={}), indent=2))"` — выводит JSON с `_envelope` блоком
4. Manually verify: запуск 2 раза, второй раз `corpus_state` берётся из cache (>0 ms на disk read, <100ms total)

## Evidence

- `uv run pytest tests/test_corpus_state.py tests/test_envelope_golden.py tests/test_envelope_drift.py tests/test_cost_ledger.py -v` → 9 passed.
- `uv run pytest tests/ -v` → 119 passed.
- `uv run python -c "from md_cli.envelope import wrap; ..."` prints `_envelope` with the golden fields.
- `printenv | rg '^CODEX'` recorded in `_ops/findings/2026-05-22-codex-env-vars.md`; `CODEX_SESSION_ID` absent, fallback path documented.
- `index_warmup_required` and `confirm_required` tests assert no runnable confirm directive without `transaction_id`.
