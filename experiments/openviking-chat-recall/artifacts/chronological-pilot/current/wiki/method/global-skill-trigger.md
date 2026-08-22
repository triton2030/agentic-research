---
type: method
title: Как устроить общий skill, чтобы его вызвали вовремя?
description: Порядок shaping общего skill через неожиданное правило, момент вызова и действие.
---

# Как устроить общий skill, чтобы его вызвали вовремя?

Общий skill должен работать для Claude, Codex и параллельных агентов. Оставь только неожиданное правило, которое агент сам не выведет. Description загружается всегда, поэтому прямо назови в нём момент вызова и действие; для Claude описание может следовать практикам Claude и отличаться от формулировки для ChatGPT.

## Steps

1. Назови ситуацию и действие в description. Для thinking/search companion явно скажи, что использовать его нужно, когда агент сомневается или не уверен, что поиск завершён.
2. Удали очевидный фон; оставь только важную дельту.
3. Для Claude и ChatGPT проверь разные практики; не копируй описание механически. Проверь чтение в Claude и Codex; если та же функция уже официально доступна в Codex, предпочтение официального skill условно.

## Check

Свежий читатель по description понимает, когда вызвать skill и что сделать. Global instruction говорит об owner-specific неизвестном и желаемом результате, а не перечисляет очевидный способ действия.

## Boundary

Убирай подозрительные строки, которые конфликтуют между собой. Не выводи из этой записи цель конкретной модели или влияние priority-флага на скорость.

## Sources

- [global skill scope](../../../../../../../_ops/chat-recall/2026-07-22-105500-claude-d8a832a4.md#L24)
- [Codex, Claude and parallel callers](../../../../../../../_ops/chat-recall/2026-07-22-111300-claude-37219ddd.md#L22)
- [short instruction preference](../../../../../../../_ops/chat-recall/2026-07-23-114721-claude-67208f21.md#L15)
- [description is always loaded](../../../../../../../_ops/chat-recall/2026-07-26-163521-claude-bddf1411.md#L15)
- [skills keep only the delta](../../../../../../../_ops/chat-recall/2026-07-26-163413-claude-2be60fdc.md#L21)
- [Claude and Codex applicability](../../../../../../../_ops/chat-recall/2026-07-26-180518-claude-fa590eea.md#L16)
- [official skill preference](../../../../../../../_ops/chat-recall/2026-07-26-180518-claude-fa590eea.md#L17)
- [Claude-specific description practices](../../../../../../../_ops/chat-recall/2026-07-27-175105-codex-019fa38f.md#L15)
- [thinking/search companion trigger](../../../../../../../_ops/chat-recall/2026-07-27-211730-claude-8e802437.md#L21)
- [owner-specific global instruction](../../../../../../../_ops/chat-recall/2026-07-29-000000-claude-068dc13d.md#L15)
- [remove conflicting instruction lines](../../../../../../../_ops/chat-recall/2026-07-29-000000-claude-068dc13d.md#L16)
