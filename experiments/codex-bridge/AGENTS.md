# codex-bridge — правда под-проекта

Под-проект `experiments/`. Правь субтри от этого файла и `README.md`, не от
корневого AGENTS.

## Что это

Вызов Codex из Claude Code как субагента: один вход `codex_review.py`
(`codex_launch.py agent`) — исполнитель, ревьюер или консультант, по заданию.
Полный доступ, рабочая папка — проект; роль и границы задают слова задания.
Backend здесь; operator/router — `~/.claude/skills/1codex/`.

## Инварианты (не ломать)

- **Биллинг через аккаунт.** `cbcommon.scrub_billing_env()` вызывается ДО запуска
  любого codex-процесса. Не убирай и не обходи — это защита от ухода на платный
  API. Любой новый вход (скрипт/режим) обязан звать его первым.
- **Модель и effort фиксируются backend-ом; tier — нет.** Default для всех
  Codex turns: `model=gpt-6.1-sol`, `effort=medium` — явно, независимо от дрейфа
  `~/.codex/config.toml`: `model` в каждом `thread_start` + `thread_resume` +
  `thread.turn`, `effort` на ходе (`thread.turn`), где его и принимает SDK.
  Ярусы вызова (владелец,
  2026-09-06, `_ops/chat-recall/2026-09-06-170311-claude-557afe59.md#L16`):
  `sol`+`medium` — дефолт, средняя работа; `luna`+`max` — много тупой работы;
  `astra`+`medium` (`gpt-6-astra`, живой пробник 2026-09-06 — `completed`) —
  суперумная работа. Луна и астра — поколения 6 (`gpt-6-luna`, `gpt-6-astra`;
  владелец 2026-09-23,
  `_ops/chat-recall/2026-09-23-051553-claude-483a304e.md#recall-9805fef9e16041928ddf6a675d7d952d`),
  сол — 6.1 (`gpt-6.1-sol`; владелец 2026-10-02,
  `_ops/chat-recall/2026-10-02-101553-claude-b40c28c9.md#recall-6e3fc918be584575ac201bde163a183a`).
  Это дефолты по роду работы, каталог не блокируется
  (там же, `#L17`): `--model`/`--effort` — выбор по ситуации, включая
  `max`/`ultra`.
  `terra` доступен явным `--model`, штатным ярусом моста не является
  (`md-scout` с 2026-09-23 работает на `gpt-6-luna`). Service tier мост по умолчанию НЕ шлёт (вердикт
  владельца 2026-07-25, снят форсинг fast от 2026-07-20): `None` опускается
  SDK (`exclude_none`), движок наследует tier из config; `features.fast_mode`
  через `config_overrides` тоже не форсится. `--service-tier` — только
  осознанный per-run opt-in. НЕ цитируй issues `#15853`/`#26391` как «SDK не
  наследует» — они про другой клиент. Новый вход: используй
  `codex_defaults.py`.
- **Права — как у субагента Claude, решение владельца 2026-09-27**: «Просто надо
  убрать все эти ограничения. Сделать их более похожими на твоих субагентов.
  […] Будем рассчитывать на то, что агенты будут слушаться слов»
  (`_ops/chat-recall/2026-09-27-143316-claude-d19cb11d.md#recall-18957d9ea5894a1c99c3618d8c3265fb`).
  Каждый ход — `AGENT_SANDBOX=full_access` + `ApprovalMode.deny_all`, cwd =
  проект; что менять, решает задание. Не возвращай песочницу, списки файлов,
  отдельные деревья или постфлайт-сверку диска как «защиту»: владелец снял их
  сознательно, чтобы отдавать Codex пишущую работу. Исключение одно и
  опциональное — `--scratch`: `workspace_write` в свежей копии проекта
  (`codex_scratch.py`), для проверок с побочными изменениями.
- **Слова вместо песочницы кладёт мост.** Общие правила хода — не трогать чужие
  правки и git-откаты, не коммитить без просьбы, не звать `claude-mcp`, отчёты
  класть в `out/` прогона — живут в `SHARED_RULES`/`OUT_DIR_RULE`
  (`codex_review.py`) и уходят в роль каждого режима, кроме нативного `diff`.
  Держи их тут, а не в памяти вызывающего: запрет `claude_ask` родился из
  девяти часов тишины (замер 2026-07-28), а чужие незакоммиченные правки git не
  вернёт.
- **Claude владеет background lifecycle.** Не добавляй Python daemon/process
  manager для долгих runs. Backend только пишет compact stdout, heartbeat events
  и `run_dir` files; Claude skill решает, когда стартовать background Bash,
  читать status/tail или останавливать task. Витрина `codex_launch.py`
  прогон не убивает: закрылась по потолку — карточка ждёт конца хода;
  остановка — только сигналом (TaskStop).
