# ClickUp Control

Private ClickUp control plane shared by Codex and Claude:

- deterministic CLI over ClickUp's Public API with direct mutations;
- local stdio MCP server with namespaced tools;
- one shared `1clickup` workflow skill;
- dual Codex/Claude plugin manifests and marketplaces.

The official ClickUp OAuth connector remains the default for semantic workspace
search and common composite actions. This project owns broader deterministic API
work: hierarchy, task CRUD, Goals, checklists, Views, webhooks, reporting, and a
generic endpoint escape hatch. Desktop/browser control remains the
fallback for Automations, Dashboards, Whiteboards, and other UI-only areas.

## Setup

```bash
uv sync
chmod 600 api_key.md
bin/clickup doctor --live
```

Authentication lookup order: `CLICKUP_API_TOKEN`, macOS Keychain service
`agentic-research.clickup-control`, then ignored local `api_key.md`. Never commit
or paste the token into skill/plugin files.

## CLI

```bash
bin/clickup capabilities
bin/clickup workspaces
bin/clickup tree WORKSPACE_ID
bin/clickup task get TASK_ID
bin/clickup task search WORKSPACE_ID --include-closed --all
bin/clickup view list list LIST_ID
bin/clickup view configure VIEW_ID --patch '{"sorting":{"fields":[]}}'
bin/clickup view tasks VIEW_ID --all
bin/clickup audit portfolio WORKSPACE_ID LIST_ID
bin/clickup api GET /v2/team/WORKSPACE_ID/goal
```

Requested mutations execute immediately:

```bash
bin/clickup api POST /v2/list/LIST_ID/task --body '{"name":"Example"}'
```

The repository root is a dual-runtime marketplace with one MCP contract. The
skill is forked per host: Codex serves `skills/1clickup`, Claude serves
`skills-claude/1clickup` (same routing contract; host-specific triggers and
session notes). Mirror semantic fixes into both copies in each copy's own
wording; do not add duplicate global skill copies.

Named View commands own List/Board/Table lifecycle and full verified
read-modify-write. The generic API accepts any documented JSON request body so
new endpoints remain reachable without waiting for a wrapper.

`audit portfolio` is a read-only persistence check. It exhausts task and View
pages, reports structural gaps and unresolved checklist items, and can compare
the live report with a partial expected JSON manifest.

See `docs/capability-map.md` for the verified routing boundary.
