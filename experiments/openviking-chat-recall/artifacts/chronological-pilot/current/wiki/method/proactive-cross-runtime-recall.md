---
type: method
title: Как использовать прошлые owner quotes в Claude и Codex?
description: Proactive retrieval of shared owner-quote context across Claude and Codex.
---

# Как использовать прошлые owner quotes в Claude и Codex?

Используй метод перед решением, которому нужен контекст владельца; не жди отдельного вопроса о том, что он говорил. Recall — дополнительный источник важного контекста.

## Steps

1. Явно держи в global instruction или skill маршрут к чтению owner quotes.
2. Когда контекст релевантен, прочитай recall proactively, а не только после прямого запроса.
3. Claude и Codex читают общий quote store и записи друг друга; retrieval не ограничивай файлами, созданными только текущим runtime.

## Check

Перед действием retrieval scope включает relevant records обоих runtimes, а не только собственные записи.

## Boundary

Этот метод задаёт retrieval behavior; формат capture и автоматическая currentness старой записи остаются отдельными правилами.

## Sources

- [make owner-quote recall explicit in global instruction](../../../../../../../_ops/chat-recall/2026-07-29-000000-claude-a9f0f34a.md#L18)
- [use recall proactively as context](../../../../../../../_ops/chat-recall/2026-07-29-000000-claude-a9f0f34a.md#L19)
- [Claude and Codex read each other's records](../../../../../../../_ops/chat-recall/2026-07-29-201707-codex-019fae73.md#L15)
