---
description: "Active task for stabilizing md CLI ownership: status core, legacy boundary, snapshots, next-step policy."
read-before-edit:
  - "[[_ops/PROJECT-ROADMAP.md]]"
  - "[[_ops/project-graph.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[experiments/md-embedding-server/docs/cli-conventions.md]]"
  - "[[experiments/md-embedding-server/docs/architecture-lock.md]]"
edit-after-edit: []
---
# Task — Stabilization refactor текущего `md` CLI

Статус: выполнено; broad goal продолжается отдельным scenario-аудитом.

## Зачем

Цель не в `v2 rewrite`, а в стабилизации текущего `md` CLI как агентной
оболочки вокруг библиотечного ядра. Нужно убрать места, где агент может
получить разные истины: public `md`, legacy CLI, snapshots, docs и envelope
hints.

Пользовательский verdict:

> Я бы делал рефактор, но не “v2 rewrite”. Лучший путь: **stabilization refactor текущего `md` CLI**, чтобы он стал нормальной агентной оболочкой вокруг библиотечного ядра.

## Scope

Внутри:

- `status_core`: одна реализация status state machine.
- Legacy boundary: `scripts/md_navigator.py` / `navigator.cli` остаются
  adapter/shim; новая логика идёт в public `md` / library core.
- Snapshot completeness: catalog, tool snapshot и response snapshots не должны
  расходиться по tool set.
- `next_steps.py` / generated catalog — условные следующие разрезы после
  scenario gates, а не обязательная архитектурная очередь.

Снаружи:

- Не переписывать CLI на Typer/Click.
- Не делать v2 framework.
- Не дробить модули без причины изменения.
- Не трогать Claude-side surfaces без отдельной явной просьбы.

## Порядок

1. Поставить scenario gates перед дальнейшим refactor.
   - Response snapshots покрывают все `TOOLS_BY_ID`.
   - Agent-facing response snapshots не предлагают legacy `md_navigator.py`
     commands, кроме явных diagnostics вроде `md_ping.navigator_script`.
   - Public API / public CLI / legacy CLI дают один status contract с
     `.md-tools.toml`.
2. Вынести `navigator/status_core.py`.
   - `status_core.status_payload(...)` считает payload, state, deltas,
     и config merge.
   - `navigator.api.status` возвращает dict из core.
   - `navigator.index_status.cmd_status` только печатает human/json.
   - `navigator.status_render` отдельно владеет human text.
3. Поставить legacy boundary guard.
   - Tests/lints не дают добавлять новую agent-facing логику в
     `scripts/md_navigator.py` / `navigator.cli`, кроме adapter/register paths.
   - Agent-facing payloads не должны предлагать `md_navigator.py` как next
     command, если есть public `md`.
4. До выноса next-step policy принять boundary decision.
   - Сейчас `status` domain payload и envelope имеют разные action surfaces:
     `recommended_action` и `_envelope.next_step`.
   - Decision: `md_cli.next_steps` — единственный владелец executable action
     policy для `_envelope.next_step`; domain payloads вроде
     `status.recommended_action` остаются доменными подсказками внутри
     результата.
5. Условно вынести `md_cli/next_steps.py`.
   - `envelope.wrap` остаётся wrapper-ом.
   - next-step policy живёт в registry по `tool/error/state`.
6. Условно сделать catalog generated/immutable.
   - Runtime import не патчит контракт.
   - Cleanup/fingerprint injection делает generator или явный sync step.

## Acceptance

- [x] `api.status` и `cmd_status --json` используют один status core и дают
  один contract payload для одинаковых args.
- [x] `.md-tools.toml` config merge применяется одинаково в public API,
  public CLI и legacy `cmd_status --json`.
- [x] `cmd_status` не содержит state-machine логики кроме rendering/exit code.
- [x] Legacy `index_status` adapter не импортирует и не реэкспортит приватные
  `status_core` helper-ы.
- [x] Tests ловят drift между `TOOLS_BY_ID` и `tests/golden/mcp-responses`.
- [x] Agent-facing golden payloads не содержат `md_navigator.py` в
  `related_reading_command`, `status_text`, `next_step` или аналогичных
  command hints.
- [x] `envelope.wrap` не владеет policy next actions после выноса.
- [x] `catalog.py` не мутирует `ToolSpec` при import.
- [x] Targeted tests и полный `uv run pytest` проходят.

## Evidence

- Implemented: `navigator/status_core.py` теперь владеет status state machine;
  `navigator.api.status` и `navigator.index_status.cmd_status` делегируют в
  него.
- Implemented: `navigator/status_render.py` отдельно владеет human rendering.
- Regression: `test_status_public_api_and_legacy_json_share_core` сравнивает
  public API payload и legacy `cmd_status --json` payload для одинаковых args.
- Regression: `test_legacy_status_json_matches_public_api_with_config`
  сравнивает status parity с `.md-tools.toml`.
