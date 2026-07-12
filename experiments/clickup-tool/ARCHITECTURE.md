# Architecture

## System Boundary

This project owns a private ClickUp Public API client, safety-gated CLI, stdio
MCP server, and shared `1clickup` skill distributed to Codex and Claude. It
complements ClickUp's official OAuth MCP and does not own UI-only features.

## Runtime Entry Points

- `bin/clickup` starts the CLI through the project-pinned `uv` environment.
- `bin/clickup-mcp` starts the stdio MCP server used by both plugin runtimes.
- `plugins/clickup-control/.mcp.json` connects both plugins to that launcher.

## Ownership Map

| Concern | Owner | Responsibility |
|---|---|---|
| Credentials | `src/clickup_control/auth.py` | Resolve token without exposing it |
| HTTP/API | `src/clickup_control/client.py` | Validate paths, requests, errors and rate metadata |
| Safety | `src/clickup_control/safety.py` | Body-bound preview tokens for mutations |
| Mutation flow | `src/clickup_control/operations.py` | Preview, before-state, consume, execute |
| CLI | `src/clickup_control/cli.py` | Stable human/skill-facing commands |
| Diagnostics | `src/clickup_control/diagnostics.py` | Redacted health summary |
| MCP | `src/clickup_control/mcp_server.py` | Thin typed tools over the same owners |
| Workflow | `plugins/clickup-control/skills/1clickup/SKILL.md` | Route official MCP, API, and UI fallback |

## Main Flow

`Codex/Claude -> 1clickup -> official ClickUp MCP or clickup-control MCP/CLI ->
ClickUp Public API`. The client attaches credentials, normalizes JSON, surfaces
rate-limit metadata, and never logs the token. Mutations first create an ignored
local preview bound to method, path, query, and body; execution consumes its
short-lived one-use token.

## Boundaries And Invariants

- API paths must be relative `/v2/...` or `/v3/...`; arbitrary hosts and path
  traversal are rejected.
- GET/HEAD/OPTIONS are read-only. POST/PUT/PATCH/DELETE require a short-lived,
  one-use preview token bound to the canonical query and body.
- Credential lookup order is `CLICKUP_API_TOKEN`, macOS Keychain, then ignored
  local `api_key.md`.
- Named commands cover frequent work; guarded generic JSON API tools keep new
  official endpoints reachable without duplicating the OpenAPI catalog.
- Multipart upload stays with the official MCP attachment tool. This runtime
  manages webhook registrations/status but does not receive or verify inbound
  webhook deliveries.
