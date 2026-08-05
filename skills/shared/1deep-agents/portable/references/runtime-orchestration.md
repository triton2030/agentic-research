# Runtime Orchestration

Read only the subsection for the active runtime. Both adapters preserve the
same task packet, one-framework-per-agent boundary and completion barrier.

## Codex

Use native `spawn_agent` with `agent_type: "default"` and
`fork_turns: "none"`. Each stream is a new conversation-history-isolated
subagent. Dispatch in parallel when slots permit; otherwise dispatch
sequentially. Do not use named critic roles. User-owned background Codex tasks
belong to `1codex-bg-threads`, not this same-thread surface.

## Claude Code

Use the native `Agent` tool with `subagent_type: general-purpose`. Each first
pass must be a new ordinary non-fork `Agent` invocation. Do not use
`context: fork`, `/subtask`, `SendMessage` or a resumed agent ID for the first
pass: those inherit or retain prior context. Multiple independent agents may be
dispatched in parallel in one message; otherwise dispatch sequentially. Do not
use named critic profiles whose built-in method would compete with the assigned
framework. Background or retained Claude tasks are a different lifecycle and
do not satisfy this surface.

Neither adapter removes tools, active instruction stacks or shared filesystem
access. No-tools/no-write remains a prompt constraint enforced only by output
acceptance and, when material, an external pre/post state receipt.
