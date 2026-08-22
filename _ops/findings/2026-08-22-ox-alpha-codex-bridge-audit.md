---
source: Ox Alpha (stealth/ox-alpha) via Hermes, session 20260822_074907_6de3a1
date: 2026-08-22
scope: experiments/codex-bridge, 16 модулей / 5324 строки
status: внешний аудит, находки C1/C2/verify/threads/LIGHT_CODEX_MODEL проверены первичкой
---

## 1. Карта системы

Единственный потребитель — агент, вызывающий модули как CLI. Три входа запускают Codex-ходы, остальные модули — инфраструктура вокруг них.

- `codex_review.py` (task/review/ask/diff) и `codex_investigate.py` — одиночные синхронные прогоны: парсер → валидация → `prepare_run_dir` → manifest/prompt.md → ленивый импорт SDK → `thread_start`/`thread_resume` (роль каналом `developer_instructions`) → `thread.turn()` → `codex_progress.run_turn` (tee потока нотификаций в ledger) → приёмка `TurnResult` → `RunResult.finish` (result.json + событие + stdout). Review отличается транскриптом, режимом diff (сырой RPC `review/start`) и реестром диалогов `dialog-threads.jsonl`.
- `codex_orchestrate.py` — асинхронный флот: `_plan_run` (вся валидация до денег) → `open_wave` (по worktree на воркера) → `_run_fleet`/`_run_one` (AsyncCodex, semaphore, результаты в `results.jsonl`) → `_assess_wave` (postflight-scope + `close_wave`: collect → commit ветки → merge, опционально через gate-дерево с `--verify`) → `_emit`.
- Состояние живёт на диске: `run_dir` (`<project>/_workspace/codex-artifacts/<run_id>/`) — единственный audit-owner (events.jsonl, manifest, prompt.md, result.json, results.jsonl); worktrees в `~/.codex-bridge/worktrees/<run_id>/`; персистентные треды — в store движка `~/.codex` (реестр диалогов у review, `results.jsonl.thread_id` у флота).
- Общие швы: `cbcommon.scrub_billing_env` (биллинг), `codex_sdk_compat.harden_sdk_enums` (дрейф enum-ов), `codex_retry` (ретрай только стартовых RPC), `codex_run_ledger` (журнал/финал), `codex_git_scope` (снимки/вердикт scope), `codex_orchestrate_contract` (схема задач + статус-предикаты), `codex_progress` (поток/пульс/steer-ящик), `codex_threads`/`codex_footprint`/`codex_preflight` — гигиена и диагностика без платных ходов.

## 2. Критические находки

**C1. Инвариант биллинга гарантирует только «нет ключей в env», а не «оплата подпиской» — проверка auth_mode существует, но ни один прогон её не вызывает.**
`cbcommon.py:16-25` вырезает лишь `OPENAI_API_KEY/CODEX_API_KEY/OPENAI_BASE_URL`; `codex_preflight.interpret` (`codex_preflight.py:124-141`) умеет заблокировать не-chatgpt аккаунт, но вызывается единственно вручную через `--doctor` (`codex_review.py:399-407`). `codex_orchestrate.py:815` и `codex_investigate.py:160` скрабят env и сразу запускают ходы без единого `account/read`. Сценарий: в `~/.codex` переключён auth на API-ключ (или конфиг-дрейф заведёт платный провайдер) — каждый прогон молча уходит на API-биллинг, ровно то, что инвариант называет дефектом максимальной тяжести. Чинить дёшево: оба RPC (`account/read`) бесплатны — перед первым `thread_start` в каждом входе звать `codex_preflight.check`/`interpret` и падать fail-closed при `mode != "chatgpt"`. (Не путать с честным caveats про service_tier в `codex_defaults.py:37-40` — там речь про тир, не про канал оплаты.)

**C2. Молчаливый ложный успех postflight в `--isolation shared`: запись воркера внутрь уже существовавшего untracked-каталога невидима.**
`codex_git_scope.py:111` снимает untracked через `ls-files --others --exclude-standard` без `-uall` — git сворачивает полностью untracked каталог в одну строку `dir/`, а `_filesystem_fingerprint` для каталога хеширует только режим (`codex_git_scope.py:151-152`). Если каталог существовал до прогона (initial-снимок уже содержит `dir/` с тем же отпечатком), любой файл, дописанный туда во время волны, не меняет ни одну пару отпечатков — `compare_scope` (`codex_git_scope.py:200-215`) молчит, `ok=true`. В shared-режиме это критично именно потому, что песочница `workspace_write` разрешает запись по всему проекту, и postflight — единственный детективный контроль файлового контракта. Ирония: в `codex_worktrees.py:129` тот же автор уже знает про `-uall`. Чинить одним словом: добавить `-uall` в третью команду `_dirty_repo_paths`.

