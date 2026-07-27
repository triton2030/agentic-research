# codex-bridge — правда под-проекта

Под-проект `experiments/`. Правь субтри от этого файла и `README.md`, не от
корневого AGENTS.

## Что это

Вызов Codex из Claude Code в трёх профилях: reviewer (built-in filesystem
read-only), investigator (артефакты в `out/`, project drift ловит postflight) и
fleet (workspace-write в проект). Backend здесь; operator/router —
`~/.claude/skills/1codex/`.

## Инварианты (не ломать)

- **Биллинг через аккаунт.** `cbcommon.scrub_billing_env()` вызывается ДО запуска
  любого codex-процесса. Не убирай и не обходи — это защита от ухода на платный
  API. Любой новый вход (скрипт/режим) обязан звать его первым.
- **Модель и effort фиксируются backend-ом; tier — нет.** Default для всех
  Codex turns: `model=gpt-5.6-sol`, `effort=xhigh` (Extra High) — явно в каждом
  `thread_start` + `thread_resume` + `thread.run`, независимо от дрейфа
  `~/.codex/config.toml`. Service tier мост по умолчанию НЕ шлёт (вердикт
  владельца 2026-07-25, снят форсинг fast от 2026-07-20): `None` опускается
  SDK (`exclude_none`), движок наследует tier из config; `features.fast_mode`
  через `config_overrides` тоже не форсится. `--service-tier` — только
  осознанный per-run opt-in. НЕ цитируй issues `#15853`/`#26391` как «SDK не
  наследует» — они про другой клиент. Новый вход: используй
  `codex_defaults.py`.
- **Ревьюер не получает права править проект.** `codex_review.py` всегда задаёт
  built-in filesystem `Sandbox.read_only` + `ApprovalMode.deny_all`; backend
  пишет только audit ledger в отдельный `run_dir`. Внешние MCP живут вне этого
  sandbox, поэтому их наличие не является разрешением на side effects.
- **Исследователь пишет deliverables себе.** `codex_investigate.py` задаёт
  `Sandbox.workspace_write` c cwd=`run_dir/out`: built-in filesystem пишет в
  `out/` + system temp, а project path блокируется. Внешние MCP находятся вне
  sandbox; postflight scope-check обнаруживает project drift и роняет `ok`.
  Не переводи cwd в проект и не давай `full_access`. Scope-чек исключает
  поддерево `run_dir` (свой scratch/ledger ≠ правка проекта).
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
- **Ход идёт через `turn()`+`stream()`, активность — на диск.** `thread.run()`
  потребляет поток нотификаций и выбрасывает его: пульс тогда говорит «жив», но
  не «движется». Каждый вход стартует ход через `thread.turn()` и отдаёт handle
  в `codex_progress.run_turn` / `run_async_turn`; `TurnResult` собирает штатный
  сборщик SDK, приёмка не меняется. Активность пишется в `events.jsonl` как
  `event=codex` (дельты только считаются — в журнал не идут). **Прогресс скрыт
  по умолчанию:** смысл субагента — беречь контекстное окно, поэтому stdout
  прогона не растёт, а заглядывают через `codex_progress.py RUN_DIR` (сводка на
  несколько строк). Сырой `events.jsonl` в окно оркестратора не читают.
- **Bridge threads эфемерны.** Все входы стартуют thread с
  `ephemeral=BRIDGE_THREAD_EPHEMERAL` (`codex_defaults.py`, =`True`). `~/.codex` —
  owner auth/config/runtime, общий с Codex Desktop, который рисует каждый
  материализованный thread как чат. Единственный audit/debug owner прогона — его
  run_dir (default `<project>/_workspace/codex-artifacts/<run_id>/`, локально в
  проекте работы; legacy `runs/` — fallback без project); Desktop history audit
  surface'ом НЕ является. Ledger пишет `codex.thread_ephemeral` как
  доказательство. Не убирай флаг и не заводи второй `CODEX_HOME` (это клонирует
  auth/config/hooks и даёт profile-drift). Единственное санкционированное
  исключение — диалог ревьюера `--dialog`/`--continue`: персистентный тред
  (resume требует rollout на диске), обязательный авто-run_dir и
  provenance-реестр `dialog-threads.jsonl`; см. README «Консультант / ревьюер».
