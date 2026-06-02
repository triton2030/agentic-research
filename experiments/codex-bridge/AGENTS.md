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
- **Backend владеет safety.** `codex_orchestrate.py` — не thin launcher, а
  entrypoint guarded shared-worktree orchestrator. Runtime safety живёт в backend:
  strict schema/preflight до импорта Codex, exact file allowlist, git fail-closed
  для real run, dirty fingerprint snapshot, run ledger, aggregate postflight
  allowlist и optional verification. Skill `1codex` — router/operator guide, не
  источник runtime enforcement.
- **Воркер пишет под контрактом.** `codex_orchestrate.py` — `workspace_write` +
  `auto_review`; `files` обязательны и enforced preflight/postflight. Не ставь
  `Sandbox.full_access` default-ом: изменения вне project/git scope нельзя
  честно проверить postflight allowlist. Shared worktree не доказывает
  per-worker attribution; worktree isolation остаётся Stage 2.

## Карта файлов

- `cbcommon.py` — общая биллинг-гигиена (одна правда).
- `codex_defaults.py` — общий runtime default: `gpt-5.5`, `xhigh`, sandbox и
  approval labels для ledger/docs.
- `codex_review.py` — ревьюер/консультант, поиск и рендер транскрипта Claude.
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
