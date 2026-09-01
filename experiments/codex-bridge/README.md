# codex-bridge

Вызов Codex (ChatGPT) из Claude Code. Зеркало `claude-bridge` (тот гоняет Claude
из Codex; этот — Codex из Claude).

Три профиля — по месту deliverables и built-in filesystem boundary (читает во
всех весь диск; внешние MCP — отдельная граница ниже):

- **Консультант / ревьюер** (`codex_review.py`) — built-in filesystem read-only;
  project edits не разрешены, backend пишет служебный audit ledger в `run_dir`.
  Два способа дать контекст:
  - **`task` (default)** — задание/вопрос БЕЗ транскрипта, как вызов субагента.
    Codex видит файлы проекта, но не историю сессии. Дёшево и быстро — основной
    режим. `codex_review.py "задание"`.
  - **`review` / `ask`** — с транскриптом текущей сессии Claude: стороннее ревью
    ХОДА работы или вопрос «по нашему диалогу». Дороже; бери, только когда Codex
    реально нужна история, а не файлы проекта.
- **Исследователь** (`codex_investigate.py`) — built-in filesystem пишет в
  `run_dir/out/` + system temp, а project path блокируется sandbox-ом;
  postflight ловит project drift. Для «изучи X, собери данные, напиши отчёт»
  Codex складывает deliverables в `out/`, Claude забирает `result.json` и сливает
  фан-аут кодом. Как вызов субагента: транскрипт не тянется.
- **Флот воркеров** (`codex_orchestrate.py`) — guarded workspace-write, по
  умолчанию с worktree-изоляцией: каждый воркер работает в своём git worktree от
  HEAD. Claude как оркестратор раздаёт file-disjoint задачи, backend валидирует
  контракт до запуска Codex, гонит N Codex параллельно (`AsyncCodex` + лимит
  concurrency), пишет run ledger, считает атрибуцию по дереву каждого воркера и в
  том же прогоне забирает работу в проект и убирает деревья.

Управляется глобальным скиллом **`1codex`** (`~/.claude/skills/1codex/`).

## Long-run control

Запуски должны быть Claude-native background Bash jobs — **все оплаченные, а не
только заведомо долгие**: форграундный вызов вешает сессию, и пользователь
видит замерший экран. Харнесс сам присылает одно уведомление о завершении.
Backend не управляет процессами Claude: он пишет свежий `run_dir`, компактный
stdout и файловые результаты, чтобы Claude мог продолжать работу и по
необходимости читать `events.jsonl` / `result.json`.

Для background-safe режима используй `--summary-stdout --run-dir PATH`.
`PATH` должен быть свежим: каталог создаёт backend. Stdout будет коротким JSON
с `run_id`, `run_dir`, статусами и путями; полный ответ лежит на диске.
`--heartbeat-sec N` пишет `heartbeat` events во время Codex-run-а (`0`
отключает). `Monitor` для ожидания завершения НЕ используется: каждая его
строка — сообщение в контексте агента, а одно уведомление «готово» даёт сам
фоновый Bash.

**«Движемся ли мы вообще».** Ход идёт через `thread.turn()` + `stream()`, и
активность Codex попадает в `events.jsonl` (`event=codex`): шаги, выполненные
команды, изменённые файлы, план. Пульс несёт `steps`, `idle_sec` и `last`, у
флота — `active` и `stalest` (воркер, молчащий дольше всех). Раньше пульс
говорил только «жив»; теперь по нему видно направление.

Смотреть это надо **сводкой, а не журналом** — субагент существует, чтобы
беречь контекстное окно оркестратора:

```bash
python codex_progress.py <RUN_DIR> [--tail N]   # несколько строк, не поток
```

Сырой `events.jsonl` в окно не читают; он для машины и для разбора постфактум.

Первая строка сводки — **исходное задание** (`# Цель` из `prompt.md`, у флота —
состав воркеров). Без неё по сводке видно, ЧТО агент делает, но не туда ли он
идёт: сравнивать было не с чем.

**Вмешательство в идущий ход.** Прогон — отдельный процесс, SDK-ручка хода
принадлежит ему, поэтому канал идёт через диск: `control.jsonl` в `run_dir` и
сторож рядом с ходом.

```bash
python codex_progress.py <RUN_DIR> --steer "ТЕКСТ" [--worker TASK_ID]
```

- Кредитов не стоит и хода не начинает: команда только кладёт реплику в ящик.
- Сторож — отдельный поток (у флота — asyncio-задача), а не проверка между
  событиями: поток нотификаций молчит минутами, пока модель думает, и реплика
  приезжала бы тогда, когда вмешиваться уже поздно.
- События: `steer_requested` → `steer_accepted` | `steer_rejected`. **`applied`
  нет намеренно** — движок подтверждает приём реплики, но не смену курса; курс
  проверяется следующими шагами сводки.
