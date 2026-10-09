# codex-bridge

Вызов Codex (ChatGPT) из Claude Code. Зеркало `claude-bridge` (тот гоняет Claude
из Codex; этот — Codex из Claude).

Один вход — `codex_review.py` (короткая команда с витриной —
`codex_launch.py agent`). Codex работает в проекте как субагент Claude Code:
пишущее задание меняет файлы прямо в проекте, просьба проверить или ответить
оставляет их нетронутыми. Это правило в роли агента, а не песочница; первые
живые прогоны без неё — в разделе «Права и прежние замеры».

| Режим | Контекст и работа |
|---|---|
| `task` (по умолчанию) | Самодостаточное задание без транскрипта сессии. |
| `review` | Независимое ревью хода текущей сессии Claude по транскрипту; файлы не менять. |
| `ask` | Ответ на вопрос по транскрипту; файлы не менять. |
| `diff` | Нативный `review/start` движка по незакоммиченным правкам, ветке, коммиту или инструкции. |

Каждый обычный ход получает `full_access` + `deny_all`, cwd = проект. Мост не
ограничивает файлы и не сверяет последующие правки; границу держат задание и
общие правила роли. Опциональный `--scratch` даёт свежую APFS-копию проекта с
`workspace_write`: тесты и сборки пишут в копию, исходник не меняется. Копия
стоит времени (~30 с на 127 тыс. файлов, прежний замер) и удаляется после
хода. `--mode diff` с `--scratch` несовместим.

Общие правила моста запрещают перетирать чужие правки, применять git-откаты,
коммитить без просьбы и вызывать `claude-mcp`: `claude_ask` однажды оставил
прогон без ответа на девять часов (замер 2026-07-28). Отчёты и другие
непроектные файлы идут в `run_dir/out/`, если задание не указало иное.

Управляется глобальным скиллом **`1codex`** (`~/.claude/skills/1codex/`).

## Долгий прогон и витрина

Оплаченные вызовы Claude запускает фоновыми Bash-задачами: в foreground экран
замирает, а завершение фоновой задачи приходит одним уведомлением. Backend
пишет свежий `run_dir`, компактный stdout и результаты на диск. Для прямого
фонового запуска служат `--summary-stdout --run-dir PATH` (каталог должен быть
новым) и `--heartbeat-sec N` (`0` отключает heartbeat).

Владелец просил «чтобы в десктоп приложении я видел факт того что агенты
работают, типа как баш команды» (2026-08-24); карточка с длинным заданием
«выглядит мусорно» (2026-09-18). Для этого
`codex_launch.py agent --name ИМЯ --prompt-file ФАЙЛ --run-dir PATH -- АРГУМЕНТЫ` запускает
`codex_review.py` отдельным процессом, пишет его вывод в
`<RUN_DIR>.launch.log` и показывает `codex_watch.py watch RUN_DIR --pulse`:
модель, усилие, задание, текстовые сообщения Codex, сводки размышлений и
финал (владелец: «вижу его мысли … чисто его текстовые слова»). `--pulse-all`
в самом `codex_watch.py` добавляет команды и инструменты
для отладки. `codex_launch.py review` — прежний алиас того же входа.

`TaskStop` пересылает сигнал прогону и запрашивает штатный interrupt. Если
витрина закрылась по своему потолку времени, сам ход продолжается до
завершения; это сохраняет недоделанную пишущую работу от обрыва.

Ход использует `thread.turn()` + `stream()`. Активность и пульс пишутся в
`events.jsonl`; краткую сводку даёт `codex_progress.py RUN_DIR`. Реплика в
идущий ход через `--steer` попадает в `control.jsonl`; `--external` передаёт
чужой текст с правами инструмента, а собственное исправление курса идёт без
него. `steer_accepted` подтверждает приём, а смену курса показывают только
следующие шаги. Сторож работает отдельным потоком, потому что поток событий
может молчать минутами. Сквозной прогон 2026-08-16 принял реплику за секунду
и завершился по новой инструкции; после снятия песочницы повторного замера не
было.

```bash
.venv/bin/python codex_progress.py "$RUN_DIR" --tail 5
.venv/bin/python codex_progress.py "$RUN_DIR" --steer "Уточнение"
.venv/bin/python codex_progress.py "$RUN_DIR" --steer "Цитата" --external
```