**C3. Worktree-режим: работа воркера внутри preexisting-untracked-каталога уничтожается уборкой — не вливается и не сохраняется в ветке.**
`codex_worktrees.py:207` вычитает `preexisting` из changed («хук виноват, не воркер»), а `commit_worker_tree` стейджит только `changed_files` (`codex_worktrees.py:233`); `remove_worker_tree` сносит дерево `--force` (`codex_worktrees.py:318`). Если воркер (или его субагент, `subagents=True) написал файл внутрь каталога, загрязнённого post-checkout-хуку при создании дерева, эта правка не попадает ни в коммит ветки, ни в вердикт `held_*` — она молча гибнет со сносом дерева. Узкий триггер (нужен хук, создающий untracked-каталог, куда воркер тоже пишет), но класс ровно «потеря работы без следа»: ни merged, ни held, ни записи в notes. Минимальный фикс: при вычитании `preexisting` разворачивать свернутые каталоги (`-uall` уже даёт точные пути) и различать «файл, лежавший при рождении» от «файл, дописанный потом» по mtime/повторному статус-снимку.

## 3. Существенные находки

- `codex_orchestrate.py:375-383` — `run_verification` зовёт `subprocess.run(shell=True)` без таймаута. Зависшая команда проверки (типичный случай) вешает закрытие волны навсегда: воркер-ветки не закрываются, деревья висят, `result.json` не пишется. Нужен таймаут + честный статус `verify_timeout` и переход в held.
- `codex_codex_orchestrate.py` → `codex_orchestrate.py:906-907` — в shared-режиме `--verify` бежит ПОСЛЕ того, как воркеры уже записали изменения прямо в проект (мерджа нет — верифицировать нечего отдельно). Красная проверка не откатывает ничего: `ok=false` в отчёте, а проект уже изменён. Это осознанный legacy-режим, но расхождение с философией «проверка — ворота» стоит хотя бы предупреждения в баннере при `--isolation shared --verify`.
- `codex_progress.py:634-637` (и `653-656`) — при недоступности штатных сборщиков SDK `run_turn` молча падает на `handle.run()`: пропадают interrupt-по-сигналу (`_InterruptOnSignal` активен только на потоковом пути, `codex_progress.py:640`), доставка steer-реплик и весь журнал активности. Реплика из ящика остаётся «в ящике» навсегда при живом прогоне. Деградация намеренная, но она неотличима от нормального прогона — минимум одно stderr-предупреждение и событие `telemetry_degraded` в ledger.
- `codex_retry.py:71-99, 102-136` — ретрай оборачивает и `thread.turn` (старт хода). Если ход фактически начался, а соединение оборвалось ошибкой, которую `is_retryable_error` сочтёт повторяемой, повтор создаст второй оплаченный turn. Замысел («ретраится только старт», `codex_retry.py:8-11`) корректен лишь в меру семантики SDK-предиката — см. раздел 7.
- `codex_preflight.py:39-45` — `check()` не вызывает `scrub_billing_env()` сам, хотя поднимает движок; защита держится на дисциплине единственного вызывающего (`codex_review.py:402`). Один лишний вызов внутри закрывает вопрос навсегда — цена нулевая.
- `codex_threads.py:253` — фильтр `cwd.startswith(str(project_cwd))` без разделителя: проект `/a/b` подберёт треды `/a/bc`.
- `codex_threads.py:316-321` + `_archive_ids:354-358` — `archive --orphaned` берёт треды всех проектов из стора движка, а archive-события пишет в реестр ТЕКУЩЕГО проекта: provenance-реестр одного проекта получает события о чужих тредах.
- `codex_worktrees.py:444-445` — пустой `run_home` удаляется только если он пуст; при `tree_stuck` каталог уровня run_id остаётся навсегда (пустой после ручной разборки) — мелочь против заявленной «уборка не опция», но видимой строки об этом в отчёте нет.

## 4. Структурный диагноз

- **Дублирование приёмки одиночного хода.** `codex_review.py:655-855` и `codex_investigate.py:272-446` — почти одинаковые ~180 строк: config, heartbeat, thread_start, turn, run_turn, except-финиш, разбор `status/error/usage`, `final.md`, `ledger.finish`, печать. Расхождения уже плодятся (у review dry-run до scrub, у investigate после — `codex_review.py:587` vs `codex_investigate.py:160`). Минимальная перестройка: один `run_single_turn(config, thread_kwargs, prompt, accept)` в новом маленьком модуле рядом с `codex_run_ledger`, входы передают sandbox/approval/ephemeral и функцию приёмки.
- **Реестр диалогов живёт не там.** `codex_threads.py:35` импортирует приватные `_append_registry_event`/`_dialog_registry_path` из входа-ревьюера — борд-утилита зависит от entrypoint. Перенос этих трёх функций в `codex_run_ledger.py` (там уже живет «форма артефактов») убирает инверсию без нового файла.
- **`codex_orchestrate_contract.py` — общий контракт под чужим именем.** `UsageError` и статус-предикаты используют review/investigate/ledger (`codex_run_ledger.py:27`), не только оркестратор. Либо переименовать смысл («bridge contract»), либо `UsageError` переехать в `cbcommon`.
- **`codex_progress.py` — четыре ответственности** (tee-поток, пульс, steer-контрол-плейн, CLI-отчётность digest/board). Читатели у них разные (процесс прогона vs внешний агент); минимум — вынести `digest/board/_task_line/_steer_cli` в `codex_report`, оставив процессной половине только то, что импортируют входы.
- **Дубль фильтра «своё»**: `codex_git_scope.is_scope_noise:219` и локальное замыкание `_is_own_output` в `codex_investigate.py:358-380` решают одну задачу чуть разными правилами — унифицировать на первом.

## 5. Тесты

Закреплено крепко: SDK-контракты через фейки с sentinel-бинарем (ephemeral/sandbox/tier/канал роли — `test_codex_review.py:348-520`, `test_codex_investigate.py:152-247`); единственный сквозной НЕ-dry-run прогон main() орчестратора (`test_codex_orchestrate.py:595-659`); жизненный цикл worktree на настоящем git — хуки, конфликты, красный/зелёный gate, поздний коммит воркера, прерывание с rescue (`test_codex_worktrees.py` целиком); слышимый ретрай (`:1077-1114`); механизм и wiring enum-hardening (`test_codex_sdk_compat.py`); устойчивость телеметрии (`TelemetryResilienceTest`).

Ложное чувство покрытия:
1. Фейковый коллектор всегда возвращает `completed` — инвариант «провалившийся ход приходит исключением» (`codex_review.py:807-811`) держится на непроверенной вере в `_raise_for_failed_turn` SDK; ветка «failed-статус → исключение → except-финиш» не исполняется ни одним тестом.
2. `_watch_control_async` (`codex_progress.py:613-624`) не покрыт вообще — steer флота мёртвая зона.
3. Слепое пятно C2 не покрыто: тест «preexisting untracked dir + запись внутрь → out_of_scope» поймал бы дефект.
4. Rescue при прерывании тестируется с подменённым `_run_fleet` (`test_codex_orchestrate.py:780-784`) — реальная отмена `asyncio.gather` (потеря `results.jsonl`-записей незавершённых воркеров) не воспроизводится.
5. `render_transcript` и весь `codex_recall.py` не покрыты ничем — дрейф форм транскрипта Claude деградирует молча до пустого «диалога».

Самые ценные новые тесты: (1) сценарий C2 на `-uall`; (2) фейковый коллектор, поднимающий RuntimeError на `failed`, для обоих одиночных входов; (3) verify с бесконечным sleep → таймаут и held-вердикт; (4) async-доставка steer в живой ход флота; (5) fixture-тест `render_transcript` на замороженном образце настоящего session-jsonl.

## 6. Что удалить

- `codex_defaults.py:25` — `LIGHT_CODEX_MODEL` не используется ни одним модулем (проверено поиском по дереву).
- `codex_run_ledger.py:29,54-55` — legacy-ветка `BACKEND_DIR/"runs"` недостижима: все три входа всегда передают `project`; удалить вместе с константой и упростить сигнатуру.
- `codex_investigate.py:358-380` — локальный фильтр своей площадки заменяется `codex_git_scope.is_scope_noise` (минус ~20 строк дубля).
Больше кандидатов на цельное удаление не нашёл: код плотный, «мёртвых» веток почти нет — что само по себе диагностический факт (сложность здесь не в лишнем коде, а в размазанности).

## 7. Чего ты не смог проверить

- Ни один файл не исполнялся и тесты не запускались (граница аудита): «182 тестовые функции» — подсчет grep-ом по `tests/`, зелёность набора не подтверждена.
- Контракты SDK (`openai_codex.retry.retry_on_overload`, `errors.is_retryable_error`, `_run._raise_for_failed_turn`, `TurnHandle.steer`) выведены из комментариев и тестов моста; исходники SDK в `.venv/` я не читал — поэтому находка про двойную оплату при ретрае `thread.turn` (разд. 3) — риск по чтению, не установленный факт.
- `requirements.txt`, `README.md`, скилл `~/.claude/skills/1codex/` не открывал: версии пинов и обещания интерфейсов взяты из комментариев кода, а не из первички.
- Реальные формы ответов движка (`account/read`, `config/read`, `review/start`, `thread/list`, rollout-файлы) сверялись только с fixtures тестов; хрупкости вроде `path.stem[-36:]` (`codex_threads.py:220`) не проверены на живом store.
- Потокобезопасность одновременного `steer` из потока-сторожа и потребления потока нотификаций по одному TurnHandle; поведение при двух параллельных орчестрациях одного проекта; фактическое наличие `lsof`-локов `~/.codex/thread-writer-locks` — всё за пределами чтения.
- Раздел 2 (C2, C3) построен на семантике git (`ls-files` без `-uall` схлопывает untracked-каталоги) — уверенность высокая, но получена из знания git, а не из прогона сценариев.
