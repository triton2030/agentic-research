---
name: 1clickup
description: >
  Use when reading, organizing, or changing work in ClickUp. Choose the right
  object and live surface, complete the requested outcome, and verify it.
---

# ClickUp Control

## Outcome

Complete the requested ClickUp result through the strongest live surface while
preserving hierarchy, permissions, and user intent. Use the official OAuth MCP
for semantic search and common composites; use `clickup-control` for broader or
deterministic Public API work; use desktop/browser control only for UI-only
features.

Runtime owner:
`/Users/triton/Documents/GitHub/agentic-research/experiments/clickup-tool`.
Never read or print its token file. Invoke the stable launcher or namespaced MCP
tools; credential resolution belongs to the runtime.

## Default Path

1. Establish the target Workspace and requested outcome. When the user says
   broadly "put this in ClickUp", organize a workflow, or create a control
   system, read [work-model.md](references/work-model.md) before choosing an
   object. Do not default every result to a Task.
2. For hierarchy-sensitive
   work, rebuild parent/child truth from IDs instead of trusting visual nesting
   or aggregate `subtasks_count` alone.
3. Choose the surface from [routing-and-gaps.md](references/routing-and-gaps.md).
   Read it when the request crosses MCP/API/UI boundaries or depends on current
   tool coverage; do not preload it for an obvious single-tool action.
   If a capability is missing, new, or uncertain, read
   [api-discovery.md](references/api-discovery.md) and check current official
   docs/OpenAPI before concluding it is unavailable.
4. Read before write. Resolve exact IDs, valid statuses, field schemas, current
   values, and plan/permission limits before constructing a mutation.
5. Execute requested writes directly without asking for a separate preview or
   confirmation. For generic writes, pre-read the target when its identity or
   current state affects correctness. Keep mutations within the user's stated
   ClickUp outcome; do not invent unrelated cleanup or restructuring.
6. Verify by re-reading the changed object or recomputing the report. Distinguish
   API proof, inference, and any UI-only residual risk.

When deciding which workspace object or View type should represent the outcome,
consult [official-practices.md](references/official-practices.md). Do not load it
when the object and requested configuration are already explicit.

For task Views such as List, Board/Kanban, Table, Calendar, or Gantt, read
[views.md](references/views.md). It owns View discovery, creation,
configuration, visible-task reads, and the API/UI boundary. Prefer named View
commands over generic `api` calls.

## API Route

When a generic API route or launcher syntax is needed, read
[api-recipes.md](references/api-recipes.md). Named View work uses `views.md`
without also loading generic recipes. Use generic `api` only after checking the
current official endpoint contract; it exists to avoid a stale catalog, not to
guess undocumented paths.

## Stop

- Stop before any external mutation outside the user's requested ClickUp outcome.
- Stop and ask before a write that may create a charge or purchase unless the
  user explicitly authorized that cost.
- Stop when IDs, permissions, valid values, or target Workspace remain
  ambiguous after safe reads.
- Never send credentials through chat, command arguments, logs, plugin metadata,
  or task content.