Стартовые `thread_start`, `thread_resume` и `thread.turn` повторяются при
`server_overloaded` (до трёх попыток, событие `retry`); начавшийся поток не
повторяется, чтобы не оплатить ход дважды. Архивный диалог при `--continue`
мост поднимает и один раз повторяет старт; события `thread_unarchived` и
`thread_unarchive_failed` фиксируют исход.

## Аудит: `run_dir`

Единственный audit/debug owner прогона — явный `run_dir` внутри рабочей папки работы:
`<project>/_workspace/work-artifacts/<дата-тема>/agents/codex-artifacts/<стамп>-<имя>/`.
В нём находятся
`manifest.json`, `events.jsonl`, `prompt.md`, `result.json`, а после реального
хода — `final.md`; непроектные артефакты кладут в `out/`. `--run-dir PATH`
обязателен для launcher и прямого входа, в том числе `--dialog`, `--continue` и `--dry-run`.
Без него вход отказывает с кодом 2 до создания файлов и запуска Codex,
показывая шаблон пути выше. `--doctor` не запускает прогон и пути не требует.
Общая `<project>/_workspace/codex-artifacts/` больше не создаётся автоматически.
Только внутренний вызов ledger без проекта сохраняет fallback `codex-bridge/runs/`.
`prompt.md` содержит user-промпт и полную роль;
manifest учитывает длины обеих частей.

`codex_progress.py --board PROJECT` и `codex_watch.py look PROJECT` ищут прогоны по
`_workspace/work-artifacts/*/agents/codex-artifacts/*`, со свежими стампами сверху.
Явный путь вне этой схемы допустим; такой прогон смотрят по его `RUN_DIR`.

Обычные треды эфемерны и не появляются отдельными чатами в Codex Desktop.
`--dialog`/`--continue` создают персистентный тред ради resume. История Desktop
не заменяет `run_dir` как аудит; `~/.codex` остаётся общим хранилищем
аутентификации, конфигурации и движка. Поле `codex.thread_ephemeral` в
`result.json` показывает режим конкретного хода.

## Модель и runtime-доступ

Backend явно закрепляет Codex turn defaults: `model=gpt-6.1-sol`,
`effort=medium` — дефолт моста (`codex_defaults.py`). Модель и
effort не зависят от текущего `~/.codex/config.toml`; флаги `--model` и
`--effort` — осознанный выбор яруса под род работы. Service tier мост по
умолчанию НЕ шлёт (см. ниже).

Какой ярус брать по роду работы, решает скил `1codex` — его таблица ярусов
единственная; мосту принадлежит только дефолт в `codex_defaults.py`.

