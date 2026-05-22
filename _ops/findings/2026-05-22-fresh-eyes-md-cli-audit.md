# Fresh-eyes md CLI audit — 2026-05-22

## Result

partial-pass-after-repair

## Accepted And Fixed

- P1 API warm-index kwargs leak: `navigator.api.search`, `overlaps`,
  `repeated_concepts`, and `audit` now pass only index-context kwargs into
  `_sections_index_context`. Added warm-index regression coverage.
- P1 transaction scope bypass: transactions now store canonical cwd, full
  non-control intent, and affected file set; confirm re-runs dry-run and rejects
  changed scope before live mutation. Added direct and CLI regression coverage.
- P1 Codex skill hot-path drift: old plain `md_*` references and invalid
  `md map` / `md headings` / `md read` style commands were removed from Codex
  skill surfaces. `sync-skill-docs.py --check` now catches that class.
- P2 generated catalog drift: `tool-catalog.md` now leads with real `md`
  commands and is regenerated from the CLI catalog.
- P2 `1md-navigator/agents/openai.yaml`: no longer instructs agents to index
  before every first project use; cold start now begins with `md orient`, and
  indexing is gated by warmup/delta evidence.
- P2 envelope corpus-state gap: CLI runner now fills `_envelope.corpus_state`
  through `navigator.api.status`, and `md_cli.corpus_state` no longer captures
  stdout from legacy `cmd_status`.
- Runtime self-repair drift: graph/status/search outputs that guide agents now
  emit `md ...` commands for related reading and index warmup instead of
  `md_navigator.py ...`.

## Accepted And Later Resolved

- Claude-side skill migration was initially blocked for Codex, but current
  `AGENTS.md` now allows Claude skill edits by explicit user request through
  `1skill-architect`. Migration evidence:
  `_ops/findings/2026-05-22-claude-skills-cli-migration.md`.

## Still Open

- Task closeout bookkeeping is weaker than implementation evidence: code/tests
  pass, but some task checkboxes still reflect historical plan text. Treat as
  planning cleanup, not implementation blocker.

## Deferred

- `navigator.__init__` still uses callable proxies so `navigator.search(...)`
  remains convenient while legacy `import navigator.search` keeps working. This
  is a P2 ergonomics/inspection smell, not a safe-removal blocker after tests.
  Cleaner future path: expose functions only from `navigator.api` or non-module
  aliases after downstream import habits are migrated.

## Runtime Mismatch

Updated `1fresh-eyes` asks for named critics:
`business-critic`, `developer-critic`, `architecture-critic`,
`trajectory-critic`. Current `spawn_agent` does not expose these names:
`developer-critic`, `business-critic`, `architecture-critic`, and
`trajectory-critic` return `unknown agent_type`; `brooks` and `smith` are
listed but return `currently not available`. Generic explorers/auditor were
used only before this mismatch was confirmed, and their findings were verified
locally.

## Checks After Repair

- `python3 scripts/sync-skill-docs.py --check` → pass.
- `md --version` → `md-tools 0.7.0`.
- `md tools --json` → 29 tools.
- `uv run pytest tests/ -q` → 174 passed.
- `bash scripts/run-tests.sh -q` → 174 passed.
