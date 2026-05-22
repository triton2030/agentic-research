# Changelog

## 2.0.0 — Simpler agent-facing CLI

Breaking changes from the agent DX cleanup pass. The CLI now keeps safety/data
primitives in Python and moves usage wisdom back to skills.

### Breaking

- Mutating dry-run handles moved from payload root to `_envelope.lock`.
  Read `_envelope.lock.transaction_id`, `_envelope.lock.expires_at`, and
  `_envelope.lock.fingerprint`.
- `_envelope.next_step[]` no longer carries shell command strings. It stays
  structured as `{tool, args, reason}`; skills assemble commands when needed.
- `--brief` was removed. Use `--json` and skill-side interpretation.
- `md extract --map-stdin` now reads map-shaped data only (`md ls` / `md toc`).
  It no longer adapts `md search` output.
- Persistent `.consumed` transaction sentinels were removed. A consumed or
  missing id returns `transaction_not_found`; rerun `--dry-run` for a fresh id.

### Added

- `md search-read CORPUS --query "..." --limit N --json` combines semantic
  ranking with section bodies. This is the default "find and read" path for
  agents.
- Transaction error payloads include `hint` strings.

### Internals

- `ToolResult` has `lock: dict | None = None`.
- Confirm uses a short-lived `.claim` file during verification and deletes it
  after the live mutation attempt.
- `STATUS_SCHEMA` now matches the live `md status --json` shape (`state` and
  `scopes[]`).
