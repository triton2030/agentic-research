# Pre-removal smoke — 2026-05-22

## Verdict

GO

## Clean Install

Command set:

- `HOME=$TEMP_HOME uv tool install .../experiments/md-embedding-server --force`
- `md --version`
- `md ping --json`
- `md status . --json`
- `md tools --json`
- `md selftest --json`

Result:

- `md-tools 0.7.0`
- `md ping` → `_envelope` present
- `md status .` from `/tmp` → `NO_INDEX`, `_envelope` present
- `md tools --json` → 29 tools
- `md selftest --json` → `{pass: 28, fail: 0, skip: 1, total: 29}`

## Standard Preflight

- `uv run pytest tests/test_*_mcp_parity.py -q` → 3 passed.
- `uv run md selftest --json | jq '.summary'` → `{pass: 28, fail: 0, skip: 1, total: 29}`.
- `uv run md doctor` → no FAIL.
- `uv run md --version` → `md-tools 0.7.0`.

## Cross-Project CLI Smoke

agentic-research:

- Prompt equivalent: «о чём папка `knowledge/`?»
  First command: `md orient knowledge --compact --json`
  Result: `tool=md_orient`, 2 compact file items, `_envelope` present.
- Prompt equivalent: «расскажи статус corpus в `_ops/`»
  First command: `md status _ops --json`
  Result: `state=NO_INDEX`, `_envelope` present.
- Prompt equivalent: «есть ли open questions в `_ops/`?»
  First command: `md query-by-type _ops --types open-question --limit 5 --json`
  Result: `tool=md_query_by_type`, `_envelope` present.

civicchain:

- Prompt equivalent: «о чём этот repo?»
  First command: `md orient . --compact --json`
  Result: `tool=md_orient`, 2 compact file items, `_envelope` present.

## Mutating Smoke

Isolated tmp corpus:

- `md init --paths "$tmp/a.md" --dry-run --json` → returned `transaction_id`.
- `md init --paths "$tmp/a.md" --confirm --transaction-id <id> --json` →
  `changed=1`, `_envelope.tool=md_init`.

## Performance

- `md status _ops --json`: repeated runs after clean install measured
  `real 0.13`, `0.10`, `0.11` seconds.

## Limits

- Fresh Claude/Codex UI sessions were not directly observable from this
  Codex thread. The verifiable substitute here is clean install + installed
  CLI smoke + migrated skill docs + config removal + no active md-mcp node
  process. Final `1fresh-eyes`/subagent review remains required before closeout.