- **Ход идёт через `turn()`+`stream()`, активность — на диск.** `thread.run()`
  потребляет поток нотификаций и выбрасывает его: пульс тогда говорит «жив», но
  не «движется». Вход стартует ход через `thread.turn()` и отдаёт handle
  в `codex_progress.run_turn`; `TurnResult` собирает штатный
  сборщик SDK, приёмка не меняется. Активность пишется в `events.jsonl` как
  `event=codex` (дельты только считаются — в журнал не идут). **Прогресс скрыт
  по умолчанию:** смысл субагента — беречь контекстное окно, поэтому stdout
  прогона не растёт, а заглядывают через `codex_progress.py RUN_DIR` (сводка на
  несколько строк). Сырой `events.jsonl` в окно оркестратора не читают.
- **Тред заводит только явный `--dialog`.** Автовключение на тяжёлом усилии
  снято 2026-08-14: оно навязывало персистентный тред одноразовому вопросу.
  Глубина мышления не доказывает второй ход.
- **Bridge threads эфемерны.** Вход стартует thread с
  `ephemeral=BRIDGE_THREAD_EPHEMERAL` (`codex_defaults.py`, =`True`). `~/.codex` —
  owner auth/config/runtime, общий с Codex Desktop, который рисует каждый
  материализованный thread как чат. Единственный audit/debug owner прогона — его
  run_dir: обязательный `--run-dir` внутри рабочей папки работы,
  `<project>/_workspace/work-artifacts/<дата-тема>/agents/codex-artifacts/<стамп>-<имя>/`.
  Launcher и прямой вход без пути отказывают с кодом 2 до создания файлов;
  `<project>/_workspace/codex-artifacts/` автоматически не создаётся.
  Ledger без project сохраняет fallback `runs/`; `--doctor` run_dir не требует.
  Desktop history audit
  surface'ом НЕ является. Ledger пишет `codex.thread_ephemeral` как
  доказательство. Не убирай флаг и не заводи второй `CODEX_HOME` (это клонирует
  auth/config/hooks и даёт profile-drift). Санкционированное исключение одно:
  диалог `--dialog`/`--continue` (персистентный тред — resume требует
  rollout на диске, обязательный явный run_dir, provenance-реестр
  `~/.local/state/codex-bridge/dialog-threads/<SHA-256 канонического пути проекта>.jsonl`;
  см. README «Вызов агента»). Реестр находится вне проекта, переживает сессии
  и уборку рабочих папок. Доски прогонов ищут
  `_workspace/work-artifacts/*/agents/codex-artifacts/*`.
- **Дрейф движка не роняет мост.** ChatGPT.app авто-обновляется, SDK запинен —
  неизвестные enum-значения ломали pydantic-валидацию в обоих направлениях:
  исходящий `--effort ultra` (07.2026) и `max` в ответе `thread_start`
  (2026-07-24, падение до старта Codex). Каждый вход зовёт `harden_sdk_enums()`
  из `codex_sdk_compat.py` сразу после импорта SDK (open-enum `_missing_`,
  warning-once на неизвестное значение); новый вход обязан тоже. Ручных патчей
  в `.venv` не держим — reinstall их стирает. **Апгрейд SDK шим не отменяет:**
  в `0.144.4` открыты 2 enum-класса из 104 (`ReasoningEffort`, `ThreadSource`),
  в `0.147.0` — 3 из 109; дрейф наблюдается живьём (движок 0.146 присылает в
  `CollabAgentTool` значения `search_openai_docs` и `fetch_openai_doc`,
  замер 2026-07-27; движок 0.151 — `SubAgentActivityKind='completed'`,
  замер 2026-09-01). Пин бампаем на конкретную поломку, не по дате релиза;
  сверка 2026-09-01 показала, что `0.147.0` не меняет ничего, что мост
  использует (см. README).
- **Успех turn-а точный.** Только SDK-статус
  `completed` при отсутствии `error` означает успех. `interrupted`,
  `inProgress` и любой неизвестный статус — `ok=false` + ненулевой exit code;
  не восстанавливай успех по наличию partial response. Провалившийся ход
  приходит ИСКЛЮЧЕНИЕМ, а не значением: штатный сборщик SDK
  (`openai_codex/_run.py`, `_raise_for_failed_turn`) поднимает `RuntimeError`
  на `TurnStatus.failed`, поэтому `TurnResult` со `status=failed` до финала не
  доходит. Проверка `result.error` в общем финальном пути остаётся страховкой
  на error при НЕ-failed статусе — не удаляй её как «мёртвую».
- **Роль и политика — каналом `developer_instructions`.** Инвариантная часть
  инструкции (роль режима и общие правила моста) уходит параметром
  `thread_start`/`thread_resume`, а не
  вклеивается в реплику; user-промпт остаётся заданием (для review/ask —
  транскрипт + вопрос). `--continue` шлёт ту же роль тем же каналом повторно
  (resume её принимает, роль идемпотентна); `--mode diff` роли не получает
  вовсе — контракт ревью несёт сам движок. Честность аудита: `prompt.md`
  обязан показывать ПОЛНУЮ эффективную инструкцию — обе секции сразу
  (`codex_run_ledger.render_prompt_document`), а manifest несёт
  `developer_instructions_chars` рядом с `prompt_chars` (`prompt_chars` —
  длина именно user-промпта). Новый вход обязан делать так же:
  инструкция, которой нет в run_dir, для аудита не существует.
