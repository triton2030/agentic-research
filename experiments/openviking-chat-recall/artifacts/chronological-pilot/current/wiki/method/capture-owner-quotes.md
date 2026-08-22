---
type: method
title: Как сохранить цитату владельца, чтобы её нашли позже?
description: Порядок записи речи владельца с исходной датой, границей окна и поисковыми метками.
---

# Как сохранить цитату владельца, чтобы её нашли позже?

Нужна именно речь владельца, а не вставленный текст или вывод агента. Сокращай удалением шума, сохраняя смысл. Используй этот метод и при handoff: новая передача должна сопровождаться отдельной chat-recall session.

## Steps

0. При handoff запусти chat-recall для того, что сказал владелец в этой сессии.
1. Сохрани owner speech в recall с исходной датой и адресом источника; старый чат не датируй заново.
2. Веди один файл на одно окно разговора: укажи writer, точное время и session ID; не переноси слова между окнами.
3. Пометь запись словами `type` и `topic`; topic делай близкой к предмету разговора. Текст субагента не owner evidence.

## Check

Перед сохранением проверь цепочку: слова владельца → дата и адрес → окно и session → метки. Если звено потеряно, запись не готова к поиску.

## Sources

- [literal owner speech and date](../../../../../../../_ops/chat-recall/2026-07-22-105500-claude-d8a832a4.md#L20)
- [owner speech rather than interpretation](../../../../../../../_ops/chat-recall/2026-07-22-105500-claude-d8a832a4.md#L21)
- [deletion-only shortening](../../../../../../../_ops/chat-recall/2026-07-22-105500-claude-d8a832a4.md#L22)
- [recall storage surface](../../../../../../../_ops/chat-recall/2026-07-22-105500-claude-d8a832a4.md#L23)
- [context otherwise forgotten](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L24)
- [instruction and topic classification](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L27)
- [writer and session metadata](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L28)
- [manual shortening of pasted blocks](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L29)
- [noise can fill context](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L30)
- [one window, one file](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L31)
- [subagents lack owner quotes](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L32)
- [searchable type and topic labels](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L33)
- [owner speech versus pasted text](../../../../../../../_ops/chat-recall/2026-07-22-121239-codex-019f889f.md#L16)
- [original date for an old chat](../../../../../../../_ops/chat-recall/2026-07-25-124728-codex-019f983d.md#L15)
- [granular discussion topics](../../../../../../../_ops/chat-recall/2026-07-26-174326-codex-019f9e61.md#L15)
- [handoff capture rule](../../../../../../../_ops/chat-recall/2026-07-26-190811-codex-019f9ec1.md#L15)
