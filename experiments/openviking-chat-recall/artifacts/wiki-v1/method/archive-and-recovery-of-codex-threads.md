---
type: method
title: Когда архивировать Codex-ветки и как устроен recovery?
description: "Ветки архивируются после вызова 1codex-bg-threads, retained-ветку архивирует root при принятии зонтичной работы; recovery — через list_threads и unarchive."
topic: codex-background-threads
---
# Когда архивировать Codex-ветки и как устроен recovery?

По правилу владельца ветки архивируются после вызова `1codex-bg-threads`; root архивирует retained-ветку при принятии зонтичной работы, а до принятия — только по явному слову владельца. Правка самого скилла ограничена stable title, pin и recovery через `list_threads` и `unarchive` — queue, revert, Goal, Cloud и handoff исключены.

## Архивирование

- Владелец предложил как правило архивировать ветки после вызова `1codex-bg-threads`. [предложил архивировать ветки после вызова как правило](../../../../../_ops/chat-recall/2026-08-04-121600-codex-019fcb91.md#L17)
- Владелец решил, что root архивирует retained-ветку при принятии зонтичной работы, а до принятия — только по явному слову владельца. [решил: root архивирует retained-ветку при принятии зонтичной работы](../../../../../_ops/chat-recall/2026-08-11-002528-claude-5fcdde37.md#L16)

## Recovery и охват правки

- Владелец решил ограничить правку `1codex-bg-threads` stable title, pin и recovery через `list_threads` и `unarchive`, исключив queue, revert, Goal, Cloud и handoff. [решил ограничить правку title, pin и recovery](../../../../../_ops/chat-recall/2026-08-14-201110-codex-019fff9f.md#L17)

## Источники

- [предложил архивировать ветки после вызова как правило](../../../../../_ops/chat-recall/2026-08-04-121600-codex-019fcb91.md#L17)
- [решил: root архивирует retained-ветку при принятии зонтичной работы](../../../../../_ops/chat-recall/2026-08-11-002528-claude-5fcdde37.md#L16)
- [решил ограничить правку title, pin и recovery](../../../../../_ops/chat-recall/2026-08-14-201110-codex-019fff9f.md#L17)
