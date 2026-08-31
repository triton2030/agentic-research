# Review status — metadata-route candidate

## Exact input

- Codex: `14c7d18fcbb73d069711ba700bcd5267adf2c605ac3c21e849a9a5f77a22f913`.
- Claude: `503e0500dd5c0cacfa65a3f386249689cdfc1191c41e3f23e17b8d3ce3b78daf`.

## Independent-review boundary

Обе разрешённые владельцем волны независимых checker-ов завершились до этого
metadata repair. Их находки по сохранённым свойствам — provenance, date/age,
same-scope supersession, finite lock, deep JSON guard — остаются semantic
evidence, потому что соответствующие bytes и tests не менялись. Их terminal
PASS нельзя переносить на изменённые topic/session/context surfaces или на
новые package manifests.

Новая волна не запускалась: владелец прямо разрешил после двух волн проверять
только самому. Поэтому terminal review этой версии — self-verified candidate,
не independently approved candidate.

## Root decisions

- **Принято:** единый parser `topics.md` используется Capture и Retrieval.
  Иначе два parser-а могли бы расходиться по live/retired boundary.
- **Принято:** topic description имеет отдельный `topic_candidates` envelope,
  `topic_rank` и admission. Его score не смешивается с holder score.
- **Отклонено:** буквальное возвращение старого unbounded dense topic route.
  Clean falsifier показал бы topic для любого запроса; dense оставлен только
  re-ranker-ом lexical-admitted boundaries.
- **Отклонено:** восстановление per-topic Markdown summaries, reconciliation,
  horizons и derived facts. Это отменённый второй слой истины, не нужный для
  поиска по текущему `topics.md`.
- **Принято:** полный holder перед Capture и перед применением позиции, полный
  актуальный `session-context`, короткий keyword-like `context-note`, создание
  новой topic boundary только после чтения всей карты.
- **Принято:** не более одного неблокирующего background Retrieval для важной
  темы; это conditional branch, не новая стадия и не validation loop.

## Terminal verdict

`PASS AS SELF-VERIFIED CANDIDATE; EXACT OWNER APPROVAL REQUIRED.`

Незакрытый review gap один: новые manifests не видели независимые checker-ы из-за
исчерпанного owner-limit. Функциональных известных дефектов metadata-route после
112/112, 109/109 и clean corpus probes не осталось.