Под ChatGPT-биллингом работают не все слаги каталога: пробники 2026-07-10
отсекли `gpt-5.6-pro` и `gpt-5.6` (без суффикса) — `HTTP 400 — "not supported
when using Codex with a ChatGPT account"` (исторический probe 2026-07-02
аналогично отсёк `gpt-5.5-pro`). `gpt-6-astra` проверен живым пробником
2026-09-06 через `codex_review.py --model gpt-6-astra --effort medium`:
`status=completed`, `ok=true` (run `20260906T120214Z-4c9019f7`). `gpt-6-luna` проверен так же 2026-09-23
(`--model gpt-6-luna --effort low`, run `20260923T002234Z-luna6-probe`:
`completed`, `ok=true`), `gpt-6-sol` — пробником картинки ниже. Каталог
движка 0.155.0 (`~/.codex/models_cache.json`, снимок 2026-09-18) идёт в
порядке `gpt-5.6-sol`, `gpt-6-astra` («Our most capable model for complex,
demanding work», default effort `medium`), дальше `terra` / `luna`, `gpt-5.5`;
скрытыми (`visibility=hide`) — `gpt-reserve` («Fast and affordable»,
запасной ярус при исчерпании луны, `openai/codex#42372`) и
`codex-auto-review` (модель автоматического approval-ревью). `gpt-5.4-mini` и
`gpt-5.3-codex-spark`, которые прежний текст этого абзаца относил к каталогу
0.153.4, в снимке 0.155.0 отсутствуют. Снимок 2026-09-23 (движок 0.155.0-alpha.16)
открывается поколением 6: `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, дальше
скрытый `gpt-reserve`, прежние `gpt-5.6-sol` / `terra` / `luna`, `gpt-5.5` и
скрытый `codex-auto-review`. Дефолт усилия у
`gpt-5.6-sol` в каталоге — `low`, у `gpt-6-sol` — `medium`; мост шлёт усилие явно, а `--mode diff` берёт его из
`config.toml` (`medium`), так что на ярусы это не влияет. `luna` и `terra`
были проверены пробниками 2026-07-13. `terra` остаётся model-override внутренних
collaboration-субагентов движка, рекомендованного применения во внешних
вызовах не имеет; `md-scout` с 2026-09-23 работает на `gpt-6-luna`. Новую модель до штатного маршрута
проверяй тем же дешёвым пробником: каталог показывает наличие, а не доступ
под подпиской.

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
(`/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex`) — он
авто-обновляется вместе с приложением и потому идёт впереди любого пина. С
2026-09-26 (движок 0.158.0-alpha.2.1) приложение кладёт упакованный CLI:
`codex-cli/bin/codex` — sh-переходник на `../CodexCLI.app/Contents/MacOS/codex`,
рядом `codex-package.json`, `codex-resources/` и `codex-path/`. Прежний путь
`Resources/codex` исчез, мост молча ушёл на бандл SDK, и тот ответил
`gpt-6-sol` HTTP 400 для ChatGPT-аккаунта. Фактический движок
фиксируется в ledger: `codex_bin` + `binary_source` (`chatgpt-app` |
`sdk-bundle`) в блоке `codex` каждого manifest/result и в stderr-banner
(`binary=…`). До 2026-09-26 бинарь приложения был неполным пакетом, и
`codex agents` (обзор сессий на общем app-server-демоне) отвечал `this CLI has
no complete local package` (замер 2026-09-18). Упакованный CLI 0.158 его
открывает — только в настоящем терминале; первый запуск ставит демон в
`~/.codex/packages/app-server-daemon` (замер 2026-09-26). Треды моста идут
через собственный app-server SDK, и видны ли они в этом обзоре, не
проверялось. `codex doctor` и `codex debug` работают.

**Одно правило поиска движка для всех, кто зовёт Codex напрямую.** Сначала
`CODEX_BIN`, если задан; затем `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex`
— он обновляется вместе с приложением, а отстающий движок отвечает новым
моделям HTTP 400; затем `codex` из PATH. Путь всегда настоящий (`realpath`):
движок, запущенный через симлинк, не находит `codex-code-mode-host`, и падает
каждый вызов инструмента (`openai/codex#32495`, открыта); а песочница
`1design-review` пускает только папку найденного файла, поэтому `CODEX_BIN`
указывает на сам движок, не на скрипт-обёртку; для упакованного CLI приложения
песочница пускает весь пакет — корень с `codex-package.json`. В PATH этого Mac `codex` нет
(замер 2026-09-23). Правилу следуют:

| Вызывающий | Где |
|---|---|
| `1-max-review` | `skills/shared/1-max-review/portable/scripts/max_review.py`, `_codex_path` |
| `1folder-tree` | `skills/shared/1folder-tree/portable/scripts/check_tree.py` |
| md-scout | `md-tools/scripts/run_md_scout.py`, `resolve_codex` (плюс флаг `--codex`) |
| `1design-review` | `experiments/1design-review/scripts/run-clean-design-agent.sh` |
| `graphiti-codex` | `experiments/graphiti-codex/src/graphiti_codex/codex_llm.py`, `resolve_codex_binary` |

Мост — исключение по устройству: PATH он не читает, а его запас — движок из
SDK (`binary_source=sdk-bundle`). Новый инструмент, который зовёт Codex сам,
добавляется в эту таблицу или объясняет здесь же, почему ищет иначе.

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
`supported_reasoning_levels`) для `gpt-6-sol` и `gpt-6-astra` (как прежде для
`gpt-5.6-sol` и `gpt-5.6-terra`) даёт
`low → medium → high → xhigh → max → ultra`, где по его же описаниям:

- `max` — «Maximum reasoning depth for the hardest problems»;
- `ultra` — «Maximum reasoning **with automatic task delegation**».

То есть глубина одиночного прогона — это `max`, а `ultra` — та же глубина плюс
делегация внутренним субагентам. У `gpt-6-luna` (как у `gpt-5.6-luna`) потолок
`max`, и именно он —
штатное усилие лёгкого яруса («Луна Макс»). Дефолт моста — `medium` (решение
владельца 2026-09-06, сменило `xhigh` от 2026-08-14); остальные усилия — выбор
по ситуации, каталог не блокируется. Тред на любом усилии заводит только явный
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

**Историческая сверка с upstream 2026-09-01: тогда пин оставался `0.144.4`.** На PyPI вышел
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
десериализации) — оба open на дату сверки. Тогдашнее правило пина было: бампать на конкретную поломку.
Оно изменилось с бампом на `0.154.0` ниже.

Историческая сверка 2026-09-01: `_sandbox.py` тогда собирал
per-turn политику из пресета без `writable_roots`, `service_tier` по-прежнему реально уходит в
`ThreadStartParams` — в `sdk/python/docs/api-reference.md` его в сигнатуре
`thread_start` нет, но это неполнота доки, а не удаление параметра.

**Бамп пина на `0.154.0` (2026-09-18, решение владельца).** ChatGPT.app
обновил движок до `0.155.0-alpha.9.2` (стабильный `rust-v0.155.0` — 2026-09-17);
пробник на старом пине `0.144.4` поломки не показал (run
`20260918T175027Z-814e6400`, stderr без warning'ов шима —
`_workspace/codex-artifacts/audit-input-20260918/`). Пин подняли не из-за
поломки, а ради двух возможностей SDK `0.154.0` — `thread.read(include_turns)`
(документирован в API reference 0.154.0; `#44084` добавляет выбор истории при
resume/fork) и `ExternalMessage` (`#44086`) — и потому,
что с 0.155.0 Python-пакеты публикуются вслед за каждым стабильным CLI
(`#44067`): прежнее правило «бамп только на поломку» опиралось на отставание
SDK, которого больше нет. Новое правило — **бамп вслед за стабильным CLI,
когда движок ChatGPT.app его догнал**, с прогоном `tests/` (190 тестов прошли
на `0.154.0` без правок). Миграции `0.154.0`, проверенные по коду моста:
`HookMetadata.root` — hooks мост не трогает; типизированные notifications —
`.params` нигде не читается; attachment turn-handle (`#44400`) — все ходы моста
идут через `thread.turn()`, чей handle держит события с момента запроса;
единственный ручной `TurnHandle` (нативное ревью `--mode diff`) с 2026-09-18
регистрирует подписку ДО `review/start` тем же маршрутом `pending_turn` /
`prepare_turn`, что и `Thread.turn()`; остаток риска — события ОТДЕЛЬНОГО
review-треда, пришедшие до ответа RPC, роутер SDK не удерживает (аудит Astra
2026-09-19), закрыть это может только SDK. Открытых enum'ов 3 из
122 — шим остаётся. Что взято из `0.154.0`: `codex_threads.py history`
(`thread/read` с историей вместо rollout-файлов) и `--external` у реплики
(`ExternalMessage`, см. «Долгий прогон и витрина»).

**Бамп пина на `0.157.1` (2026-09-26) — по правилу выше.** Стабильный CLI
`0.157.1`, движок ChatGPT.app `0.158.0-alpha.2.1` его догнал. Для моста в
`0.155`–`0.157` ничего не удалено: снятый `thread/rollback` (`#44915`) мост не
вызывал. `tests/` прошли без правок (222), открытых enum'ов 3 из 127 — шим
остаётся; живой пробник `20260926T183238Z-probe-sdk-0157`.

