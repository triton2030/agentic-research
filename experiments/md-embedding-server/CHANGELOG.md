# Changelog

## 2.0.0 — Schema cut for "natural for agents" DX

Breaking changes drawn from two real-agent DX sessions (Claude Opus 4.7,
GPT-5.5 via Codex). One envelope-revision pass; no dual-write.

### Breaking

- **`transaction_id` / `expires_at` / `fingerprint` moved to `_envelope.lock`.**
  Mutating dry-run payloads no longer carry these fields in the payload root.
  Read `_envelope.lock.transaction_id` (and `_envelope.lock.fingerprint` /
  `_envelope.lock.expires_at`) instead.
- **`reason: "unknown"` from `verify_and_consume_transaction` split into
  `reason: "transaction_not_found"` and `reason: "transaction_consumed"`.**
  A second `--confirm` of the same id now returns `transaction_consumed`
  so agents can distinguish "race lost / already applied" from "bad id".
- **`md extract` no longer requires `--map-data`.** Either `--map-data` or
  `--map-stdin` must be supplied (`oneOf`). Schemas that hard-required
  `map_data` need to switch to `oneOf`.

### Added

- **`md extract --map-stdin`** reads the map from stdin so pipes like
  `md search ... --json | md extract --map-stdin --headings 1,2,3` work
  without manual JSON quoting. Search payloads are auto-adapted to the
  map shape (results → files+headings).
- **`_envelope.next_step[].command`** — every routable next step now
  carries a copy-pasteable shell command. Main use cases:
  - dry-run → confirm: payload of `md <tool> --dry-run` now includes
    `_envelope.next_step[0].command = "md <tool> ... --confirm
    --transaction-id <id> --json"`.
  - search → extract: top-N pipe is pre-built.
- **`--brief` global flag** prints compact human-readable rows for
  `md_search`, `md_overlaps`, `md_repeated_concepts`, `md_extract`,
  `md_refactor_candidates`. Other tools fall back to JSON. Works in
  both `md --brief <cmd>` and `md <cmd> --brief` positions.
- **`hint`** field added to transaction error payloads with actionable
  next steps (e.g. `"Run --dry-run to obtain a fresh id"`).
- **Sentinel `.consumed`** files persist after successful mutation
  (cleaned by `gc_expired` after `2 * TXN_TTL_SECONDS` grace) so race
  losers see `transaction_consumed`, not `transaction_not_found`.

### Internals

- `ToolResult` dataclass gained `lock: dict | None = None`.
- `envelope.derive_next_step` now takes a `lock` kwarg.
- Atomic sentinel via `claimed.rename(sentinel)` (single POSIX syscall)
  replaces `touch() + unlink()` — no TOCTOU window between two syscalls.
- `_missing_path_reason` polls briefly for sibling `.claim` files so the
  race-lost branch returns `transaction_consumed` instead of
  `transaction_not_found` when winner has not yet finalised the rename.
