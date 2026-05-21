---
description: "Decision log for md-tools-v2 architecture and compatibility choices."
read-before-edit:
  - "[[minimum-document-set.md]]"
  - "[[compatibility-and-migration.md]]"
edit-after-edit: []
---
# Decision Log

Здесь фиксируются только решения, которые меняют архитектурную границу,
публичный контракт или миграционный путь.

## D-001 - Начать v2 с docs-first папки

Дата: 2026-05-22.

Решение: создать отдельную папку `experiments/md-tools-v2/` и сначала описать
минимальный набор документов для разработки сложного Markdown tools backend.

Причина: текущие `md_*` функции реально используются разными скилами в разных
моментах. Задача v2 - не удалить функции, а спроектировать более ясную систему
возможностей, границ, состояния и совместимости.

Следствие: код v2 не пишется, пока docs не закрывают usage map, jobs,
public capability contract, architecture boundaries, state/cost,
compatibility and validation gates.

## D-002 - Не переписывать skills как часть v2

Дата: 2026-05-22.

Решение: v2 переписывает backend-код так, чтобы текущие Codex/Claude skills
продолжили работать. Миграция должна сводиться к замене backend-ссылки,
MCP registration path, env vars or compatibility shim.

Причина: текущие skills используют `md_*` инструменты в разных рабочих
моментах. Переписывание skills смешает две задачи: улучшение backend
архитектуры и изменение agent workflows.

Следствие: перед кодом нужен `full-functionality-contract.md`, который
описывает весь функционал, ожидаемый текущими skills.

## D-003 - Приоритетная совместимость navigator / graph / strategy

Дата: 2026-05-22.

Решение: `1md-navigator`, `1md-graph` и `1strategy` являются priority
consumers v2. Их привычные workflows должны работать после замены backend
ссылки без правки skill bodies.

Причина: эти три скила задают основные способы использования Markdown tools:
navigation/search, graph evidence and strategy ground-check. Если они требуют
переучивания, v2 не является совместимой заменой.

Следствие: validation gates должны включать отдельный replay для этих трёх
скилов до любого runtime switch.