- Regression: `test_response_snapshots_cover_every_catalog_tool` не даёт
  потерять `md_search_read` или будущие tools в response snapshots.
- Regression: `test_agent_facing_response_snapshots_do_not_suggest_legacy_cli`
  ловит stale `md_navigator.py` hints в agent-facing goldens.
- Regression: `test_legacy_status_adapter_does_not_export_core_internals`
  держит `index_status` adapter-only.
- Implemented: `md_cli.next_steps` теперь владеет `_envelope.next_step`
  executable action policy; `envelope.wrap` только собирает `_envelope`.
- Regression: `test_envelope_delegates_next_step_policy` держит next-step
  policy вне `envelope.py` и не даёт `next_steps.py` импортировать wrapper.
- Implemented: `catalog.py` пересобран из canonical tool-signatures snapshot:
  `$schema` cleanup и `fingerprint` fields теперь находятся в source data, а
  не в import-time mutation loop.
- Regression: `test_catalog_values_match_mcp_snapshot_without_runtime_patching`
  сравнивает `ToolSpec.to_dict()` со snapshot и запрещает cleanup / fingerprint
  injection code в `catalog.py`.
- Repair: `experiments/md-embedding-server/docs/cli-conventions.md` получил
  graph frontmatter; literal link examples rewritten as prose so graph
  preflight no longer reports fake broken links.
- `uv run python -m compileall -q src/navigator/status_core.py src/navigator/status_render.py src/navigator/index_status.py src/navigator/api.py src/navigator/index.py` → pass.
- `uv run pytest tests/test_path_filters.py tests/test_real_world_complaints.py tests/test_catalog_contract.py tests/test_envelope_golden.py` → `31 passed`.
- `uv run pytest tests/test_agent_hint_contract.py tests/test_corpus_config_parity.py tests/test_path_filters.py tests/test_architecture_boundaries.py tests/test_generated_actions_contract.py` → `32 passed`.
- `uv run pytest tests/test_catalog_contract.py tests/test_catalog_signature_match.py tests/test_mcp_cli_parity.py tests/test_generated_actions_contract.py tests/test_envelope_golden.py tests/test_envelope_truncation_hint.py tests/test_architecture_boundaries.py` → `30 passed`.
- `uv run pytest` → `250 passed`.
- `uv run --project experiments/md-embedding-server md preflight _ops/plans/md-cli-agent-contract/task-2026-05-23-md-cli-stabilization-refactor.md --scan . --json` → pass.
- `uv run --project experiments/md-embedding-server md preflight experiments/md-embedding-server/docs/architecture-lock.md --scan . --json` → pass.
- `uv run --project experiments/md-embedding-server md preflight experiments/md-embedding-server/docs/cli-conventions.md --scan . --json` → pass.
- `uv run --project experiments/md-embedding-server md changed --scan . --path-include '_ops/plans/md-cli-agent-contract/*' --path-include 'experiments/md-embedding-server/docs/*' --json` → pass.
- `git diff --check -- experiments/md-embedding-server _ops/plans/md-cli-agent-contract` → pass.
- Fresh-eyes synthesis:
  `trajectory-critic` accepted → scenario gates before structural work;
  `developer-critic` accepted → golden hint guard and config parity first;
  `architecture-critic` accepted → fix status rendering/private exports now,
  defer executable action owner decision before `next_steps.py`.
- `1repo-map` с bias на `status/cmd_status/wrap/catalog` показал центральные
  owner-файлы: `navigator/api.py`, `navigator/index_status.py`,
  `md_cli/envelope.py`, `md_cli/catalog.py`.
- `1cli-tools` probe: доступны `rg`, `ast-grep`, `depcruise`, `jq`, `uv`,
  `pytest` и другие проверки для refactor evidence.
- `ast-grep` подтвердил status split:
  `navigator.api` импортировал `_state_payload` / helpers из
  `navigator.index_status`, а legacy parser импортирует `register_status`.

## Проверка

Минимум:

```bash
uv run pytest tests/test_path_filters.py tests/test_real_world_complaints.py tests/test_catalog_contract.py tests/test_envelope_golden.py
uv run pytest
```

Markdown gates после правок task/docs:

```bash
uv run --project experiments/md-embedding-server md preflight _ops/plans/md-cli-agent-contract/task-2026-05-23-md-cli-stabilization-refactor.md --scan . --json
uv run --project experiments/md-embedding-server md changed --scan . --path-include '_ops/plans/md-cli-agent-contract/*' --path-include 'experiments/md-embedding-server/docs/*' --json
git diff --check -- experiments/md-embedding-server _ops/plans/md-cli-agent-contract
```

## Открытое сомнение

Главное открытое решение: единый owner executable action policy. До него не
выносить `next_steps.py` и не закреплять generated catalog cleanup как
обязательный шаг. Если unresolved complaints 3/4/5 воспроизводятся как
agent-workflow bugs, порядок refactor пересобирается вокруг них.
