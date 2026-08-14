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

Поэтому карточки не входят в record BM25 или embeddings. Одна lexical card на
файл образует отдельный `session_candidates`; маршрут включается только по
query-термину, отсутствующему во всём record-index, и не переставляет
`records`. При пустом `records` тот же маршрут становится fallback; его
`--timeline` разворачивает все записи выбранных файлов.

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
