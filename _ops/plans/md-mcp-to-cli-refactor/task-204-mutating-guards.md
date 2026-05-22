# Mutating tools: md_init, md_strip, md_index, md_profile_sections с dry-run/confirm

## Цель
**4 mutating handlers** (после architectural review: md_profile_sections тоже cost-bearing — LLM profiling stoит реальных $) — те что меняют файлы или дорого расходуют API. Каждый защищён dry-run/confirm/fingerprint protocol с **intent-binding verify** (не только content fingerprint, но и совпадение tool name + args).

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)

## Зависимости
- task-103 закрыт (transactions module)
- task-102 закрыт (envelope)
- task-201 закрыт (basic handler patterns established)

## Codex sandbox-mode considerations (audit Codex #6)

Codex использует `sandbox_mode = "workspace-write"`. Mutating tools пишут в `<corpus>/.md-navigator/` и саму directory tree corpus'а (md_init добавляет frontmatter, md_strip убирает).

**Risk**: если corpus вне Codex workspace — `sandbox_mode="workspace-write"` блокирует write, mutating fails silently или с PermissionError.

**Mitigation в handlers**:
- При write failure — return envelope error с явным сообщением «corpus outside writable scope; in Codex проверьте workspace boundary или поднимите sandbox»
- НЕ swallow PermissionError — пусть всплывает наверх как clear error
- Document в task-302/305 что Codex skills используют mutating tools только на corpus внутри workspace

## Подшаги

- [ ] Реализовать `src/md_cli/handlers/md_init.py`:
  - Wraps `navigator.graph.init()` (or scripts/md_graph.py init equivalent)
  - Decorator `@requires_transaction`
  - dry-run: scan target paths, compute affected files (те что без frontmatter получат template), return preview + transaction_id
  - confirm: verify fingerprint, apply template, consume txn
  - destructiveHint: true (annotation)

- [ ] Реализовать `src/md_cli/handlers/md_strip.py`:
  - Wraps `navigator.graph.strip()` (legacy fields cleanup + optional related-docs section removal)
  - Decorator `@requires_transaction`
  - dry-run: identify legacy fields, sections to remove, return diff preview
  - confirm: apply strip, consume txn
  - Bool flag `--also-related-section` (presence-based)
  - destructiveHint: true

- [ ] Реализовать `src/md_cli/handlers/md_index.py`:
  - Wraps `navigator.index()` — embedding warmup
  - Decorator `@requires_transaction`
  - dry-run: count pending chunks, estimate cost ($X based on chunk count + model), return preview
  - confirm: actually embed, persist to disk
  - idempotentHint: false (different runs = different embedded state if corpus changes)
  - openWorldHint: true (HTTP к OpenRouter)
  - Особый exit code 4 для `index_warmup_required` (используется другими tools для self-repair via envelope.next_step)

- [ ] Реализовать `src/md_cli/handlers/md_profile_sections.py` (audit cycle-2 architectural review):
  - Wraps `navigator.profile_sections()` — LLM-classifier для секций
  - Decorator `@requires_transaction`
  - **Cost-bearing**: `mode: "llm"` использует OpenRouter LLM ~$0.0005 per section. На corpus 200+ секций — реальные $$.
  - dry-run: count unprofiled sections, estimate cost, return preview
  - confirm: actually classify, persist to index.sqlite
  - mode=heuristic — free, можно skip dry-run/confirm gate
  - mode=llm — must use dry-run/confirm

- [ ] Envelope integration (audit architectural review — strict intent verify):
  - error response `confirm_required` → envelope.next_step генерирует **только dry-run directive** (НЕ runnable confirm без transaction_id). Confirm directive активируется только после dry-run возвращает transaction_id.
  - error response `index_warmup_required` (specifically for md_index ситуация) → envelope.next_step генерирует **dry-run + retry original** (без runnable confirm). Confirm составляется skill после видения dry-run результата.
  - error response `drift_detected` → не next_step (это user error), просто error в payload
  - **Confirm always re-verifies**: даже после fingerprint match, confirm перепроверяет (re-compute fingerprint снова из live files) + intent args match (tool name, path/corpus args identical к dry-run-ed). Двойная защита.

- [ ] Tests `tests/test_mutating_handlers.py`:
  - test md_init без флагов → exit 1 with `confirm_required` + envelope.next_step has 2 directives
  - test md_init --dry-run → transaction_id present, no file changes
  - test md_init --confirm --transaction-id <id> → file changes applied, txn consumed
  - test md_init --confirm --transaction-id <stale_id> → `drift_detected`
  - test md_strip same 4 scenarios
  - test md_index same scenarios
  - test md_index --dry-run shows estimated_cost field
  - Use tmp corpus copies for isolation

- [ ] Parity test `tests/test_mutating_mcp_parity.py`:
  - MCP md_init/strip/index dry-run vs CLI dry-run → same affected_files, same preview shape
  - Confirm flow → same final state in test corpus

## Готово
- [ ] `src/md_cli/handlers/md_init.py` — реализован, `@requires_transaction`, ToolResult
- [ ] `src/md_cli/handlers/md_strip.py` — реализован
- [ ] `src/md_cli/handlers/md_index.py` — реализован, special exit 4 на cold corpus refusal
- [ ] `src/md_cli/handlers/md_profile_sections.py` — реализован (mode=llm требует dry-run/confirm; mode=heuristic free path)
- [ ] `tests/test_mutating_handlers.py` — 16+ test cases (4 per tool × 4 tools) зелёные
- [ ] `tests/test_mutating_mcp_parity.py` (snapshot-based) — 4 tools match зелёные
- [ ] Без `--confirm` все 4 tools безопасны (no file changes, no HTTP cost)
- [ ] Confirm всегда re-verifies fingerprint + intent args (двойная защита)

## Красные линии
- [ ] Не пропускать transaction verify даже если args обещают «я уверен». Skill agent может ошибиться.
- [ ] Не accept `--confirm` без `--transaction-id` или `--fingerprint`. Один из двух обязателен.
- [ ] Не обходить TTL транзакций (5 минут) — пользователь должен явно перевызвать dry-run.
- [ ] Не embed без confirm — md_index без confirm = no HTTP costs.

## Проверка
1. `md init --path /tmp/test --json` (без флагов) → exit 1, `_envelope.next_step[].tool == "md_init"`, dry-run и confirm directives
2. `md init --path /tmp/test --dry-run --json | jq '.transaction_id'` → exists
3. `md index --corpus /tmp/empty --json` → exit 4, error `index_warmup_required`, envelope.next_step с 3 directives
4. `cd experiments/md-embedding-server && uv run pytest tests/test_mutating_handlers.py tests/test_mutating_mcp_parity.py -v` → all green
5. Manual: dry-run, изменить файл, confirm → `drift_detected`