- Отказ движка — нормальный ответ, а не авария прогона: ход уже сменился
  (`expectedTurnId`), прогон закончился, либо вид хода не управляем — по схеме
  SDK это только нативное ревью (`--mode diff`) и упаковка контекста.
- Волна требует адресата: без `--worker` команда отказывает и печатает состав.
- Закончившийся прогон реплику не принимает — чинить его надо следующим
  прогоном, которому дан путь к его же `final.md`.

Проверено сквозным прогоном 2026-08-16: фоновый `codex_review.py` получил
реплику через ящик, движок принял её за секунду, и ход закрылся
`status=completed` ответом по новой инструкции вместо старой.

**Перегрузка движка не съедает ход.** Стартовые вызовы (`thread_start`,
`thread_resume`, `thread.turn`) идут через `codex_retry`: transient
`server_overloaded` повторяется (до 3 попыток, backoff как в SDK), и оплаченный
ход не теряется на ровном месте. Потребление потока НЕ ретраится — повтор после
начала хода означал бы второй оплаченный turn. Каждый повтор виден в
`events.jsonl` событием `retry` (`operation`, `attempt`, у флота — `worker`).

**Архивный тред не съедает ремонтный круг.** Мост сам архивирует треды воркеров
на закрытии волны, поэтому тёплый `thread_id` штатно приходит архивным, и голый
`thread_resume` падал `session ... is archived`, не начав работы.
`resume_thread[_async]` поднимает тред и повторяет старт один раз: подъём виден
событием `thread_unarchived`, отказ подъёма — `thread_unarchive_failed`, и
наружу тогда идёт исходная ошибка resume, а не подъёма. Предикат намеренно
широкий — код `-32600` ИЛИ подстрока `archiv`: текст движка интерфейсом не
объявлен. Цена ложного срабатывания — лишний `thread_unarchive` на уже
провалившемся старте; цена пропуска — потерянная задача.

## Audit surface — только run_dir прогона

Единственный audit/debug owner прогона — его `run_dir`. Все входы пишут
`manifest.json`, `events.jsonl` и `result.json`; reviewer/investigator также
держат `prompt.md`/`final.md`, fleet — `results.jsonl`. Default для всех трёх входов —
**локально в проекте работы**: `<project>/_workspace/codex-artifacts/<run_id>/`
(создаёт backend; артефакты не сыплются в чужое репо, субагентам это рабочая
зона — подпапки/архив свободно; при желании добавь `_workspace/` в `.gitignore`
проекта). `--run-dir PATH` — явный override; legacy `<backend>/runs/` остаётся
только fallback-ом без `--project`. Bridge стартует Codex-threads с
`ephemeral=True`, поэтому они не материализуются в общий `~/.codex` session
store. Единственное исключение — диалог ревьюера (`--dialog` / `--continue`):
такой тред персистентен (иначе resume невозможен), а run_dir для него
создаётся автоматически даже без флагов — audit owner обязателен.

**История Codex Desktop НЕ является audit surface для bridge** — не ищи прогоны
там. SDK под капотом запускает тот же локальный движок `codex app-server`, что и
Desktop, и делит с ним `~/.codex`; без `ephemeral` каждый вызов всплывал бы там
как новый чат. `~/.codex` остаётся общим owner-ом только для auth/config/runtime.
Доказательство в каждом прогоне — поле `codex.thread_ephemeral` в `result.json`.

## Модель и runtime-доступ

Backend явно закрепляет Codex turn defaults: `model=gpt-5.6-sol`,
`effort=xhigh` — дефолт (см. «Ярусы вызова» в `AGENTS.md`). Модель и
effort не зависят от текущего
`~/.codex/config.toml`; флаги `--model` и `--effort` остаются только для
осознанного override. Service tier мост по умолчанию НЕ шлёт (см. ниже).

Это текущий потолок под ChatGPT-биллингом, проверено живыми пробниками
2026-07-10: `gpt-5.6-pro` и `gpt-5.6` (без суффикса) возвращают `HTTP 400 —
"not supported when using Codex with a ChatGPT account"`; наверху работает
только `gpt-5.6-sol` — тот же model ID, что в живом `~/.codex/config.toml`.
(Исторический probe 2026-07-02 аналогично отсёк `gpt-5.5-pro`.)

Вниз шкала существует, но НЕ используется. Движок несёт три слага
5.6-семейства — `gpt-5.6-sol` / `gpt-5.6-terra` / `gpt-5.6-luna` (strings
бинаря 0.144.2); `luna` и `terra` были проверены живыми пробниками 2026-07-13
(`completed` под ChatGPT-auth, ~5-6 с). Вердикт владельца 2026-08-14 вернул
`luna` в узкой нише: «луна только для тупых и больших заданий» — объёмная
механика, где нужна пропускная способность, а не суждение. Этим снят его
полный ретайр `luna` от 2026-07-21 (а тем, в свою очередь, был снят «пол —
medium» от 2026-07-13). Ширина берётся
параллельными вызовами на default `sol`, глубина — `--effort ultra`;
`terra` технически работает (и остаётся model-override внутренних
collaboration-субагентов движка), но рекомендованного применения во внешних
вызовах не имеет. Default — `gpt-5.6-sol`.

