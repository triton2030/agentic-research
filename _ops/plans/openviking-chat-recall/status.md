---
эпик: "самостоятельный experiment: openviking-chat-recall"
план: "[[task|Библиотека знаний из chat-recall]]"
состояние: 🔨 в работе
режим: Execution
вех-готово: 3
вех-всего: 6
обновлено: 2026-08-25
kind: status
---

# Статус — библиотека знаний из chat-recall

## Next

**MAVO-слой не принят.** Снимок коммита `e6ccc3e0` содержал 173 raw-holder-а
и 1807 typed records. После обязательной capture текущей коррекции live-слой
содержит 174 raw-holder-а, 1808 typed records, 20 tracked topic-файлов и 16
непустых тем. Четыре файла остаются пустыми:
`agent-surfaces`, `goals-and-priorities`, `planning-system`, `pricing`.
`horizon.json` и `reconcile-noops.json` отсутствуют.

Снимочный `check_topics.py` даёт ноль проблем, но current denominator шире
его карты. Read-only сверка живого корпуса дала 1791 уникальный topic-anchor,
47 current records без topic-effect, 30 якорей не на typed record и 23
source-anchor-а одновременно в активной части и в `## Отменено`.
`chat_digest.py` использует другой parser и считает больше records; разницу
parser-ов надо закрыть отдельным falsifying check, а не выбором удобного
знаменателя.

Существующий pipeline тоже не терминален:

- MAVO merge: построено 16, запущено 12, принято штатным `wave.py` 10;
  semantic `wave_ready.py` с явными `tasks`, `runs`, `good` и `--flat`
  принимает только 5 из 16, но сейчас всегда возвращает exit 0; пока checker
  не падает на неполной волне, он diagnostic, а не barrier;
- retopic: построено 169, запущено 0, принято 0; live raw/task set имеет пять
  пропусков, а каталог содержит 16 topic-id против 20 live topic-файлов;
- `build_update_tasks.py`, `apply_update.py`, `reanchor.py` и соседние
  post-retopic инструменты ещё не доказаны на внешнем project root;
- существующие focused update-tests не доказывают full MAVO path, retopic с
  двадцатью темами и matched semantic acceptance.

Discriminating merge-check запускается из корня `agentic-research`:

```bash
python3 experiments/openviking-chat-recall/scripts/wave_ready.py \
  _workspace/ox-mavo-merge/tasks \
  _workspace/ox-mavo-merge/runs \
  _workspace/ox-mavo-merge/good \
  --flat=experiments/openviking-chat-recall/artifacts/mavo-short2/flat
```

Порядок продолжения — по dependency seam, без ручной правки generated текста:

1. сделать semantic `wave_ready.py` fail-closed, параметризировать и покрыть
   falsifying tests external-root маршруты update/coverage/reanchor/horizon и
   gap записей без `topic`;
2. закрыть либо заново принять merge всех 20 current тем; пустой stub не
   считается темой;
3. пересобрать retopic-задания по current 174-holder corpus и 20-topic catalog,
   выполнить Luna/max, применить только поле `topic` и frontmatter inventory;
4. восстановить якоря deterministic writer-ом и повторить current coverage;
5. добрать append-only records, corrections провести typed
   `topic_reconcile.py`, evidence-backed no-op записать helper-ом;
6. записать `horizon.json` только после нулевого backlog;
7. провести matched blind acceptance против действующего `1chat-recall`, а не
   против голой папки;
8. отдельным cold-start прогоном доказать, что свежий агент по triad
   `task.md` · `context.md` · `status.md` восстанавливает owner-маршрут,
   следующий шаг и stop predicate, не читая `HISTORY.md`/`modules/**` как
   current instruction. До этого план и MAVO-слой не терминальны.

Опоры маршрута: `experiments/openviking-chat-recall/{PROTOCOL,RUNBOOK}.md`,
`scripts/{wave,wave_ready,build_retopic_tasks,apply_retopic}.py`; MAVO boundary —
`_ops/chat-recall/AGENTS.md` того проекта. Следующий observable result —
fail-closed semantic gate, external-root tests и regenerated manifests, после
которых Luna получает писательские задания с непересекающимися outputs.

Wave 1 от 2026-08-25 — **candidate, не accepted**:

- `wave_ready.py`: focused CLI 4/4; current MAVO merge даёт 5/16 и exit 1;
- update/coverage/horizon: 15/15 на temporary foreign roots;
- retopic/reanchor: 6/6 на temporary foreign root, static checks чисты.

Первый independent acceptance вернул **FAIL**: ephemeral foreign-root probe
дал две delta-records, покрылась одна, но `apply_update.py` вернул exit 0.
Owner добавил barrier до dry/write и subprocess regression; повторная приёмка
дала 26/26, partial delta exit 1 и byte-identical temporary roots. Шаг 1
принят. Current MAVO merge остаётся 5/16 и exit 1: это блокирует `apply_stage`
и любые записи MAVO, но разрешает построение и выполнение недостающих merge
tasks только в новом external `_workspace` до 16/16. Legacy `--help` probe во
время волны оказался рабочим запуском:
созданная им папка удалена, tracked `coverage-gaps.tsv` восстановлен byte-exact
из доказанного clean HEAD. Preexisting dirty `update-delta.json` и untracked
`update-repair-pending.json` были перезаписаны, а их прежние bytes не сохранились;
оба артефакта invalidated и должны быть пересобраны штатным writer-ом, не
приняты и не восстановлены догадкой.

