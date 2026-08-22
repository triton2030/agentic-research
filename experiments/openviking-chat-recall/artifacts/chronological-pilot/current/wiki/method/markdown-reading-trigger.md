---
type: method
title: Как сделать скилл чтения Markdown находимым и полезным?
description: Trigger и практическое использование Markdown-reading skill с явной границей неизвестного порядка инструментов.
---

# Как сделать скилл чтения Markdown находимым и полезным?

Используй метод, когда в проекте есть Markdown-файлы. Скилл должен сразу объяснять маршрут и пользу, чтобы агент не принял его за необязательное указание.

## Steps

1. Trigger 1md-read whenever project Markdown files are present.
2. Дай практический порядок запуска инструментов и укажи, какой чаще полезен, а какой реже; точный порядок в этих records не установлен.
3. Объясни, почему маршрут помогает цели агента, а не только перечисляй команды.
4. Во время использования проверь собственную полезность: устаревшие или мешающие строки пометь для переформулировки.

## Check

Fresh reader понимает, когда вызвать skill, какую пользу он получает и с чего начать; неизвестный ranking инструментов не подменён догадкой.

## Boundary

Этот draft устанавливает trigger и experience, но не выбирает единственный инструментальный порядок.

## Sources

- [always read Markdown through 1md-read](../../../../../../../_ops/chat-recall/2026-07-29-000000-claude-a9f0f34a.md#L17)
- [practical tool sequence](../../../../../../../_ops/chat-recall/2026-07-30-125453-codex-019fb200.md#L17)
- [self-review for stale skill text](../../../../../../../_ops/chat-recall/2026-07-30-125453-codex-019fb200.md#L18)
- [explain why the skill helps](../../../../../../../_ops/chat-recall/2026-07-30-125453-codex-019fb200.md#L19)
- [trigger whenever Markdown exists](../../../../../../../_ops/chat-recall/2026-07-30-125453-codex-019fb200.md#L20)