Service tier / fast mode: вердикт владельца 2026-07-25 — мост fast НЕ
запрашивает (снят прежний форсинг «всегда fast» от 2026-07-20). По умолчанию
`--service-tier` пуст: параметр не шлётся вовсе (SDK сериализует с
`exclude_none=True`, `None` опускается), и движок берёт tier из живого
`~/.codex/config.toml`. Feature gate `features.fast_mode` мост тоже больше не
форсит через `config_overrides`. В stderr-banner это видно как `tier=inherit`,
в ledger — `service_tier: null`.

Явный `--service-tier priority` остаётся осознанным opt-in на прогон
(`priority` — каноническое wire-значение Fast для gpt-5.6; алиас `fast` движок
нормализует в `priority`, живой пробник 2026-07-20 принял оба). Оговорки:
(1) без включённого в config feature gate `features.fast_mode` один только tier
может не маршрутизировать Fast; (2) ГРАНИЦА requested vs applied — ledger и
banner фиксируют ЗАПРОШЕННЫЙ тир из `args` до SDK-вызова, а не применение
сервером; тарификация видна только на дашборде кредитов. Историческая справка:
наследование через `exclude_none` подтверждено round-2 аудитом Codex
2026-07-20 (баги `openai/codex#15853`/`#26391` — про другой клиент, не про
этот SDK; не цитируй их как «SDK не наследует»).

**Codex binary.** `resolve_codex_bin()` в `codex_defaults.py` подставляет в
`CodexConfig.codex_bin` бинарь ChatGPT Desktop
(`/Applications/ChatGPT.app/Contents/Resources/codex`) — он авто-обновляется
вместе с приложением и потому идёт впереди любого пина. Фактический движок
фиксируется в ledger: `codex_bin` + `binary_source` (`chatgpt-app` |
`sdk-bundle`) в блоке `codex` каждого manifest/result и в stderr-banner
(`binary=…`).

Выбор в пользу приложения — осознанный, и его цена названа ниже (дрейф схемы).
Запинить бандл не даёт воспроизводимости: оба бинаря делят один `~/.codex`
(auth, config, кэш моделей), и старый бандл ломается на состоянии, записанном
новым движком, — замер 2026-07-27: `0.137.0a4` не читает текущий `auth.json`
(`invalid type: map, expected a string` на поле `agent_identity`). Бандл
`0.144.4` модель `gpt-5.6-sol` обслуживает (живая проба той же даты) — то есть
апгрейд SDK возможен, но он меняет только версию, не эту развилку. Апгрейд
сделан 2026-08-14 по конкретной поломке: движок шлёт элемент треда
`subAgentActivity` (появляется в любом треде, где Codex звал субагентов), и
`0.1.0b3` ронял на нём `thread_resume` целиком — такие треды были мосту
недоступны. `0.144.4` этот тип знает; дрейф на этом не кончился
(`CollabAgentTool.fetch_openai_doc` уже неизвестен и ему), поэтому
`codex_sdk_compat.py` остаётся.

**Шкала reasoning effort.** Каталог движка (`~/.codex/models_cache.json`,
`supported_reasoning_levels`) для `gpt-5.6-sol` и `gpt-5.6-terra` даёт
`low → medium → high → xhigh → max → ultra`, где по его же описаниям:

- `max` — «Maximum reasoning depth for the hardest problems»;
- `ultra` — «Maximum reasoning **with automatic task delegation**».

То есть глубина одиночного прогона — это `max`, а `ultra` — та же глубина плюс
делегация внутренним субагентам. У `gpt-5.6-luna` потолок `max`. Дефолт моста
— `xhigh` (решение владельца 2026-08-14); `max`/`ultra` со штатных маршрутов
сняты и остаются техническим opt-in. Тред на любом усилии заводит только явный
`--dialog` (автовключение снято 2026-08-14). Как и у
`service_tier`, ledger фиксирует
ЗАПРОШЕННЫЙ effort, применение сервером не доказывает.

Нижний рабочий порог — `low` (см. ниже), верхний берётся из каталога.

**Дрейф enum под запиненным SDK.** ChatGPT.app авто-обновляет движок, а SDK
запинен — wire-протокол дрейфует под замороженной схемой. Дважды это роняло
мост в обоих направлениях: исходящем (`--effort ultra` падал на нашем же
`ReasoningEffort(...)`) и входящем (движок стал слать `max` в ответе
`thread_start`, роняя каждый запуск до старта Codex).

