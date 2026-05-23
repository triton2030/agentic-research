---
description: "Active task for proving md CLI tools work through agent-like scenario smoke checks."
read-before-edit:
  - "[[_ops/PROJECT-ROADMAP.md]]"
  - "[[_ops/project-graph.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[experiments/md-embedding-server/docs/cli-conventions.md]]"
  - "[[experiments/md-embedding-server/docs/architecture-lock.md]]"
edit-after-edit: []
---
# Task — `md` CLI scenario selftest

Статус: активно.

## Зачем

Broad goal остаётся шире, чем архитектурный refactor: агенту нужен быстрый
observable gate, что все `md` tools хотя бы запускаются как реальные CLI JSON
вызовы в сценариях, похожих на skill usage.

## Scope

Внутри:

- `md selftest --json` должен проверять не только imports/catalog, но и
  реальные CLI JSON вызовы по catalog tools.
- Быстрые tools проходят behavior smoke на `tests/fixtures/sample-corpus`.
- Slow/costly `md_audit` остаётся skip by default, но включается явно через
  `SMOKE_AUDIT=1` или `--tool md_audit`.
- Existing `test_cli_smoke_all_tools.py` остаётся pytest gate для всех 30
  subcommands и nested cwd / relative paths.

Снаружи:

- Не требовать network/index warmup для default selftest.
- Не считать broad goal complete, пока complaints 3/4/5 и реальные skill
  сценарии не проверены отдельным audit pass.

## Acceptance

- [x] `md selftest --json` содержит `cli_json_smoke` для быстрых tools.
- [x] `md selftest --json` возвращает `pass=29`, `skip=1`, `fail=0` на fixture
  corpus без network/index warmup.
- [x] `SMOKE_AUDIT=1 md selftest --json` либо проходит на fixture, либо даёт
  понятный failure/skip contract без raw traceback.
- [x] Complaints 3/4/5 классифицированы как fixed / not-a-bug / remaining.
- [x] Full `uv run pytest` проходит после scenario selftest changes.

## Evidence

- Implemented: `src/md_cli/handlers/selftest.py` теперь запускает per-tool
  CLI JSON smoke через `python -m md_cli ... --json`.
- Regression: `tests/test_selftest.py` проверяет наличие `cli_json_smoke` у
  всех non-skip rows.
- `uv run pytest tests/test_selftest.py tests/test_cli_smoke_all_tools.py tests/test_catalog_contract.py` → `12 passed`.
- `uv run python -m md_cli selftest --json` → summary `pass=29`, `fail=0`,
  `skip=1`, `total=30`.
- `SMOKE_AUDIT=1 uv run python -m md_cli selftest --json` → summary
  `pass=30`, `fail=0`, `skip=0`, `total=30`.
- `uv run pytest` → `250 passed`.
- Complaint #3 (`md changed --base HEAD` showed fewer files): classified as
  contract/UX, not data-loss bug. `test_changed_path_filter.py` proves
  default excludes hide `_archive/`, `runs/`, `build/`, while
  `--no-default-excludes` returns all git-diff Markdown paths.
- Complaint #4 (`md repeated-concepts` huge output): classified fixed enough
  for agent workflow by `_envelope.next_step` narrowing. Covered by
  `test_envelope_truncation_hint.py` and generated-action parser tests.
- Complaint #5 (`md index --confirm` required 3 launches): classified fixed.
  `md index --dry-run` returns `_envelope.lock` plus executable
  `_envelope.next_step` with `confirm=true` and matching `transaction_id`;
  `test_mcp_cli_parity.py` now asserts that exact action.

## Next

Следующий фронт broad goal: проверить реальные skill usage paths поверх этого
selftest gate, особенно `1md-navigator` / `1md-graph` command snippets и
large-output сценарии на живом corpus.
