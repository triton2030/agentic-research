---
description: "Compatibility and migration contract for moving from current md backend to md-tools-v2."
read-before-edit:
  - "[[current-skill-usage-map.md]]"
  - "[[public-capability-contract.md]]"
edit-after-edit:
  - "[[validation-and-release-gates.md]]"
  - "[[decision-log.md]]"
---
# Compatibility And Migration

v2 не имеет права требовать переписывания живых skills. Текущий backend
обслуживает Codex и Claude, поэтому миграция должна быть staged and
link-switch compatible.

## Compatibility Matrix

Каждая текущая возможность получает один статус:

| Статус | Значение |
|---|---|
| `keep` | имя и behavior остаются |
| `alias` | старое имя вызывает новую capability |
| `replace` | нужен documented migration path |
| `internal` | primitive больше не public, но покрыт public capability |
| `remove` | удаляется только после evidence, что skill-момент закрыт иначе |

## Что Нельзя Ломать Без Решения

- Installed Codex/Claude skills.
- Habitual workflows of `1md-navigator`, `1md-graph` and `1strategy`.
- MCP tool discovery and descriptions.
- Read-only / mutating / open-world annotations.
- Confirm-required behavior.
- Output shapes, которые читают skills or tests.
- Exit codes and error classes.
- Existing index behavior, если corpus уже warm.
- CLI fallback names used in skill text.
- `MD_NAVIGATOR_SCRIPT` / `MD_GRAPH_SCRIPT` path override behavior.

## Минимальный Migration Path

1. Characterization tests current backend.
2. Compatibility matrix per current tool.
3. v2 implementation behind separate folder.
4. Replay skill workflows against v1 and v2.
5. Switch backend link for one runtime at a time.
6. Keep old skill text working through server path, env vars or shim.
7. Rewrite skill docs only later, as cleanup, not as migration requirement.

## Priority Replay

Перед switch обязательно прогнать три привычных workflow набора:

- `1md-navigator`: orient -> search -> extract -> read-related -> audit probe.
- `1md-graph`: edit-context -> preflight -> impact -> changed -> check/scan.
- `1strategy`: search `_ops` -> extract -> read-related GOAL -> query decisions
  -> one-way door impact/preflight.
