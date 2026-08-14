# Existing Claude Sessions

Read this only when the owner asks what is currently running in Claude or asks
to inspect a known active local Claude conversation.

## Read-only route

- To discover sessions, call `claude_sessions` with `op: list_active`; set `cwd`
  only to narrow the result to one project. The list returns metadata, not
  conversation text.
- To inspect a known session, call `claude_sessions` with `op: read` and its
  native `session_id` only when the owner asks to read its conversation.

`read` returns bounded visible user/assistant text and excludes system messages,
thinking, tool calls/results, hooks and subagent transcripts.

`claude_sessions` is read-only. While a session appears active, never use its
`session_id` with `claude_session` `op: open_resume`: an active Claude process
already owns that session.
