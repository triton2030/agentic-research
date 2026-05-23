# Findings — 2026-05-23 — gpt-5-5 — sess:anonymou

- 22:45 — Codex custom agents ignored because nickname_candidates contain non-ASCII | /Users/triton/.codex/agents/*.toml:5 + codex exec warning | named critic subagents unavailable until nicknames are ASCII-only
- 23:26 — md CLI snapshots не сходятся с каталогом | experiments/md-embedding-server/tests/golden/mcp-responses содержит 29 файлов, TOOLS_BY_ID=30, missing md_search_read; docs/mcp-response-snapshots.md Count: 29 | риск: agent-facing snapshot gate не ловит полный surface
