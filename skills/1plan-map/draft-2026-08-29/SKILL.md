---
name: 1plan-map
description: >-
  Use when epic composition or map state is created, audited, or changed:
  derive epic topology from product truth and keep its dashboard current. Not
  for task admission or task files.
---

# Plan map — strategic truth and owner dashboard

## Unique Context

The owner follows the project through one map, not through task files or an
agent's retelling. The map is the durable strategic truth from current state to
`GOAL.md` Done: outcome epics, their order, frontier, evidence-backed state,
and the dashboard that makes the path visible.

## User Goals

- Product frames, principles, `GOAL.md`, and real carriers produce
  non-overlapping, commensurate outcome epics with explicit dependencies,
  order, frontier, and a reason for each position.
- The dashboard shows the path, blockers, deferred work, and accepted state
  without opening epics; closure and status come from carrier evidence.
- Composition changes are explicitly approved and remain visible, while state
  events preserve history and never silently rewrite composition.

## Behavior Protocol

> «скилл карты, это скилл карты планов, это скилл эпиков, и уже более
> детального работы и планирования верхнего уровня во всего проекта»

1. Read every applicable product frame and principle plus `GOAL.md`, then run
   `1use-principles`; no frames means `GOAL.md` is the source, while every epic
   names its principle files and a missing fit goes through `1product-shaping`
   or an explicit `нет принципа — <reason>`. Resolve the project instruction
   that owns the map root and instrument, creating that route only with the
   first substantive map.
2. Name the move before writing: composition creates, audits, splits, merges,
   reorders, or changes epic criteria; a state event only records accepted
   carrier evidence, status, updates, released blockers, and frontier state.
3. For composition, derive results, dependencies, risk order, external gates,
   and cross-cutting epics, show the exact change with its reason, and obtain
   the owner's approval; a state event cannot smuggle in composition.
4. Write only map-owned truth per [map-form](references/map-form.md) and the
   owner surface per [dashboard](references/dashboard.md); a frontier without
   a live task signals admission through `1planning`, never permission to
   create the task here.
5. Validate machine invariants with the project instrument; a divergence is a
   finding, `✅` requires accepted carrier evidence, and closed or deferred
   epics remain visible.

## Boundaries

Task admission and task-level decomposition belong to `1planning`. Task files
and routine execution belong to `1plan-task`; when they need an epic state
event, this skill owns that write.