Устойчивость живёт в репо: `codex_sdk_compat.harden_sdk_enums()` вызывается
каждым входом сразу после импорта SDK и делает строковые enum'ы сгенерённой
схемы открытыми (`_missing_`). Неизвестное значение принимается дословно как
pseudo-member, в stderr — warning-once: дрейф виден, но не роняет.

**Апгрейд SDK шим НЕ отменяет.** В `0.144.4` upstream открыл 2 enum-класса из
104 (`ReasoningEffort`, `ThreadSource`) — то есть починил ровно одну известную
регрессию, а механизм остался. Дрейф наблюдается живьём: движок `0.146`
присылает в `CollabAgentTool` значения `search_openai_docs` и
`fetch_openai_doc`, которых схема не знает (замер 2026-07-27).

**Сверка с upstream 2026-09-01: пин остаётся `0.144.4`.** На PyPI вышел
`openai-codex` `0.147.0` (2026-08-18) — взяли его wheel и сравнили с
установленным: `_run.py`, `retry.py`, `client.py`, `_sandbox.py` побайтово
идентичны, `__init__.py` экспортирует ровно тот же набор, в `api.py` добавлен
один необязательный `section_id`. В схеме +63 класса, и все — поверхность
Codex Desktop (apps/connectors, scheduled tasks, thread sections, audio,
plugins, Bedrock); мост не трогает ни одного. Открытых enum'ов стало 3 из 109
(добавлен `PlanType`), то есть шим нужен ровно так же — движок
`0.151.0-alpha.7.2` шлёт `SubAgentActivityKind='completed'`, которого не знает
ни `0.144.4`, ни `0.147.0`, ни `main`. Апстрим-причина структурная и открыта:
`openai/codex#32478` (Python SDK отстаёт от CLI) и `#21871` (skew
десериализации) — оба open на дату сверки. Правило пина не меняется: бампаем
на конкретную поломку, как 2026-08-14 на `subAgentActivity`, а не по дате
релиза.

Проверено тогда же и оказалось прежним: `_sandbox.py` по-прежнему собирает
per-turn политику из пресета без `writable_roots` (оговорка в
`codex_defaults.py` в силе), `service_tier` по-прежнему реально уходит в
`ThreadStartParams` — в `sdk/python/docs/api-reference.md` его в сигнатуре
`thread_start` нет, но это неполнота доки, а не удаление параметра.

Нижний рабочий порог — `low`, и он enforced: `--effort` ниже (`minimal`/`none`)
отсекается на валидации флагов (`REASONING_EFFORTS` в `codex_defaults.py`).
Причина: turn'у по умолчанию доступны инструменты (`web_search`/`image_gen`), и
Codex на `minimal` отвечает `HTTP 400 — "The following tools cannot be used with
reasoning.effort 'minimal': image_gen, web_search"` — валидация превращает этот
поздний runtime-фейл в мгновенный.

Permissions тоже задаются backend-ом явно:

- reviewer: `Sandbox.read_only` + `ApprovalMode.deny_all`;
- write-fleet: `Sandbox.workspace_write` + `ApprovalMode.auto_review`.

`Sandbox.full_access` не является default: он может менять файлы вне git/project
scope, а значит backend не сможет честно доказать postflight allowlist. Максимум
для v1 — свободная работа внутри workspace-write под declared `files`,
dirty-gate, ledger и scope-check.

## Биллинг: только ChatGPT-аккаунт, не API

Все SDK-входы (review / investigate / orchestrate, а также
`codex_threads.py archive/unarchive`; `list` SDK не запускает вовсе) перед
запуском дочернего codex-процесса вырезают из окружения `OPENAI_API_KEY` /
`CODEX_API_KEY` / `OPENAI_BASE_URL` (см. `cbcommon.py`), чтобы случайная
переменная не увела вызов на платный API. Строка `env чист` / `вырезано из
env: …` в логах подтверждает именно вычистку ключей; сам ChatGPT-login backend
не проверяет — auth берётся из твоего `codex login` (`auth_mode=chatgpt`), той
же подписки, что у интерактивного терминала.

Это прямое зеркало того, как `claude-bridge` вырезает `ANTHROPIC_API_KEY`.

## Установка

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # openai-codex
```

SDK тянет собственный пиннутый бинарь `codex`; он читает глобальный
`~/.codex/auth.json`, поэтому отдельный логин не нужен.

## Консультант / ревьюер

```bash
# DEFAULT — задание/вопрос без транскрипта (Codex видит файлы проекта):
.venv/bin/python codex_review.py "Проверь, нет ли гонки в codex_orchestrate.py"
.venv/bin/python codex_review.py --task "Сверь README с реальными флагами кода"

# Стороннее ревью ХОДА текущей сессии (нужен транскрипт):
.venv/bin/python codex_review.py --mode review

# Вопрос «по нашему диалогу» (нужен транскрипт):
.venv/bin/python codex_review.py --mode ask --question "Где здесь дыра в подходе?"

