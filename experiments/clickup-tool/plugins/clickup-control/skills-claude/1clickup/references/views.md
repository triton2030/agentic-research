# Task Views

Use for List, Board/Kanban, Table, Calendar, Gantt, Timeline, Workload,
Activity, Map, and Chat task Views. Dashboard, Doc, Form, and Whiteboard page
views are separate surfaces.

## Default Route

Prefer the named `view list/get/create/configure/tasks/delete` CLI commands or
their `clickup_control_*_view*` MCP equivalents. Use generic `api` only for a
current official View endpoint not represented by a named command.

Use `view tasks VIEW_ID --all` or `all_pages=true` for counts, comparisons, and
complete-set claims. A single page is a sample; ClickUp's View response does not
provide one stable page-size/termination contract across observed endpoints.
The named exhaustive route stops on `last_page`, an empty page, or a repeated
page and deduplicates by task ID.

Views can live at Workspace, Space, Folder, or List level. Create endpoints
currently advertise `list`, `board`, `calendar`, `table`, `timeline`,
`workload`, `activity`, `map`, `conversation`, and `gantt`. Re-check the current
endpoint contract for unusual types because the general Views guide lists
fewer types.

## Configure Contract

`PUT /v2/view/{view_id}` requires the complete writable configuration. The
named configure command therefore performs:

1. GET the current View.
2. Keep only `name`, `type`, `parent`, `grouping`, `divide`, `sorting`,
   `filters`, `columns`, `team_sidebar`, and `settings` for the PUT body.
3. Deep-merge the requested patch while preserving unknown nested settings.
4. PUT the complete configuration.
5. GET again and verify the normalized requested values.

Configuration readback is not enough when the outcome concerns which tasks are
visible. Also read all visible tasks and verify the expected IDs, count, or
task-type distribution.

Do not send response metadata such as ID, creator, timestamps, `orderindex`, or
protection/visibility fields. Do not hand-build a partial generic PUT.

The official OpenAPI schema incorrectly types some sorting/filter/column items
as strings while its examples and live responses use objects:

```json
{
  "sorting": {
    "fields": [
      {"field": "priority", "dir": 1, "idx": 0},
      {"field": "dueDate", "dir": 1, "idx": 1}
    ]
  },
  "columns": {
    "fields": [
      {"field": "assignee", "idx": 0, "width": 160, "hidden": false}
    ]
  }
}
```

Use `cf_<field_id>` for a Custom Field. Resolve its ID and applicable task
types first. Adding a Custom Field column to an Everything-level View can apply
that field across the Workspace, so verify the intended hierarchy level.

## Settings And UI Boundary

The API documents task locations, subtask display, parent names, closed
subtasks, assignees, images, empty-column collapse, and Me-mode options. Live
responses also contain visual keys such as `card_size`, `task_cover`,
`colored_columns`, and `show_empty_fields`. Preserve these during unrelated
updates. Change an undocumented key only after a disposable-View probe or use
the UI fallback.

The documented v3 ACL endpoint can update privacy and access for supported
objects, including Views. Sharing may incur charges and the public spec does
not expose a symmetric ACL read, so use it only for an explicit access request
with exact object/member IDs. If a charge is possible and not already
authorized, stop before the write. Treat the mutation response as API evidence,
then verify the visible access state through the UI; without that check, report
the ACL result as unverified rather than complete.

Use desktop/browser control for pinning, favorites, protection/default state,
Views Bar order, required Views, manual drag order, and visual settings that
cannot be safely verified through the API.

## Durable Manual Order

The Public API does not expose a reliable task drag-order mutation. When order
must remain programmable, use an applicable Number Custom Field such as `Rank`,
assign spaced values, and sort the View by `cf_<rank_field_id>` with a stable
secondary sort. Set values through the Custom Field endpoint, not Update Task.
Use UI drag-and-drop only for one-off visual movement.

Sources:

- https://developer.clickup.com/docs/views
- https://developer.clickup.com/reference/updateview
- https://developer.clickup.com/reference/getviewtasks
- https://developer.clickup.com/reference/publicpatchacl
- https://developer.clickup.com/openapi/clickup-api-v2-reference.json
