---
kind: module-card
волна: 5
роль: acceptance-lock-writer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — blind acceptance lock для distilled Wiki

## Outcome

До просмотра candidate Wiki зафиксировать JSON-контракт слепой приёмки,
который отличит полезное дистиллированное знание от гладкой historical ошибки.

## Оркестрация

- Сначала `$1orchestration`; внутренние субагенты независимо проектируют
  currentness, provenance/history и no-gold arms, затем ты дедуплицируешь их.
- Ты не один в кодовой базе. Не откатывай чужие правки и не читай/не меняй
  будущие `artifacts/distilled-wiki/**`.

## Ownership

Только:

- `experiments/openviking-chat-recall/artifacts/distilled-acceptance.json`.

Не менять никакие другие файлы. Один commit с этим JSON.

## Inputs

Прочитай полностью:

- `_ops/plans/openviking-chat-recall/task.md`;
- `_ops/plans/openviking-chat-recall/context.md`;
- `_ops/plans/openviking-chat-recall/modules/_returns/fresh-eyes-distilled-knowledge.md`;
- `_ops/chat-recall/2026-08-20-181330-claude-a7539038.md`;
- `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.

Не читай старые/generated Wiki pages при формулировке expected answers.

## JSON contract

Минимум пять locked cases:

1. stable knowledge;
2. superseded/current distinction;
3. contested или scope-dependent knowledge;
4. history/provenance request, который обязан маршрутизироваться к holder;
5. no-gold abstention.

Каждый case: stable ID, Russian question, allowed surface, expected semantic
criteria, forbidden claims, required source route, hard-failure conditions и
measurable read/context budget. Не копируй полный source quote в expected
answer; используй source record IDs/addresses.

## Return

Сделай один commit только ownership file. Верни `THREAD_DONE`: commit SHA,
case IDs, schema validation command, почему каждый case способен опровергнуть
candidate, UNKNOWN и nested-agent receipts.