- **Ретраится только СТАРТ.** `thread_start` / `thread_resume` / `thread.turn`
  оборачиваются в `codex_retry` (поверх `retry_on_overload` из SDK):
  transient `server_overloaded` не должен терять оплаченный ход. Потребление
  потока НЕ ретраится — повтор после начала хода означал бы второй оплаченный
  turn. Каждая попытка пишется в ledger событием `retry` (`operation`,
  `attempt`): молчаливый повтор прятал бы нестабильность
  движка. Вторая восстановимая причина отказа старта — АРХИВНЫЙ тред: уборка
  доски (`codex_threads.py archive`) штатно архивирует диалоги, к которым
  потом возвращается `--continue`. `resume_thread` поднимает его и повторяет старт
  один раз (событие `thread_unarchived`), а успешный подъём ещё пишется
  в реестр диалогов событием `unarchive` — доска считает статус по событиям, и
  `continue` архивность не снимает.

## Карта файлов

- `cbcommon.py` — общая биллинг-гигиена (одна правда) + мелкие общие помощники
  входов: `first_nonblank`, `UsageError`, точный статус хода
  (`codex_status_value`, `codex_turn_completed`).
- `codex_sdk_compat.py` — open-enum hardening запиненного SDK: дрейф движка
  ChatGPT.app не роняет мост.
- `codex_retry.py` — восстановимые отказы СТАРТА: ретрай под перегрузкой движка
  и подъём архивного треда при resume; события `retry`,
  `thread_unarchived`, `thread_unarchive_failed` в ledger.
- `codex_defaults.py` — ярусы вызова и runtime default (`gpt-6.1-sol`+`medium`),
  права хода (`AGENT_SANDBOX`, `SCRATCH_SANDBOX`, approval),
  `BRIDGE_THREAD_EPHEMERAL`.
- `codex_launch.py` — короткая команда карточки: свежий `RUN_DIR`, вход моста
  отдельным процессом, витрина `codex_watch.py watch --pulse` в stdout.
- `codex_review.py` — единственный вход: Codex-субагент. Default режим `task`:
  самодостаточное задание без транскрипта (вызов «как субагент»). Режимы
  `review`/`ask` дополнительно ищут и рендерят транскрипт сессии Claude,
  `diff` зовёт нативный ревьюер движка. Здесь же роли режимов и
  `SHARED_RULES`.
- `codex_scratch.py` — свежая APFS-копия проекта для `--scratch` и её уборка.
- `codex_recall.py` — глубокий recall по корпусу цитат владельца одним вызовом
  для Claude и Codex; владеет промптом, чтобы обе стороны спрашивали одинаково.
  Ревьюер на `luna`+`xhigh`, `--no-dialog`; тактику поиска модели не диктует.
- `codex_run_ledger.py` — журнал прогона: `run_dir`, события, пульс, атомарная
  запись. Он же владеет формой своих артефактов:
  `render_prompt_document` (полная эффективная инструкция в `prompt.md`) и
  `RunResult` — единый финализатор `result.json` + событие + compact stdout,
  которым вход закрывает ВСЕ свои ветки (dry-run,
  недоступный SDK, исключение, завершённый ход).
- `codex_footprint.py` — след моста СНАРУЖИ run_dir: треды на удалённых папках
  и мёртвые записи `[projects.*]`. Локальный бесплатный скан; питает `--doctor`
  и `codex_threads.py archive --orphaned`. Ничего не удаляет.
- `codex_progress.py` — живая активность хода: tee потока нотификаций в журнал,
  `ProgressTracker` для пульса, `digest()`, доска и CLI-сводка, реплика в ход
  (`--steer`).
- `codex_watch.py` — витрина карточки (`watch --pulse`) и живая доска
  прогонов (`look`).
- `codex_threads.py` — доска диалогов, `mine`, история и архив тредов.
- `requirements.txt` — pinned `openai-codex` SDK + bundled CLI bin. venv в
  `.venv/` (git-ignored).

## Проверка

`--dry-run` у `codex_review.py` гоняет рендер без трат. Перед сдачей
запускай `.venv/bin/python -m unittest discover tests` и
`.venv/bin/python -m pyflakes *.py` из папки моста. Реальные прогоны тратят
кредиты аккаунта; тестируй на временных подпапках и чисти за собой.

**pyflakes обязателен, `py_compile` его не заменяет.** Замер 2026-08-14: рефактор
оставил имя, уехавшее в другую функцию; компиляция прошла, все тесты остались
зелёными, а первый живой прогон упал бы `NameError`. Причина дыры — ни один
тест не проходил `main()` на НЕ-dry-run пути. Теперь такие тесты есть у
`codex_review.py` (стаб SDK, например
`test_task_mode_thread_start_ephemeral_full_access`); правя путь живого
прогона, держи их зелёными — только они там что-то доказывают.