**Бамп пина на `0.161.0` (2026-10-09) — по тому же правилу.** Движок
ChatGPT.app `0.162.0-alpha.2` догнал стабильный `0.161.0`, но не `0.162.0`
(вышел 2026-10-08), поэтому пин — `0.161.0`. Для моста в `0.158`–`0.161`
ничего не удалено; локальные треды перешли на постраничную историю
(`#47900`), а `codex_threads.py history` через `thread/read` на треде движка
0.162 работает. SDK сам открыл `CodexErrorInfoValue` (`#49806`): открытых
enum'ов 4 из 128 — шим остаётся. `tests/` прошли без правок (130), pyflakes
чист; живой пробник `20261009T1220-probe-sdk-0161` (`gpt-6-luna`/`low`,
`completed`, предупреждений шима нет).

Нижний рабочий порог — `low`, и он enforced: `--effort` ниже (`minimal`/`none`)
отсекается на валидации флагов (`REASONING_EFFORTS` в `codex_defaults.py`).
Причина: turn'у по умолчанию доступны инструменты (`web_search`/`image_gen`), и
Codex на `minimal` отвечает `HTTP 400 — "The following tools cannot be used with
reasoning.effort 'minimal': image_gen, web_search"` — валидация превращает этот
поздний runtime-фейл в мгновенный.

## Права и прежние замеры

Решение владельца 2026-09-27 сняло прежние профили прав: «Просто надо убрать
все эти ограничения. Сделать их более похожими на твоих субагентов. […] Будем
рассчитывать на то, что агенты будут слушаться слов». Теперь backend явно
задаёт `full_access` + `deny_all`; права не наследуются от Claude. Запись вне
проекта мост не отслеживает и не откатывает. Роль задаёт правило: при просьбе
проверить, ответить или посоветовать проектные файлы не менять.

Первые прогоны без песочницы, 2026-09-27. Два писателя параллельно
(`_workspace/codex-artifacts/20260927T100416Z-писатель-progress-watch`,
`…T100418Z-писатель-retry-threads`) остались в своих зонах; из 152 их команд
ни одной git-правки (checkout, reset, stash, commit) — только show, status,
diff. Оба вместе с кодом флота стёрли не-флотские причины в докстрингах, и
Claude вернул их по диффу (коммит `f2818ef2`): писателя проверяет дифф, а не
его отчёт. Три проверяющих скила с просьбой «файлы не меняй» не записали ни
одного файла (`…T101258Z`, `…T101259Z`, `…T101301Z`). Это пять случаев, а не
вероятность.

Решение владельца 2026-09-23 дать Codex интернет и больше пользы ценой меньшей
безопасности предшествовало снятию ограничений: «Все три и дать доступ в
интеренет, кодекс очень умная модель она ничего плохо делать не будет»[^loosen].
Исторический замер 2026-09-18: внутри прежней `workspace_write` песочницы
`curl` к `127.0.0.1`, `localhost` и `https://example.com` вернул exit 0 (run
`20260918T175500Z-c2add3dd`), хотя SDK сериализовал `networkAccess: false`.
Причина расхождения не выяснена. Прежний `open_sandbox_network()` открывал
сеть для песочниц; нынешний обычный ход использует `full_access`, а
`--scratch` остаётся в `workspace_write`. Нативный `diff` идёт через
`review/start`, который не принимает per-turn политику песочницы.

Исторический замер прежнего scope-check: во время пробника картинки Claude
правил `skills/claude/1codex/SKILL.md`, и проверка приписала эту правку
прогону Codex. Сам ход и картинка были в порядке. Этот механизм снят;
наблюдение объясняет, почему старый отказ не доказывал ошибку Codex.

[^loosen]: `_ops/chat-recall/2026-09-23-051553-claude-483a304e.md#recall-94036c7a45b24ae2aa0cbdeaa094b974`.

## Биллинг: ChatGPT-аккаунт

Перед запуском Codex `codex_review.py` вырезает из окружения
`OPENAI_API_KEY`, `CODEX_API_KEY`, `OPENAI_BASE_URL` через `cbcommon.py`, чтобы
случайная переменная не увела вызов на платный API. Лог подтверждает вычистку
переменных; сам ChatGPT-login backend не проверяет. Аутентификация берётся из
общего `codex login` (`auth_mode=chatgpt`). Это зеркало биллинг-гигиены
`claude-bridge`.

## Установка

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

SDK содержит запасной бинарь Codex и читает общий `~/.codex/auth.json`;
отдельный логин для моста не нужен.

## Вызов агента

