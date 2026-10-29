# Reaching a session from its line

A line in `agents/sessions.md` names where its session runs; a line marked `listed for the owner's archive decision` or `kept by the owner` records a sweep or the owner's choice, not a session.
A message to a live session arrives as its next turn, interrupts nothing and runs that turn at the session's cost.
Ask it to answer in a file you will read, such as the folder's README: a reply usually stays in its own thread.

| The line has | Live when | Send | Who can send |
| --- | --- | --- | --- |
| `T3 thread <id>` | `t3 thread show <id> --json` shows `.thread.settled` false | `t3 thread send <id> "<text>"`; outside a sweep, `--wait` waits for the turn to end and prints the reply | any agent with a shell |
| `claude session <id>`, no T3 | `claude agents --json` lists that `sessionId`; its `name` is the address | `SendMessage` to that name; a Claude Desktop session by its `local_…` id, the name of the file under `~/Library/Application Support/Claude/claude-code-sessions/` whose `cliSessionId` is the session id, since a message by display name can be held and expire; two sessions with one name, by the `[ref]` `ListAgents` shows, matched by start time and status, and none if they stay ambiguous | Claude only |
| `codex session <id>`, no T3 | NOT ESTABLISHED: `codex queue` also accepts a message it never delivers | `codex queue --thread <id> --message "<text>"`, for Codex in its app or terminal; a sweep lists such a session as not asked | any agent with a shell |

`t3` is `$T3CODE_CLI_PATH` inside T3, or `~/.t3/bin/t3`.
On 2026-10-29 `codex queue` accepted a message for a Codex session in T3 that did not start a turn there within a minute, while `t3 thread send` from Claude to that Codex thread got its reply; so a Codex line from T3 carries its T3 thread.
A settled T3 thread and a Claude session missing from `claude agents --json` are closed.
A closed session is reached only by resuming it, a new paid run with its memory: `t3 thread send` to a settled thread, `claude --bg --resume <id> "<text>"` or `codex exec resume <id> "<text>"`. Do it only when the owner asks; a sweep never does.
