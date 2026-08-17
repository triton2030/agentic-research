# Evidence — session-context, 2026-08-14

## Реальный корпус

- Backfill-снимок содержал 142 session holder-а и 140 уникальных session ID. Для
  него прочитаны до конца 139 завершённых transcript: 83 Codex rollout и 56
  Claude JSONL; текущая 140-я сессия велась из live transcript.
- После backfill обычный capture создал ещё два holder-а. Финальный corpus
  содержит 144 holder-а и 142 session ID; в каждом holder-е ровно одна
  однострочная `session-context`.
- Две пары duplicate holder-ов получили одинаковую карточку своей общей
  сессии. Исторические quote-records не переписаны: текущий diff 140
  исторических holder-ов меняет только frontmatter; тело меняется лишь у
  текущей сессии через обычный capture.

## Отброшенные маршруты

- Повтор одной file-card в каждом record испортил real-corpus hybrid `hit@5` с
  `0.70` до `0.55`; ablation без карточек вернула `0.70`.
- File-level RRF, складывающий evidence разных quote одной сессии, также дал
  `0.55`: общий файл не означает один общий тезис.
- Card fallback только при полностью пустом record lexical оказался почти
  мёртвым: на 20 pinned queries record-index дал хотя бы одно OR-совпадение во
  всех 20 случаях.

Superseded 2026-08-16: поэтому карточки не входят в record BM25 или embeddings.
Одна lexical card на файл образует отдельный `session_candidates`; маршрут
включается только по query-термину, отсутствующему во всём record-index, и не
переставляет `records`. При пустом `records` тот же маршрут становится fallback;
его `--timeline` разворачивает все записи выбранных файлов.

## Проверки

- Codex suite: 77 tests, `OK`; Claude suite: 76 tests, `OK`.
- Real mixed queries сохранили обычный record ranking и отдельно нашли gold
  session: `skillrouter инструкция`, `mantineprovider компоненты`,
  `skillsbench исследование`.
- Card-only `skillrouter` вернул нужный файл первым и как fallback record, и в
  `session_candidates`.
- Pinned 20-query regression после разделения маршрутов: lexical `hit@5=0.30`,
  hybrid `hit@5=0.70`, delta `+0.40`. Общий acceptance-порог `0.90` остаётся
  красным; эта возможность его не маскирует.
- Corpus check показывает 19 прежних diagnostics — duplicate holder и unmarked
  approximate. Число records не заморожено: параллельный обычный capture
  продолжал пополнять corpus во время аудита. `--check --strict` закономерно
  завершается с code 1.

## MAVO Russian-first probe, 2026-08-16

- Корпус: 123 holder-а; 93 metadata-only Russian-first перевода и три
  последующих source-grounded дополнения карточек.
- Слепой evaluator прочитал 20 исходных transcript, не видел
  `session-context` и не запускал retrieval.
- Старые английские карточки: BM25 top-5 3/20; Russian-first: 15/20;
  прежний novel-only gate: 1/20.
- Двухкорневой lexical admission: top-5 16/20 и 0/6 отсутствующих тем.
- E5 внутри admission-tier: тот же top-5 16/20, но точный p10 ухудшился
  с 1-го до 4-го места; поэтому карточный E5 удалён.
- Естественный quote-поиск на трёх свежих случаях дал ранги 6, 23 и 1:
  при `--limit 8` видимы два из трёх.
- В p19 назначенный gold не попал в top-5, но читатель, слепой к gold и
  ranking report, прочитал все пять holder-ов целиком и нашёл три прямо
  релевантных и два смежных. Single-gold остаётся retrieval-прокси, а не
  продуктовой приёмкой.

## Разделение record/file routes, 2026-08-17

- Воспроизводимая blind-20 фикстура:
  `tests/blind_mavo_short2_cases.json`. Её 20 holder-ов были выбраны, а source
  sessions прочитаны в Codex task `01a00846-8a4c-7791-9378-41208c55c0ed` до
  использования `session-context`; фикстура хранит точные natural queries и
  gold-файлы.
- Quote-only file retrieval на одном снимке из 1363 records: стартовый
  `5216879cf24a` и текущий код дали одинаковый hybrid `hit@5=0.60`,
  `hit@1=0.05`, `hit@10=0.65`, `mrr@10=0.271`. Проверка стартового кода
  воспроизводится тем же `evaluate_retrieval.py` через `--digest-script`.
- Текущий pinned agentic-research набор из 20 queries и 810 records:
  lexical `hit@5=0.30`, hybrid `hit@5=0.70`, `hit@1=0.45`,
  `mrr@10=0.540`; порог `0.70` пройден.
- Текущие suites: Codex 83 tests, Claude 80 tests, оба `OK`. Код runtime и
  его общие тесты между Codex и Claude byte-identical; Codex дополнительно
  владеет corpus-bound evaluator и blind fixture.
- Fresh-agent E2E открыл file-route одним четырёхкорневым повтором, прочитал
  выбранный holder от первой до последней строки и проверил более поздний
  holder. Отдельный natural+root absent-case дважды вернул пустые records,
  пустые session candidates и `selection=none`. Ещё один later-holder check
  обнаружил реальную более позднюю коррекцию Luna → Sol xhigh.