Укажи папку моста и целевой проект независимо от текущей папки shell.
Для каждой команды прогона выбери новый `RUN_DIR`; команды ниже — отдельные примеры.
Каталог ещё не должен существовать. `--run-dir` передаётся launcher до `--`.

```bash
BRIDGE_DIR="/путь/к/agentic-research/experiments/codex-bridge"
PROJECT="/путь/к/целевому-проекту"
RUN_DIR="$PROJECT/_workspace/work-artifacts/2026-10-05-тема/agents/codex-artifacts/20261005T120000Z-имя"
# Задание без транскрипта — режим task по умолчанию:
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" "Сверь README с реальными флагами кода" --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --task "Исправь ошибку в parser.py" --run-dir "$RUN_DIR"

# Сессия Claude нужна режимам review и ask:
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --mode review --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --mode ask --question "Где дыра в подходе?" --run-dir "$RUN_DIR"

# Нативное ревью незакоммиченных изменений, ветки или коммита:
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --mode diff --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --mode diff --base main --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --mode diff --commit SHA --run-dir "$RUN_DIR"

# Проверки в копии; промпт без траты; бесплатная диагностика движка:
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" "Запусти тесты" --scratch --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" "Сверь документы" --dry-run --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" --doctor

# Диалог:
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" "ВОПРОС" --dialog --topic "Тема" --run-dir "$RUN_DIR"
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_review.py" --project "$PROJECT" "УТОЧНЕНИЕ" --continue THREAD_ID --run-dir "$RUN_DIR"

# Короткая карточка с витриной:
"$BRIDGE_DIR/.venv/bin/python" "$BRIDGE_DIR/codex_launch.py" agent --name readme --prompt-file /tmp/task.md --project "$PROJECT" --run-dir "$RUN_DIR" -- --model gpt-6.1-sol
```

Для запуска витрины `/tmp/task.md` должен заранее содержать задание. Режим
`task` не подхватывает транскрипт. `review` и `ask` ищут его по
`CLAUDE_CODE_SESSION_ID`, иначе берут свежайший `.jsonl` проекта в
`~/.claude/projects/`; при нескольких сессиях передай `--transcript` явно.
Рендер сохраняет реплики, сжимает вызовы инструментов и обрезает длинные
результаты. `--max-chars` ограничивает бюджет транскрипта.

Все режимы пишут `run_dir`. Роль `task`/`review`/`ask` и общие правила уходят
через `developer_instructions`, а задание остаётся user-промптом; в `diff`
роль не передаётся, контракт задаёт движок. Правила `review`/`ask` запрещают
правку файлов; право `full_access` при этом технически остаётся. `diff` не
принимает `--effort`: усилие наследуется из конфигурации движка. Поведение
`review`/`ask` при полном доступе после снятия песочницы не замерялось.

Диалог (`--dialog` / `--continue`) — исключение из ephemeral-дефолта: resume
работает только по rollout на диске (эфемерный тред → «no rollout found»,
проверено живыми пробниками 2026-07-12), поэтому диалоговые треды персистентны
и видны в Desktop-истории. Контракты:

- Свежий run_dir обязателен через `--run-dir` для каждого хода; ledger фиксирует
  `thread_id`, `thread_persistent`, `resumed_from_thread`, событие `thread`.
- Provenance и статусная доска: `--dialog` пишет в
  `~/.local/state/codex-bridge/dialog-threads/<SHA-256 канонического пути проекта>.jsonl` событие `start`
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
  Реестр переживает сессии и уборку рабочих папок; он отделён по пути проекта.
  Старый `dialog-threads.jsonl` автоматически не переносится. Прежний тред можно
  продолжить через `--continue THREAD_ID --continue-foreign --run-dir НОВЫЙ_RUN_DIR`:
  этот ход добавит его в новый реестр, сохранив записи уже начатых новых диалогов.
- Реестр моста знает только свои треды. Что вообще открыто у владельца
  (Codex Desktop, `codex` в терминале) — `codex_threads.py mine [--limit N]
  [--all-projects] [--json]`: нативный `thread_list` движка по общему store
  `~/.codex`, с именем, временем, cwd и веткой. Чтение, кредитов не тратит;
  продолжение такого треда — по-прежнему только через `--continue-foreign`.
