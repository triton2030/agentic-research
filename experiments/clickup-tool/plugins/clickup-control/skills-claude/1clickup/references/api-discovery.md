# Adaptive API Discovery

Use when the requested ClickUp capability is missing from named tools, appears
new, or may have changed. Do not conclude that ClickUp cannot do something from
the installed MCP catalog alone.

Do not browse for every stable named operation. Re-run discovery when live tool
exposure disagrees with the skill, a documented payload fails, a response shape
drifts, the feature is plan-sensitive, or ClickUp has recently changed the
endpoint family.

## Discovery Order

1. Inspect the live official ClickUp MCP tools. In Claude Code the
   deferred-tool list is the live catalog; ToolSearch loads schemas. Prefer a
   typed tool when it directly owns the operation.
2. Run `clickup capabilities` and inspect the named `clickup-control` tools.
3. Search the internet, restricted to current official ClickUp developer/help
   documentation, for product semantics, plan/role limits, and the endpoint
   family.
4. Inspect the official v2/v3 OpenAPI request and response schemas. Record the
   documentation/update date when available. Compare examples with a read-only
   live GET because ClickUp schemas can drift from their examples.
5. Use the generic relative-path API for a documented JSON endpoint that has no
   named command. Resolve IDs and current values first, execute the requested
   operation, then re-read the affected object.
6. Use desktop/browser control only when the capability is absent from the
   public API or depends on UI state.

Primary discovery sources:

- https://developer.clickup.com/llms.txt
- https://developer.clickup.com/docs/open-api-spec
- https://developer.clickup.com/openapi/clickup-api-v2-reference.json
- https://developer.clickup.com/openapi/clickup-api-v3-reference.json
- https://developer.clickup.com/docs/mcp-tools
- https://help.clickup.com/

For technical claims, prefer those official sources over blogs or remembered
payloads. Never send credentials to documentation, search, or command
arguments; the local runtime owns authentication.

If the namespaced `clickup_control_*` tools are absent but the runtime exists,
do not conclude that the capability is unavailable. Use the stable launcher in
`api-recipes.md`, starting with `doctor --live`, `capabilities`, `workspaces`,
and a targeted read.

## Promotion Rule

Do not wrap every endpoint. Keep a capability on the generic API route when its
schema is straightforward and use is rare. Promote it to a named module only
when at least one is true:

- the operation is frequent;
- it needs read-modify-write, pagination, multipart, or multi-call verification;
- the official schema is misleading or unstable;
- a wrong payload has meaningful blast radius;
- repeated agent traces fail to discover or execute it correctly.

Do not use ClickUp's private browser network endpoints as a stable integration.
Live undocumented fields may inform a disposable probe, but they are not a
durable contract until a verified owner and fallback exist.

## Known Route Traps

- Update Task does not update existing Custom Field values; use the dedicated
  Set/Remove Custom Field Value endpoints.
- Task and View collections are paginated. Use exhaustive named reads before
  asserting totals, absence, equality between Views, or duplicate-free state.
- UI editors and filter panels can display local state that is not persisted.
  Verify comments, checklists, and View filters through their owning API reads.
- A human-readable done label can remain a custom non-closed status. Check the
  status `type` before testing closed-task behavior.
- Current v3 has a documented move-task endpoint with status and Custom Field
  mapping. Prefer it over stale FAQ claims that tasks cannot change home List.
- v3 ACL can change privacy/access for many object types, but sharing can incur
  charges and the spec has no symmetric public ACL read. Require explicit cost
  authorization when applicable, then verify visible access through the UI.
- Generic JSON cannot upload multipart files. Use official MCP for task
  attachments. Re-check the incomplete v3 multipart schema before attempting a
  File Custom Field upload. If no typed route exists, use the ClickUp UI to
  upload into the target task's File field, reload the task, and verify the
  displayed filename before declaring completion.