## Свидетельства и статус

Подтверждено замером:

- **приёмка поиском закрыта.** Пятнадцать вопросов, четыре маршрута, слепой
  судья. Слой тем: 12 верных, 0 уверенно-неверных, 1 файл на вопрос. Штатный
  поиск `1chat-recall` и голая папка: 12 верных, 1 неверный, 3 файла. Библиотека
  из 367 страниц: 10 верных, 3 уверенно-неверных, 2 файла;
- **аудит смысла закрыт по всем 40 темам:** 113 расхождений найдено, 95 правок
  применено точной заменой, четыре структурные разведены по страницам;
- **покрытие корпуса** на момент сборки: 1191 запись из 1207 учтена — на месте
  либо названа не несущей знания;
- **перенос на чужой корпус** дошёл до конца конвейера: `kumysbekov`, 26 файлов,
  7 тем, 96,3% записей;
- **ссылки** открываются и чинятся сами по отпечатку записи.

Опровергнуто и снято:

- **письмо страниц и указатель.** Проиграли слою, из которого собирались.
  Механизм назван: страница режет тему и теряет соседний контекст, а модель
  дописывает связность. Снято из протокола 2026-08-24;
- **утверждение «разница не в корпусе»** про потери стадии 1 — собственный
  фальсификатор его не подтвердил: обвязка объясняет 60% потери, остальное
  суждение модели.

Закрыто 2026-08-24:

- **первое обновление слоя доведено до конца.** Две волны, 226 + 14 записей
  дельты; пересборка дельты после вливания даёт **0 разговоров, 0 записей** —
  слой впервые догнал корпус;
- **стадия назначения темы построена и пройдена.** Её не существовало, и на
  разговорах без темы стояла половина первой дельты: 11 разговоров, одна новая
  тема `claude-config`. Судит прогон по границам сорока тем, кладёт скрипт;
- **ревизия инструкций закрыта по всем 40 темам** — разница волны пуста. В один
  документ по-прежнему не сведена;
- **слой переехал** в `_ops/chat-recall/topics/` соседом корпуса, с собственным
  `AGENTS.md`; корневая инструкция получила маршрут к нему;
- **горизонт стал командой** `set_horizon.py`: 1336 записей, 207 разговоров,
  41 тема, 1340 якорей в слое;
- **контейнер собран по слову владельца:** `_ops/chat-recall/{raw,topics}` с
  одним `AGENTS.md` и `CLAUDE.md`; скрипты мастерской, скил и репо-инструкции
  переведены на новые пути; `chat_capture.py`/`chat_digest.py` адаптивны —
  в проектах с плоской `_ops/chat-recall/` работают как раньше;
- **словарь тем записи освобождён:** тема выбирается из существующих в корпусе
  (`--list-metadata` печатает их с частотами), новая — только осознанным
  `--new-topic`; читающая сторона принимает свободные темы без диагностики.
  Тесты обеих семей зелёные (Claude 82, Codex 83).

Закрыто 2026-08-24 (перенос на mavo-short2):

- **три шва конвейера чинились по ходу переноса**, каждый ронял честные
  прогоны: `apply_flatten` не снимал ```-забор, `apply_topicmap` падал от
  строки-шапки перед таблицей, `build_retopic_tasks` требовал у темы поле
  `why`, которого у свежей карты нет по построению;
- **стадия переразметки стала переносимой**: `build_retopic_tasks.py` и
  `apply_retopic.py` принимают папку реплик и каталог тем аргументами;
- **круг повторов защищает принятое**: `_workspace/ox-mavo-merge/grind.sh`
  переносит принятый прогон в `good/` до пересчёта остатка. Причина — RUNBOOK
  предупреждал, что волна пишет поверх задания, а измерять готовность размером
  файла нельзя: пустая квитанция весит столько же, сколько короткий ответ.

Открыто:

- **проверки и починки смотрели на снятую ветку.** `check_coverage.py` выносила
  вердикт по страницам — исправлено; `build_drift_tasks.py` читал страницы и
  только их форму якоря — исправлено; `apply_repair.py`, `apply_split.py`,
  `apply_backfill.py` **пишут в `wiki-v1` до сих пор** — помечено в RUNBOOK,
  находка `_ops/findings/2026-08-24-021559-72466-12839.md`;
- **провенанс слияния не доказан:** починенный `check_topics.py` даёт 13
  расхождений, в `openviking-wiki` потеряно 12 якорей из 47 —
  `_ops/findings/2026-08-24-021254-67547-6397.md`;
- **инструкции проверены холодными читателями** (четыре рукава Codex,
  2026-08-24). Писатель вернул «не-готов» с шестью догадками — все закрыты;
  повторный прогон по починенным файлам разбирается;
- карта тем `artifacts/flatten-v1/topics.json` узнаёт новые темы только от
  стадии назначения; темы, рождённые capture-ом через `--new-topic`, в неё не
  попадают до выверки при следующем обновлении слоя;
- current продуктовая рамка `skills/shared/1chat-recall/product-frame.md`
  называет `topics` производной картой над raw. Внешняя мастерская остаётся
  compiler-механикой, а не вторым reader-store; этот seam считается закрытым
  только когда foreign-root test доказывает запись в MAVO через штатный writer
  и отсутствие второй читающей правды.
