# Повторный вход в retained thread

## Цель

Переиспользовать прогретый тематический контекст, не подменяя им текущую правду
и не создавая дубликат specialist-а.

Открывай перед новым запросом к retained thread и перед ответом specialist-а.

- Единственный прежний `threadId` доказывается live list/read evidence.
- Archived candidate сначала unarchive и снова verify.
- Retained thread остаётся unpinned.
- Source resolver заново находит current authority.
- Relation `same` разрешает использовать cache.
- Relation `delta` требует прочитать изменения и затронутые зависимости.
- Replacement переиндексирует affected scope.
- Source conflict блокирует только зависимый claim.
- После compaction восстанови effective `THREAD_CARD` и source basis.
- Невосстановимый source basis требует re-ingest.
- Replacement запрещён, пока прежний identity не разрешён.