# Диалог: персистентный тред → уточнения/возражения следующей репликой:
.venv/bin/python codex_review.py "ВОПРОС СОВЕТНИКУ" --dialog        # печатает thread_id
.venv/bin/python codex_review.py "УТОЧНЕНИЕ" --continue THREAD_ID   # контекст цел

# Полный каталог флагов — `codex_review.py --help` (здесь не дублируется).
```

Режим `task` (default) транскрипт не подхватывает — это и есть смысл: вызов «как
субагент», самодостаточное задание, дёшево и быстро. Режимы `review` / `ask`
берут транскрипт текущей сессии по `CLAUDE_CODE_SESSION_ID` (иначе — свежайший
`.jsonl` в `~/.claude/projects/<кодированный-путь>/`); рендер сжимает лог:
реплики целиком, вызовы инструментов — одной строкой, дампы результатов усечены.

Reviewer всегда создаёт `run_dir` и пишет `manifest.json`, `events.jsonl`,
`prompt.md`, `result.json`, а после реального Codex-run-а — `final.md`.
`--run-dir` только переопределяет project-local default.

Роль (эксперт в `task`, ревьюер в `review`, рамка вопроса в `ask`) уходит в
движок отдельным каналом — `developer_instructions` у `thread_start`, — а не
вклеивается в реплику: задание остаётся заданием. `prompt.md` при этом
показывает ОБЕ части (секции `DEVELOPER INSTRUCTIONS` и `USER PROMPT`), потому
что audit-владелец обязан показывать полную эффективную инструкцию; в manifest
рядом с `prompt_chars` (длина user-промпта) лежит
`developer_instructions_chars`. У `--mode diff` роли нет вовсе — контракт ревью
несёт сам движок.

Диалог (`--dialog` / `--continue`) — исключение из ephemeral-дефолта: resume
работает только по rollout на диске (эфемерный тред → «no rollout found»,
проверено живыми пробниками 2026-07-12), поэтому диалоговые треды персистентны
и видны в Desktop-истории. Контракты:

- run_dir создаётся автоматически (audit owner обязателен); ledger фиксирует
  `thread_id`, `thread_persistent`, `resumed_from_thread`, событие `thread`.
- Provenance и статусная доска: `--dialog` пишет в
  `<project>/_workspace/codex-artifacts/dialog-threads.jsonl` событие `start`
  (тема из `--topic` или головы задания, короткий id сессии), `--continue` —
  событие `continue`; `--continue` по умолчанию принимает только треды из
  этого реестра — чужой Desktop/API-тред несёт непроверенные роль и контекст.
  Осознанный override — `--continue-foreign` (после него тред «усыновлён»
  реестром). Свёртка реестра и чистка — `codex_threads.py`:
  `list --project PATH` (тема/ходы/активность/сессия/run на тред; события
  несут `run_dir` — точный путь даже при custom `--run-dir`),
  `archive THREAD_ID | --stale [--older-hours 48]` (штатный SDK
  `thread_archive`; per-target ошибки не обрывают батч, rc=1 при частичном
  провале; `--stale` fail closed на битом реестре) и `unarchive THREAD_ID`.
  Ручной `unarchive` перед `--continue` не нужен: архивный тред поднимает сам
  resume, а успешный подъём пишет в реестр событие `unarchive` — доска считает
  статус по событиям, и `continue` архивность не снимает.
  Руками `~/.codex` не чистить. Archive-событие provenance НЕ даёт — чужой
  тред нельзя «легализовать» его архивацией. Реестр append-only без локов:
  «чужой живой тред не трогай» — дисциплина агента, не backend-гарантия.
- Реестр моста знает только свои треды. Что вообще открыто у владельца
  (Codex Desktop, `codex` в терминале) — `codex_threads.py mine [--limit N]
  [--all-projects] [--json]`: нативный `thread_list` движка по общему store
  `~/.codex`, с именем, временем, cwd и веткой. Чтение, кредитов не тратит;
  продолжение такого треда — по-прежнему только через `--continue-foreign`.
- Пустой THREAD_ID (потерянная `$VAR`) — отказ с кодом 2, не молчаливый новый
  тред. `--dry-run` валидирует CLI/prompt/реестр, но НЕ существование треда
  (`resume_checked=false` в ledger).
- Sandbox/approval переприбиваются на каждом turn'е — resume не ослабляет
  read-only. Реплика в `--continue` уходит как есть, без обёртки ролью в
  тексте: контекст уже в треде, а роль повторяется своим каналом
  (`developer_instructions` у `thread_resume`) — она идемпотентна.

## Исследователь

```bash
# Codex читает проект; built-in filesystem пишет в run_dir/out + system temp,
# project path блокируется; ответ забираешь из result.json:
.venv/bin/python codex_investigate.py "Изучи X в проекте и напиши отчёт в out/" --project "$PWD"

