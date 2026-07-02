# codex-bridge — правда под-проекта

Под-проект `experiments/`. Правь субтри от этого файла и `README.md`, не от
корневого AGENTS.

## Что это

Вызов Codex из Claude Code: ревьюер (read-only) и флот воркеров (workspace-write)
под оркестрацией Claude. Backend здесь; декларативный скилл — `~/.claude/skills/1codex/`.

## Инварианты (не ломать)

- **Биллинг через аккаунт.** `cbcommon.scrub_billing_env()` вызывается ДО запуска
  любого codex-процесса. Не убирай и не обходи — это защита от ухода на платный
  API. Любой новый вход (скрипт/режим) обязан звать его первым.
- **Модель фиксируется backend-ом.** Default для всех Codex turns:
  `model=gpt-5.5`, `effort=xhigh` (Extra High). Не полагайся только на
  `~/.codex/config.toml`; если добавляешь новый вход, используй
  `codex_defaults.py` и передавай model/effort в `thread.run`.
- **Ревьюер писать не должен.** `codex_review.py` — всегда `Sandbox.read_only` +
  `ApprovalMode.deny_all`, даже если пользователь просит "максимальные"
  permissions.
- **Исследователь пишет только себе.** `codex_investigate.py` —
  `Sandbox.workspace_write` c cwd=`run_dir/out`; писать в проект запрещено
  sandbox-ом (не постфактум-чеком). Не переводи cwd на корень проекта и не давай
  `full_access` — это стёрло бы границу между исследователем и флотом. Scope-чек
  исключает поддерево `run_dir` (свой scratch/ledger ≠ правка проекта).
- **Backend владеет safety.** `codex_orchestrate.py` — не thin launcher, а
  entrypoint guarded shared-worktree orchestrator. Runtime safety живёт в backend:
  strict schema/preflight до импорта Codex, exact file allowlist, git fail-closed
  для real run, dirty fingerprint snapshot, run ledger, aggregate postflight
  allowlist и optional verification. Skill `1codex` — router/operator guide, не
  источник runtime enforcement.
- **Claude владеет background lifecycle.** Не добавляй Python daemon/process
  manager для долгих runs. Backend только пишет compact stdout, heartbeat events
  и `run_dir` files; Claude skill решает, когда стартовать background Bash,
  читать status/tail или останавливать task.
- **Bridge threads эфемерны.** Оба входа стартуют thread с
  `ephemeral=BRIDGE_THREAD_EPHEMERAL` (`codex_defaults.py`, =`True`). `~/.codex` —
  owner auth/config/runtime, общий с Codex Desktop, который рисует каждый
  материализованный thread как чат. Единственный audit/debug owner прогона —
  `runs/<run_id>/`; Desktop history audit surface'ом НЕ является. Ledger пишет
  `codex.thread_ephemeral` как доказательство. Не убирай флаг и не заводи второй
  `CODEX_HOME` (это клонирует auth/config/hooks и даёт profile-drift).
- **Воркер пишет под контрактом.** `codex_orchestrate.py` — `workspace_write` +
  `auto_review`; `files` обязательны и enforced preflight/postflight. Не ставь
  `Sandbox.full_access` default-ом: изменения вне project/git scope нельзя
  честно проверить postflight allowlist. Shared worktree не доказывает
  per-worker attribution; worktree isolation остаётся Stage 2.

## Карта файлов

- `cbcommon.py` — общая биллинг-гигиена (одна правда).
- `codex_defaults.py` — общий runtime default: `gpt-5.5`, `xhigh`, sandbox и
  approval labels для ledger/docs, `BRIDGE_THREAD_EPHEMERAL`.
- `codex_review.py` — консультант/ревьюер read-only. Default режим `task`:
  самодостаточное задание без транскрипта (вызов «как субагент»). Режимы
  `review`/`ask` дополнительно ищут и рендерят транскрипт сессии Claude.
- `codex_investigate.py` — исследователь: читает проект/диск, пишет только в
  `run_dir/out`. Uniform `result.json` c `artifacts` и `scope_status`. Общий
  `start_heartbeat` и ledger-примитивы из `codex_orchestrate_state.py`.
- `codex_orchestrate.py` — entrypoint/runner для guarded shared-worktree пула
  воркеров (`AsyncCodex` + semaphore).
- `codex_orchestrate_contract.py` — pure schema/path/status contract:
  обязательные `prompt`/`files`, exact file allowlist, overlap и status mapping.
- `codex_orchestrate_state.py` — git snapshot/scope-check и ledger primitives.
- `requirements.txt` — pinned `openai-codex` SDK + bundled CLI bin. venv в
  `.venv/` (git-ignored).

## Проверка

`--dry-run` есть у обоих скриптов — гоняет рендер/план без трат. Для оркестрации
запускай `python -m unittest discover experiments/codex-bridge/tests` и
`python -m py_compile experiments/codex-bridge/*.py`. Реальные прогоны тратят
кредиты аккаунта; тестируй на временных подпапках (`_ftest/`, `_wtest/` —
git-ignored) и чисти за собой.