- **Воркер пишет под контрактом.** `codex_orchestrate.py` — `workspace_write` +
  `auto_review`; `files` обязательны и enforced preflight/postflight. Не ставь
  `Sandbox.full_access` default-ом: изменения вне project/git scope нельзя
  честно проверить postflight allowlist. Shared worktree не доказывает
  per-worker attribution; worktree isolation остаётся Stage 2.
- **Дрейф движка не роняет мост.** ChatGPT.app авто-обновляется, SDK запинен —
  неизвестные enum-значения ломали pydantic-валидацию в обоих направлениях:
  исходящий `--effort ultra` (07.2026) и `max` в ответе `thread_start`
  (2026-07-24, падение до старта Codex). Каждый вход зовёт `harden_sdk_enums()`
  из `codex_sdk_compat.py` сразу после импорта SDK (open-enum `_missing_`,
  warning-once на неизвестное значение); новый вход обязан тоже. Ручных патчей
  в `.venv` не держим — reinstall их стирает. **Апгрейд SDK шим не отменяет:**
  в `0.144.4` открыты 2 enum-класса из 104 (`ReasoningEffort`, `ThreadSource`),
  остальные 102 закрыты; дрейф наблюдается живьём (движок 0.146 присылает в
  `CollabAgentTool` значения `search_openai_docs` и `fetch_openai_doc`,
  замер 2026-07-27).
- **Успех turn-а точный.** Для review / investigate / worker только SDK-статус
  `completed` при отсутствии `error` означает успех. `interrupted`,
  `inProgress` и любой неизвестный статус — `ok=false` + ненулевой exit code;
  не восстанавливай успех по наличию partial response.

## Карта файлов

- `cbcommon.py` — общая биллинг-гигиена (одна правда).
- `codex_sdk_compat.py` — open-enum hardening запиненного SDK: дрейф движка
  ChatGPT.app не роняет мост.
- `codex_defaults.py` — общий runtime default: `gpt-5.6-sol`, `xhigh`, sandbox и
  approval labels для ledger/docs, `BRIDGE_THREAD_EPHEMERAL`.
- `codex_review.py` — консультант/ревьюер с built-in filesystem read-only.
  Default режим `task`:
  самодостаточное задание без транскрипта (вызов «как субагент»). Режимы
  `review`/`ask` дополнительно ищут и рендерят транскрипт сессии Claude.
- `codex_investigate.py` — исследователь: deliverables в `run_dir/out`,
  built-in filesystem также допускает system temp; project drift ловит
  postflight. Uniform `result.json` c `artifacts` и `scope_status`.
- `codex_orchestrate.py` — entrypoint/runner для guarded shared-worktree пула
  воркеров (`AsyncCodex` + semaphore).
- `codex_orchestrate_contract.py` — pure schema/path/status contract:
  обязательные `prompt`/`files`, exact file allowlist, overlap и status mapping.
- `codex_run_ledger.py` — журнал прогона: `run_dir`, события, пульс, атомарная
  запись. Общий для всех трёх входов.
- `codex_git_scope.py` — git snapshot и постфлайт-вердикт «писали ли лишнее».
- `codex_progress.py` — живая активность хода: tee потока нотификаций в журнал,
  `ProgressTracker`/`ProgressRegistry` для пульса, `digest()` и CLI-сводка.
- `requirements.txt` — pinned `openai-codex` SDK + bundled CLI bin. venv в
  `.venv/` (git-ignored).

## Проверка

`--dry-run` есть у обоих скриптов — гоняет рендер/план без трат. Для оркестрации
запускай `python -m unittest discover experiments/codex-bridge/tests` и
`python -m py_compile experiments/codex-bridge/*.py`. Реальные прогоны тратят
кредиты аккаунта; тестируй на временных подпапках (`_ftest/`, `_wtest/` —
git-ignored) и чисти за собой.