# Фоном + компактный stdout (штатный режим под фан-аут):
.venv/bin/python codex_investigate.py "..." --project "$PWD" \
  --run-dir "$B/runs/$(date -u +%Y%m%dT%H%M%SZ)-inv" --summary-stdout --heartbeat-sec 120
#   --dry-run   собрать промпт без вызова Codex
```

`run_dir` создаётся всегда (в нём живёт `out/`); default —
`<project>/_workspace/codex-artifacts/<run_id>/`. Sandbox-контракт Codex
получает каналом `developer_instructions` при `thread_start`, а репликой —
чистое задание: читать весь диск свободно, складывать артефакты в `cwd`
(=`out/`, подпапки и своя структура — свободно) и в конце `result.md`, проект
не править. В `prompt.md` лежат обе части сразу — audit-владелец показывает
полную эффективную инструкцию. Backend пишет уникальный
`result.json`: `status`, `artifacts` (файлы, реально созданные в `out/`),
`scope_status` (второе, независимое доказательство «проект не тронут»; из
проверки исключены `out/` и ledger-файлы; `scope=failed` роняет `ok` в false),
`final_response`.

**Гарантия и её граница (проверено эмпирически).** Built-in filesystem запись в
ПРОЕКТ блокируется sandbox (`operation not permitted`); чтение вне workspace
проходит. Но enforced-writable множество под `workspace_write` = `cwd` (out) + системный temp
(`/tmp`, `$TMPDIR`) — не только `out/`. Сузить до одного `out/` этим SDK нельзя:
для enum-`Sandbox` он шлёт фиксированную per-turn политику, и
`writable_roots`/`exclude_slash_tmp` через `config_overrides` игнорируются. То
есть гарантия sandbox-а — «built-in filesystem не пишет в project path», а не
«пишет исключительно в out/». Temp эфемерен и не является deliverable surface.

Вторая граница: **MCP-серверы Codex живут вне sandbox** (отдельные процессы
движка) и могут писать в проект. Наблюдалось вживую: serena при онбординге
чужого проекта создала `.serena/` — sandbox это не блокировал, а `scope_status`
поймал (`failed` с точными путями). Поэтому scope-чек — не формальность, а
второй, независимый слой доказательства.

Разделение профилей: reviewer не получает project-write authority;
investigator складывает deliverables в `out/` и валит project drift postflight;
fleet пишет в проект под file-disjoint контрактом. Внешние MCP — исключение из
sandbox-enforcement, не из permission contract.

## Флот воркеров

```bash
echo '[
  {"id":"f1","prompt":"Перепиши краткое описание вверху файла короче и яснее","files":["docs/a.md"]},
  {"id":"f2","prompt":"То же для второго файла","files":["docs/b.md"]}
]' | .venv/bin/python codex_orchestrate.py --concurrency 4 --project "$PWD"

