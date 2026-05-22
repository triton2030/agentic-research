# Transactions module: stateless fingerprint + intent-binding cache

## Цель
`src/md_cli/transactions.py` — stateless safety для mutating operations (md_init, md_strip, md_index). Не in-memory store как сейчас в MCP (так как CLI invocations не shared memory). Используется hybrid: content fingerprint + optional intent-binding через file cache.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-101 закрыт (есть `md_cli/`)

## Подшаги

- [ ] Дизайн protocol:
  - **Phase 1 — dry-run**: handler выполняет полный preview (computes affected files), возвращает `{transaction_id, fingerprint, affected_files, preview, expires_at}`. Side-effect: запись `~/.cache/md-tools/transactions/{transaction_id}.json` с intent + fingerprint.
  - **Phase 2 — confirm**: вызывает с `--confirm --transaction-id <id>` или `--confirm --fingerprint <hash>` (один из двух обязателен).
  - Verify: re-compute fingerprint over affected_files; compare to stored или provided.
  - If match → execute mutation, удалить cache file, вернуть результат.
  - If mismatch → return `{error: "drift_detected", original_fingerprint, current_fingerprint, ...}` через envelope's `next_step`.

- [ ] Реализовать `src/md_cli/transactions.py`:
  - `compute_fingerprint(file_paths: list[str]) -> tuple[str, list[FileEntry]]` — SHA256 over sorted `path:sha16` pairs
  - `create_transaction(tool, args, fingerprint, files) -> dict` — генерирует ID `txn_<8 random hex>`, пишет cache file с TTL 5 минут
  - `verify_transaction(transaction_id, expected_tool) -> dict` — читает cache, re-computes fingerprint, возвращает `{ok, txn|reason}`
  - `consume_transaction(transaction_id)` — удаляет cache file
  - `gc_expired()` — runs **только при create_transaction**, не при verify (audit Implementation #4 — TTL race fix). Это устраняет окно: proc A читает txn для verify ↔ proc B запускает GC и удаляет тот же txn если created_at около cutoff. GC на verify был бы false drift_detected.
  - File removal в `consume_transaction` использует `os.rename` to temp file then unlink (atomic) — tolerates ENOENT в verify if another process already cleaned up

- [ ] Cache file shape `~/.cache/md-tools/transactions/{txn_id}.json`:
  ```json
  {
    "id": "txn_abc123",
    "tool": "md_strip",
    "args": {"path": "..."},
    "fingerprint": "sha256_32hex",
    "files": [{"path": "...", "hash": "sha256_16hex"}],
    "created_at": "ISO8601",
    "expires_at": "ISO8601"
  }
  ```

- [ ] Intent-binding (S1 раunhinged): дополнительная защита поверх fingerprint.
  - При verify проверяется не только fingerprint, но что `expected_tool == txn.tool` и что `confirm args` совпадают с `txn.args` по ключевым полям (path, target etc.)
  - Это закрывает дырку «confirm от другой dry-run с тем же fingerprint целевого файла»

- [ ] Stateless fallback (без cache file):
  - Если user явно передаёт `--confirm --fingerprint <hash>` без transaction-id:
    - Handler сам re-computes fingerprint, compares to provided
    - Без intent check (agent сам отвечает за корректность сопоставления)
    - Это backup path если cache недоступен

- [ ] Создать `src/md_cli/decorators.py`:
  - `@requires_transaction` декоратор для handlers mutating tools
  - Если `args.dry_run` → handler runs preview, calls `create_transaction()`, returns dry-run result + transaction_id
  - Если `args.confirm` → handler calls `verify_transaction()` first, if ok → executes mutation + `consume_transaction()`
  - Если ни dry_run ни confirm → возвращает error `confirm_required` (envelope's next_step → dry-run directives)

- [ ] Tests `tests/test_transactions.py`:
  - test: dry-run возвращает txn_id, cache file создан
  - test: confirm с matching fingerprint → success
  - test: confirm с stale fingerprint (file changed) → `drift_detected`
  - test: confirm с wrong tool name → `tool_mismatch`
  - test: confirm с expired txn (>5 min) → `expired`
  - test: stateless `--fingerprint` без txn_id работает

## Готово
- [ ] `src/md_cli/transactions.py` существует, все API функции реализованы
- [ ] `src/md_cli/decorators.py` существует с `@requires_transaction`
- [ ] Cache directory `~/.cache/md-tools/transactions/` создаётся при первом вызове
- [ ] `tests/test_transactions.py` — все тесты зелёные, покрывают 6 сценариев

## Красные линии
- [ ] Не использовать in-memory state. Cache должен переживать процессы.
- [ ] Не игнорировать intent-binding — просто fingerprint = false confidence.
- [ ] Не растягивать TTL >5 минут.
- [ ] Не давать confirm без re-verify (TOCTOU защита).

## Проверка
1. `cd experiments/md-embedding-server && uv run pytest tests/test_transactions.py -v` → 6/6 green
2. Manual: создать tmpfile, `md strip --path tmpfile --dry-run --json` → есть transaction_id. Изменить tmpfile. `md strip --path tmpfile --confirm --transaction-id <id>` → `drift_detected`
3. `ls ~/.cache/md-tools/transactions/` — содержит активные txns, очищается после consume
