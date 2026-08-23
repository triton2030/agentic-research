---
type: concept
title: Как устроены records ranking, card-only fallback и выдача --json?
description: Позиция владельца об устройстве ранжирующего поиска по цитатам с context-note, отдельном file-level маршруте session_candidates и раздельных lexical-маршрутах.
topic: chat-recall-retrieval
---
# Как устроены records ranking, card-only fallback и выдача --json?

`records` ranking ищет по цитатам и `context-note`; BM25 с dense rerank схлопывает выдачу до одного кандидата на файл. Когда существенного термина нет ни в цитатах, ни в `context-note`, но он есть в `session-context`, совпавшие карточки идут отдельным top-5 `session_candidates`, не меняя порядок `records`, а при пустом `records` служат fallback.

Card-only fallback с `--timeline` возвращает все записи найденных файлов; file-level карточка и rank только выбирают файл для полного чтения и не доказывают позицию владельца. `--json` отдаёт `address` для record-кандидатов и `session_candidates` для file-level маршрутов; без подготовленной модели `--lexical` сохраняет два раздельных lexical-маршрута. Acceptance проверяет ровно этот сценарий: термин только в `session-context`, файл показывается в top-5 `session_candidates`, порядок `records` не меняется.

## Устройство маршрутов

- Владелец решил, что `records` ranking ищет по цитатам и `context-note`, а BM25 с dense rerank схлопывает выдачу до одного кандидата на файл.
- Владелец решил, что при отсутствии существенного термина в `record-index` совпавшие карточки идут отдельным top-5 `session_candidates`, не меняя порядок `records`, а при пустом `records` служат fallback.
- Владелец решил, что card-only fallback с `--timeline` возвращает все записи найденных файлов, а file-level карточка и rank только выбирают файл для полного чтения и не доказывают позицию владельца.
- Владелец решил, что `--json` отдаёт `address` для record-кандидатов и `session_candidates` для file-level маршрутов, а без подготовленной модели `--lexical` сохраняет два раздельных lexical-маршрута.
- Владелец решил оставить `session-context` отдельным BM25 file-route с прежним novel-term gate либо минимум двумя совпавшими корнями; карточка не входит в `records`, E5 её не ранжирует, а card-only records пусты кроме timeline.

## Проверка

- Владелец решил включить в acceptance проверку, при которой существенный термин отсутствует в цитатах и `context-note`, но есть только в `session-context`, а default JSON показывает нужный файл в top-5 `session_candidates`, не меняя порядок `records`.

## Источники

- [решил: records ranking по цитатам и context-note; BM25+dense схлопывает до одного на файл](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L26)
- [решил: session_candidates top-5 без изменения порядка records; fallback при пустых records](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L26)
- [решил: card-only fallback с --timeline; карточка выбирает файл, не доказывает позицию](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L35)
- [решил: file-level rank только выбирает файл для чтения](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L35)
- [решил: --json address + session_candidates; --lexical два раздельных маршрута](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L26)
- [решил: session-context отдельный BM25 file-route, карточка не входит в records](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L35)
- [решил: acceptance-проверка термина только в session-context через top-5 session_candidates](../../../../../../../_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md#L26)
