---
description: >-
  Use after conflict checks to synchronize or retire one project-local 2*
  owner and its Claude/Codex projections.
---

# Синхронизировать локальный скил

- Разреши owner и обе проекции по реестру и применимым корневым инструкциям
  целевого проекта; если контракт владельца отсутствует, верни blocker, не
  создавая новый source tree.
- При создании или обновлении синхронизируй из owner-а `SKILL.md`,
  `references/`, `scripts/` и `assets/` в обе проекции и проверь их рекурсивное
  совпадение; различаться может только runtime-owned metadata вне этих
  поверхностей, например Codex `agents/openai.yaml`.
- При снятии подтверди отсутствие owner-а и обеих проекций.
- Верни адреса трёх поверхностей и прямой parity либо absence check.

Частичное состояние не является результатом.
