# Architecture

## System Boundary

This project owns a private ClickUp Public API client, direct-write CLI, stdio
MCP server, and the `1clickup` skill distributed to Codex and Claude as
host-tuned forks. It complements ClickUp's official OAuth MCP and does not own
UI-only features.

## Runtime Entry Points

- `bin/clickup` starts the CLI through the project-pinned `uv` environment.
- `bin/clickup-mcp` starts the stdio MCP server used by both plugin runtimes.
- `plugins/clickup-control/.mcp.json` connects both plugins to that launcher.

## Ownership Map

| Concern | Owner | Responsibility |
|---|---|---|
| Credentials | `src/clickup_control/auth.py` | Resolve token without exposing it |
| HTTP/API | `src/clickup_control/client.py` | Validate paths, requests, errors and rate metadata |
| Mutation flow | `src/clickup_control/operations.py` | Execute requested API mutations directly |
| Task Views | `src/clickup_control/views.py` | Create, merge-configure, verify, query, and delete Views |
| Pagination | `src/clickup_control/pagination.py` | Exhaust task/View pages and deduplicate IDs |
| Portfolio audit | `src/clickup_control/audit.py` | Persistence report and expected-manifest comparison |
| CLI | `src/clickup_control/cli.py` | Stable human/skill-facing commands |
| Diagnostics | `src/clickup_control/diagnostics.py` | Redacted health summary |
| MCP | `src/clickup_control/mcp_server.py` | Thin typed tools over the same owners |
| Workflow | `plugins/clickup-control/skills/1clickup/SKILL.md` (Codex), `.../skills-claude/1clickup/SKILL.md` (Claude) | Route official MCP, API, and UI fallback |

## Main Flow

`Codex/Claude -> 1clickup -> official ClickUp MCP or clickup-control MCP/CLI ->
ClickUp Public API`. The client attaches credentials, normalizes JSON, surfaces
rate-limit metadata, and never logs the token. Requested mutations execute
directly; the agent resolves the target first when correctness depends on its
identity or current state, then verifies the result.

## Boundaries And Invariants

- API paths must be relative `/v2/...` or `/v3/...`; arbitrary hosts and path
  traversal are rejected.
- GET/HEAD/OPTIONS are read-only. Requested POST/PUT/PATCH/DELETE operations run
  directly without a second confirmation round.
- Credential lookup order is `CLICKUP_API_TOKEN`, macOS Keychain, then ignored
  local `api_key.md`.
- Named commands cover frequent work; generic JSON API tools keep new
  official endpoints reachable without duplicating the OpenAPI catalog. Generic
  request bodies may be any JSON value; query parameters remain JSON objects.
- View configuration is allowlisted read-modify-write: preserve unknown nested
  settings, omit response-only metadata, then re-read the requested patch.
- Exhaustive task reads stop safely on a declared last page, an empty page, or
  a repeated page; portfolio acceptance compares persisted state with explicit
  invariants instead of inferring semantics from names.
- Multipart upload stays with the official MCP attachment tool. This runtime
  manages webhook registrations/status but does not receive or verify inbound
  webhook deliveries.
