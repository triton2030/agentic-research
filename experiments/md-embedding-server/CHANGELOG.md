# Changelog

## 3.0.0 — Agent-view output projection

Bounded-by-default outputs with guaranteed progressive disclosure. On a
2000-file corpus this took `md orient` 502KB→7KB, `md ls` 884KB→22KB,
`md status` 30KB→2KB. Verified by consumer-simulation + adversarial agents:
no information is unreachable.

### Breaking

- `SCHEMA_VERSION` → `4.0.0`. `search` rows drop `body`, `content_hash`,
  `rowid`, and raw `bm25_score`/`dense_distance` (use `rrf_score`; raw scores
  only as `score_sources` under `--expanded`). `search-read` drops `map_only`/
  `content_included`; `status` no longer requires `scopes` (headline default).
- `map_only` / `content_included` flags retired across tools → one `view`
  field (`"map"` | `"expanded"`). Per-item `read_next` collapsed to a single
  payload-level channel.

### Added

- `md_cli.envelope.project_payload`: central agent-view projection (internal-
  field denylist, path relativization, flag collapse) applied in `wrap()`.
- `md orient` default: `start_here` (ranked entry files + why) + `owner_docs`
  (root/top-folder AGENTS/README) + folded `shape`; full list via `--expanded`.
- `md ls` default: folded `summary` + bounded top-N (full headings via
  `--expanded` / `md toc`). `md status`, `md ls`, `md cluster` gained
  `--expanded`. `md search` payload gained a compact `render` string.
- `navigator.pick` re-derives per-file headings on demand, so `md extract`
  works on any map (lean or full).

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
