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
  Codex turns: `model=gpt-5.6-sol`, `effort=xhigh` — явно в каждом
  `thread_start` + `thread_resume` + `thread.turn`, независимо от дрейфа
  `~/.codex/config.toml`. Ярусы вызова (владелец, 2026-08-14, разворот его же
  решения 2026-07-27): `sol`+`xhigh` — дефолт на всё; `max`/`ultra` — глубже
  дефолта и переходят в диалог; `luna` — только тупые и большие задания.
  `terra` доступен явным `--model` (дефолт `md-scout`), штатным ярусом моста
  быть перестал. Service tier мост по умолчанию НЕ шлёт (вердикт
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
  guarded orchestrator. Runtime safety живёт в backend:
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
- **Тяжёлое усилие — разговор, а не выстрел.** На пути ревьюера
  `--effort` из `HEAVY_EFFORTS` (`xhigh`/`max`/`ultra`) сам включает
  персистентный тред: такой прогон долго читает и думает, и ценность приходит
  во втором обмене — поправить курс или углубить. Отказ осознанный:
  `--no-dialog`. Не делай это молчаливым — вход печатает причину в stderr.
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
- **Воркер пишет под контрактом, по умолчанию в своём дереве.**
  `codex_orchestrate.py` — `workspace_write` + `auto_review`; `files` обязательны
  и enforced preflight/postflight. Не ставь `Sandbox.full_access` default-ом:
  изменения вне project/git scope нельзя честно проверить postflight allowlist.
  `--isolation worktree` (default) даёт воркеру отдельный git worktree от HEAD:
  атрибуция становится фактом, запись вне allowlist отбраковывается вместе с
  деревом, а параллельная запись оркестратора в основное дерево перестаёт валить
  волну (замер 2026-08-14: 41 провал `scope_status` из 106 боевых волн, 68%
  записей `out_of_scope_files` — служебные файлы оркестратора). Вердикт
  `scope_status` в этом режиме строится по per-worker атрибуции, а дрейф
  основного дерева уходит информационным полем `wave.main_tree_drift`.
  `--isolation shared` — прежнее поведение с aggregate-чеком, для задач, которым
  нужно видеть правки друг друга.
- **Волна закрывается в том же прогоне.** Собрать → коммит только файлов
  allowlist → `merge --no-ff` на воркера → снести деревья и ветки; порядок не
  переставляется, и незабранная работа никогда не удаляется (конфликт оставляет
  ветку и валит `ok`). Уборка не опция: дерево — выкладка проекта, и мусор
  копится молча (7.3 ГБ в `~/.codex/worktrees` за три дня к 2026-08-14).
  Инвентарь и ручную уборку мост НЕ оборачивает — это готовый `git worktree`;
  не заводи для них второй интерфейс.
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
  не восстанавливай успех по наличию partial response. Провалившийся ход
  приходит ИСКЛЮЧЕНИЕМ, а не значением: штатный сборщик SDK
  (`openai_codex/_run.py`, `_raise_for_failed_turn`) поднимает `RuntimeError`
  на `TurnStatus.failed`, поэтому `TurnResult` со `status=failed` до финала не
  доходит. Проверка `result.error` в общем финальном пути остаётся страховкой
  на error при НЕ-failed статусе — не удаляй её как «мёртвую».
- **Роль и политика — каналом `developer_instructions`.** Инвариантная часть
  инструкции (роль эксперта/ревьюера, sandbox-контракт исследователя, файловый
  allowlist воркера) уходит параметром `thread_start`/`thread_resume`, а не
  вклеивается в реплику; user-промпт остаётся заданием (для review/ask —
  транскрипт + вопрос). `--continue` шлёт ту же роль тем же каналом повторно
  (resume её принимает, роль идемпотентна); `--mode diff` роли не получает
  вовсе — контракт ревью несёт сам движок. Честность аудита: `prompt.md`
  обязан показывать ПОЛНУЮ эффективную инструкцию — обе секции сразу
  (`codex_run_ledger.render_prompt_document`), а manifest несёт
  `developer_instructions_chars` рядом с `prompt_chars` (`prompt_chars` —
  длина именно user-промпта). У флота своего `prompt.md` нет: точный текст
  файлового контракта и его длина лежат в записи задачи —
  `manifest.tasks[].developer_instructions` (+ `_chars`), пишутся до первого
  хода, поэтому фиксируются и в `--dry-run`. Новый вход обязан делать так же:
  инструкция, которой нет в run_dir, для аудита не существует.
- **Ретраится только СТАРТ.** `thread_start` / `thread_resume` / `thread.turn`
  оборачиваются в `codex_retry` (sync — поверх `retry_on_overload` из SDK,
  async-зеркало для флота — свой backoff на общем `is_retryable_error`):
  transient `server_overloaded` не должен терять оплаченный ход. Потребление
  потока НЕ ретраится — повтор после начала хода означал бы второй оплаченный
  turn. Каждая попытка пишется в ledger событием `retry` (`operation`,
  `attempt`, у флота ещё `worker`): молчаливый повтор прятал бы нестабильность
  движка.

## Карта файлов

- `cbcommon.py` — общая биллинг-гигиена (одна правда) + мелкие общие помощники
  входов (`first_nonblank`).
- `codex_sdk_compat.py` — open-enum hardening запиненного SDK: дрейф движка
  ChatGPT.app не роняет мост.
- `codex_retry.py` — ретрай стартовых вызовов под перегрузкой движка (sync +
  async), события `retry` в ledger.
- `codex_defaults.py` — ярусы вызова и runtime default (`gpt-5.6-sol`+`xhigh`),
  `HEAVY_EFFORTS`, sandbox и
  approval labels для ledger/docs, `BRIDGE_THREAD_EPHEMERAL`.
- `codex_review.py` — консультант/ревьюер с built-in filesystem read-only.
  Default режим `task`:
  самодостаточное задание без транскрипта (вызов «как субагент»). Режимы
  `review`/`ask` дополнительно ищут и рендерят транскрипт сессии Claude.
- `codex_investigate.py` — исследователь: deliverables в `run_dir/out`,
  built-in filesystem также допускает system temp; project drift ловит
  postflight. Uniform `result.json` c `artifacts` и `scope_status`.
- `codex_orchestrate.py` — entrypoint/runner для guarded пула воркеров
  (`AsyncCodex` + semaphore), по умолчанию с worktree-изоляцией. Прогон разложен
  на этапы: `_plan_run` (всё, что проверяется до трат) → `open_wave` → `_run_fleet`
  → `_assess_wave` (закрытие волны и вердикт scope) → `_emit`. Новый шаг добавляй
  этапом, а не строкой в `main()`: она была на 329 строк и любая правка требовала
  прочитать остальные.
- `codex_worktrees.py` — жизненный цикл изоляции целиком: `open_wave` разворачивает
  деревья волны или ни одного, `close_wave` собирает атрибуцию, коммитит только
  allowlist задачи, мерджит и убирает. Открытие и закрытие живут вместе намеренно —
  они меняются одним движением. Инвентарь и разбор конфликтов остаются готовому git.
- `codex_recall.py` — глубокий recall по корпусу цитат владельца одним вызовом
  для Claude и Codex; владеет промптом, чтобы обе стороны спрашивали одинаково.
  Ревьюер на `luna`+`xhigh`, `--no-dialog`; тактику поиска модели не диктует.
- `codex_orchestrate_contract.py` — pure schema/path/status contract:
  обязательные `prompt`/`files`, exact file allowlist, overlap и status mapping.
- `codex_run_ledger.py` — журнал прогона: `run_dir`, события, пульс, атомарная
  запись. Общий для всех трёх входов. Он же владеет формой своих артефактов:
  `render_prompt_document` (полная эффективная инструкция в `prompt.md`) и
  `RunResult` — единый финализатор `result.json` + событие + compact stdout,
  которым reviewer и investigator закрывают ВСЕ свои ветки (dry-run,
  недоступный SDK, исключение, завершённый ход).
- `codex_git_scope.py` — git snapshot и постфлайт-вердикт «писали ли лишнее».
- `codex_progress.py` — живая активность хода: tee потока нотификаций в журнал,
  `ProgressTracker`/`ProgressRegistry` для пульса, `digest()` и CLI-сводка.
- `requirements.txt` — pinned `openai-codex` SDK + bundled CLI bin. venv в
  `.venv/` (git-ignored).

## Проверка

`--dry-run` есть у обоих скриптов — гоняет рендер/план без трат. Для оркестрации
запускай `python -m unittest discover experiments/codex-bridge/tests` и
`python -m pyflakes experiments/codex-bridge/*.py`. Реальные прогоны тратят
кредиты аккаунта; тестируй на временных подпапках (`_ftest/`, `_wtest/` —
git-ignored) и чисти за собой.

**pyflakes обязателен, `py_compile` его не заменяет.** Замер 2026-08-14: рефактор
оставил в `defaults` имя, уехавшее в другую функцию; компиляция прошла, все 106
тестов остались зелёными, а первый живой прогон упал бы `NameError`. Причина
дыры — ни один тест не проходил `main()` на НЕ-dry-run пути. Теперь такой тест
есть один (`test_full_run_path_end_to_end_with_isolation`); правя путь живого
прогона, держи его зелёным — он единственный, кто там что-то доказывает.