# или из файла:
.venv/bin/python codex_orchestrate.py --tasks tasks.json --project "$PWD"
# Проверка после воркеров: --verify "pytest ...".
# Подготовка деревьев под приборы: --tree-setup "npm ci".
# Полный каталог флагов — `codex_orchestrate.py --help`.
```

Вход — JSON-массив задач. `prompt` и `files` обязательны; `id` опционален;
`allow_create: true` разрешает создание отсутствующего файла; `subagents: true`
разрешает воркеру делегировать внутри своего дерева; `model` и `effort` задают
ярус ЭТОЙ задачи поверх флагов прогона; `contracts_changed` и `contracts_read`
объявляют смысловую зону поверх файловой. `cwd` в задаче не
поддерживается: cwd воркера задаёт backend — его worktree в режиме изоляции либо
`--project` в shared. Unknown keys, не-bool `allow_create`/`subagents`,
не-string `id`, неизвестный `effort`, absolute paths, `..`, пустые `files`,
overlap между задачами (по файлам и по контрактам) и `concurrency < 1` падают до
импорта Codex и до любых трат.

Выход в stdout — JSON object. По умолчанию он остаётся полным и включает
результаты воркеров. С `--summary-stdout` stdout становится компактным:
`run_id`, `run_dir`, статусы, `codex`, `paths`, счётчики и postflight summary
без worker responses. Полный ledger пишется в свежий run_dir
(default `<project>/_workspace/codex-artifacts/<run_id>/`; `manifest.json`,
`events.jsonl`, `results.jsonl`, `result.json`) или в свежий `--run-dir PATH`;
существующий каталог считается ошибкой. Постфлайт scope-чек исключает сам
run_dir и его collapsed-предков (`_workspace/`) — своя площадка прогона не
считается правкой проекта.

### Контракт оркестрации (обязателен)

- **File-disjoint enforced.** Backend нормализует `files` и reject-ит overlap
  до запуска Codex. `files` — exact file paths, не directory/prefix scopes.
  Воркеру allowlist объявляется каналом `developer_instructions` его треда, а
  репликой уходит чистый `prompt` задачи; текст — объяснение рамки, enforcement
  остаётся на preflight/postflight. Сам текст и его длина фиксируются в
  `manifest.tasks[]` (`developer_instructions` / `developer_instructions_chars`)
  до первого хода — в `--dry-run` тоже, чтобы прогон был восстановим по run_dir.
- **Git safety fail-closed.** Реальный write-run требует рабочий git worktree.
  `--dry-run` может работать вне git, но помечает `git.available=false`.
- **Dirty-overlap gate + fingerprint snapshot.** По умолчанию запуск блокируется,
  если текущие dirty files пересекаются с `files` задач. Override:
  `--allow-dirty-overlap`. Все initial dirty files fingerprint-ятся; если
  воркер меняет любой non-allowlisted dirty file, `scope_status=failed`.
- **Scope-check после запуска.** Изменённые path fingerprints и смена `HEAD`
  проверяются после workers; changed files должны входить в union declared
  `files`, иначе `scope_status=failed`.
- **Verification отдельно.** `worker_status=completed` не равно done.
  `--verify CMD` даёт `verification_status=passed`; без verify статус
  `not_requested`, а `fully_verified=false`.
- **Worktree-изоляция по умолчанию.** `--isolation worktree` (default) заводит
  воркеру git worktree от HEAD под `~/.codex-bridge/worktrees/<run_id>/<task_id>`
  на ветке `codex-fleet/<run_id>/<task_id>`. Следствия: атрибуция считается в его
  дереве, запись вне allowlist в проект не попадает, а параллельная запись
  оркестратора в основное дерево волну не валит — она уходит информационным полем
  `wave.main_tree_drift`. `scope_status` в этом режиме строится по per-worker
  атрибуции и по успеху интеграции. `--isolation shared` — прежний режим с
  aggregate-чеком, для задач, которым нужно видеть правки друг друга; цена
  изоляции — выкладка рабочего дерева на воркера.
- **Ссылка наружу дерева работой не считается.** Симлинк вне allowlist, чей
  target лежит за пределами дерева воркера (типовой случай — `node_modules` на
  соседнее дерево вместо установки), вычитается из `changed_files` с заметкой:
  правило `.gitignore` с завершающим слэшем такой линк не ловит, и раньше он
  удерживал ВСЮ работу воркера как внесписочную запись. В ветку и в проект он не
  попадает — `commit_worker_tree` фиксирует ровно `changed_files`.
- **Закрытие волны в том же прогоне.** Собрать изменения → коммит в ветку
  воркера ВСЕГО изменённого (gitignored-мусор отсечён `--exclude-standard`;
  фиксация ≠ интеграция) → `merge --no-ff`, но только чистого воркера: упавший
  ход (`held_failed_worker`), внесписочная правка (`held_out_of_scope`) и
  конфликт остаются в ветке — merge несёт только файлы списка, потому что
  чистый воркер другого и не менял → снести деревья; ветки — только у
  merged/empty. Закоммиченная работа не удаляется никогда; неразобранное видно
  в `wave.kept_branches`, и `ok` падает. `--no-integrate` останавливается на
  коммитах в ветках и держит деревья, `--keep-worktrees` держит деревья при
  интеграции. Инвентарь и ручная уборка — готовым
  `git worktree list/remove/prune`; мост их не оборачивает.
- **Ярус на задачу.** `model`/`effort` в задаче побеждают `--model`/`--effort`
  прогона: `model` — во всех трёх точках движка (`thread_start`, `thread_resume`,
  `thread.turn`), `effort` — на ходе (`thread.turn`), там его и принимает SDK. Одна волна может быть разноярусной — пишущие
  на `gpt-5.6-luna`, судящие на `gpt-5.6-sol`, — и делить её на два запуска ради
  ярусов больше не нужно. Фактический ярус воркера пишется в `results.jsonl`
  (`model`, `effort`) и в `manifest.tasks[]`; `codex.model` манифеста и баннер
  остаются ярусом ПРОГОНА, поэтому баннер разноярусной волны дописывает
  `(свой ярус у …)`.
- **Смысловая зона задачи.** `contracts_changed` / `contracts_read` — свободные
  имена контрактов; backend режектит до траты волну, где один воркер меняет
  контракт, который другой меняет или читает. Сверка БУКВАЛЬНАЯ: это не замена
  файловому allowlist (тот опирается на существование пути и на постфлайт-диф), а
  добавочные ворота против тихого случая «файлов не делили, семантику разъехали».
  Молчание backend'а значит лишь, что сверять было нечего. Объявленные контракты
  уходят воркеру секцией `КОНТРАКТЫ` его `developer_instructions` — иначе о его
  смысловой зоне знал бы только preflight, а не он сам.
- **`--tree-setup "CMD"` — подготовка деревьев.** Свежий worktree несёт только
  версионированное, поэтому `npm test` и его родня падают в нём по среде — и у
  воркера, и в воротах `--verify`, которые идут по такому же свежему слитому
  дереву. Команда исполняется параллельно (лимит — `--concurrency`) в каждом
  дереве воркера и в интеграционном дереве перед проверкой, таймаут
  `TREE_SETUP_TIMEOUT_SEC` = 1200 с (по нему убивается вся группа процессов, а не
  одна оболочка). Полный лог всех деревьев — `run_dir/tree_setup.json`. Порядок
  значим: подготовка идёт ДО снимка `preexisting`, поэтому её артефакты не
  приписываются воркеру. Отменяют волну до первого оплаченного хода (`exit 2`,
  `result.json` не пишется) три случая: ненулевой exit, любое прерывание
  (Ctrl-C, SIGTERM, OSError) и подготовка, тронувшая файл ИЗ списка задачи —
  в таком файле работу воркера от кодогенерации уже не отличить, и вместо
  `held_dirty_birth` после полной оплаты волна отказывается до неё. Красная
  подготовка ИНТЕГРАЦИОННОГО дерева — это `verification_status: setup_failed` и
  `held_setup_failed` у воркеров, а не «проверка красная»: проверка не шла.
  Только с `--isolation worktree`: в shared воркеры уже в дереве проекта.
- **`subagents: true` в задаче.** Кладёт воркеру разрешение делить свою работу на
  собственных субагентов (движок молчит про них, пока явно не попросят).
  Осмысленно только в изолированном дереве — иначе его субагенты пишут в общее.
- **Треды воркеров персистентны** (`FLEET_THREAD_EPHEMERAL=False`, владелец
  2026-08-14): каждый воркер виден чатом в Codex Desktop — живой монитор его
  прогресса. `thread_id` — в `results.jsonl` и событии `worker_thread`.
  Audit-владельцем прогона остаётся run_dir.
- **Тред воркера уходит вместе со своим деревом.** «Проект» у Codex — это ПАПКА
  треда (в старте треда есть только `cwd`), а папка воркера одноразовая: после
  уборки в списке проектов оставалась карточка в никуда — замер 2026-08-18, 34 из
  34 тредов моста висели на снесённых деревьях, и список проектов владельца
  состоял из имён наших задач. Закрытие волны с уборкой архивирует их само
  (`wave.threads_orphaned` → `wave.threads_archived`; отказ движка — событие
  `thread_archive_failed`, волну не роняет). Архив обратим и снимается САМ:
  ремонтный круг штатно приходит к архивному треду, и `thread_resume` поднимает
  его перед повтором старта (событие `thread_unarchived`; ручной путь остался —
  `codex_threads.py unarchive THREAD_ID`). `--keep-worktrees` и `--no-integrate`
  держат и дерево, и тред: карточка рабочая, убирать нечего. `archive --stale`
  сюда не относится — он ходит по реестру диалогов, воркеров в нём нет.

## Карта кода

- `codex_review.py` / `codex_investigate.py` / `codex_orchestrate.py` — три
  входа по профилям выше.
- `codex_preflight.py` — `--doctor`: бесплатный снимок runtime (аккаунт,
  эффективный конфиг, наследуемый tier) плюс след моста снаружи.
- `codex_footprint.py` — локальный бесплатный скан следа моста СНАРУЖИ run_dir.
  Тесты, отчёт волны и `git worktree list` смотрят внутрь; эта грязь живёт в
  чужих системах и находится глазами владельца, а не прогоном. Считает треды
  моста на удалённых папках (каждый — карточка проекта в Codex в никуда) и
  мёртвые записи `[projects.*]` в `~/.codex/config.toml` (косметика, не чиним:
  правка живого конфига дороже мусора). Ничего не удаляет; уборка — отдельной
  названной командой `codex_threads.py archive --orphaned`, обратимой через
  `unarchive`. Фильтр по метке движка `originator`, а не по путям: чужие чаты
  владельца датчик не видит.
- `codex_recall.py` — один вызов глубокого recall по корпусу цитат владельца
  для Claude и Codex: владеет промптом, чтобы обе стороны спрашивали одинаково.
  Идёт ревьюером на `luna` + `xhigh`, без диалога.
- `cbcommon.py` — биллинг-гигиена; `codex_defaults.py` — runtime-дефолты;
  `codex_sdk_compat.py` — open-enum hardening; `codex_retry.py` — ретрай
  стартовых вызовов под перегрузкой и подъём архивного треда при resume.
- `codex_run_ledger.py` — журнал прогона (run_dir, события, пульс) + форма его
  артефактов: `prompt.md` и финал `result.json` (`RunResult`).
- `codex_git_scope.py` — снимок дерева и постфлайт-вердикт.
- `codex_progress.py` — живая активность хода + сводка `digest()`.
- `codex_orchestrate_contract.py` / `codex_threads.py` — контракт флота и
  реестр диалогов (`mine` — нативные треды движка, включая сессии владельца).

Пути в скиле `1codex` абсолютные и привязаны к расположению этого репо.