- Переписка персистентного треда — `codex_threads.py history THREAD_ID
  [--last N] [--full] [--json]`: `thread/read` с историей ходов (SDK ≥ 0.154.0)
  вместо чтения `~/.codex/sessions/rollout-*.jsonl`. Writer-lock не берёт,
  кредитов не тратит; эфемерных тредов в store нет — их переписка только в
  `run_dir`.
- Пустой THREAD_ID (потерянная `$VAR`) — отказ с кодом 2, не молчаливый новый
  тред. `--dry-run` валидирует CLI/prompt/реестр, но НЕ существование треда
  (`resume_checked=false` в ledger).
- Права `full_access` + `deny_all` задаются и при resume; соблюдение словесной
  границы после снятия песочницы не замерялось. Реплика в `--continue` уходит
  как есть, без обёртки ролью в тексте: контекст уже в треде, а роль повторяется своим каналом
  (`developer_instructions` у `thread_resume`) — она идемпотентна.

## Картинки

Встроенный `image_gen` доступен в ходе; из-за его инструментов нижний порог
усилия — `low`. Движок хранит оригиналы в
`~/.codex/generated_images/<id треда>/`, а `collect_images` копирует их в
`run_dir/images/`. Если файла по `savedPath` нет, он использует PNG из base64
поля `result` (`openai/codex#40249`). `result.json` перечисляет `file`,
`saved_path` и `failure` для каждой картинки. Витрина отмечает генерацию 🖼.

Исторический пробник 2026-09-23 сгенерировал картинку прежним входом при
`read_only`; без развёртки SDK `AbsolutePathBuf` путь записался как `root='…'`,
но base64-запас сохранил изображение. Более ранние пробники:
`20260923T001119Z-image-probe` (`gpt-5.6-sol`) и
`20260923T002233Z-image-probe-gpt6` (`gpt-6-sol`). После снятия песочницы
генерацию живым прогоном не перемеряли.

## Панель Codex в Claude Code

`claude-mod/codex-runs/` — мод Claude Code: панель прогонов, история по клику и
кнопка «Codex N» в нижней строке. Он ничего не пишет в контекст Claude и
никого не будит — только показывает владельцу то, что отдают
`codex_watch.py look --json --session ID` и `codex_watch.py story RUN_DIR`.
«Прогоны этой сессии» — по полю `claude_session` в `manifest.json`, которое
пишет `codex_review.py` из `CLAUDE_CODE_SESSION_ID`.

Поля этих JSON — контракт с модом: их сверяет с `types/index.d.ts` тест
`test_json_fields_match_mod_types`. Переименовал поле — поправь типы мода.

Мод установлен для всех сессий из локального магазина
`claude-mod/.claude-plugin/marketplace.json` и живёт **копией** в кеше
плагинов. После правки мода подними `version` в его
`.claude-plugin/plugin.json` и выполни
`claude plugin marketplace update codex-bridge-mods && claude plugin update codex-runs@codex-bridge-mods`;
в открытой сессии — `/reload-plugins`. Тесты мода:
`claude plugin test claude-mod/codex-runs`.

## Карта кода

- `codex_review.py` — единственный вход, режимы и роли с общими правилами.
- `codex_launch.py`, `codex_watch.py` — короткая команда и витрина прогона.
- `codex_progress.py`, `codex_run_ledger.py` — активность, картинки, управление
  ходом и файлы аудита.
- `codex_defaults.py`, `codex_sdk_compat.py`, `codex_retry.py`, `cbcommon.py` —
  настройки движка, совместимость SDK, восстановление старта и биллинг.
- `codex_scratch.py` — копия проекта для `--scratch`.
- `codex_threads.py`, `codex_footprint.py`, `codex_preflight.py` — диалоги,
  след моста вне `run_dir` и `--doctor`. Скан следа ничего не удаляет;
  `archive --orphaned` — отдельная обратимая уборка тредов на удалённых папках.
- `codex_recall.py` — глубокий поиск цитат одним вызовом для Claude и Codex;
  принимает и передаёт обязательный `--run-dir` (кроме `--print-prompt`).

Пути в скиле `1codex` абсолютные и привязаны к расположению этого репо.
