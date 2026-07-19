# Claude Agent Orchestration

Choose the smallest control surface that matches the communication pattern.

Official sources:

- https://code.claude.com/docs/en/agents
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/agent-teams
- https://www.anthropic.com/engineering/multi-agent-research-system

## Decision Table

| Need | Use | Owner and persistence |
| --- | --- | --- |
| One judgment or implementation | Single Opus/Fable run | Claude session |
| Retained specialist or independent opinions | Separate bridge threads | Codex; each UUID resumes independently |
| Focused delegation inside one Claude answer | Claude subagents | Claude lead; results return to its context |
| Peers must message and coordinate shared tasks | Agent team | Claude team lead; experimental session runtime |

Parallelize only independent, valuable work. Dependency-heavy work, one-file
editing, or tiny tasks lose more to coordination than they gain.

## Bridge Threads

Use bridge threads when Codex must retain, resume, interrupt, compare, or assign
different branches/worktrees to separate Claude conversations. Each thread is
bound to its UUID, cwd, worktree, and ref; the shared registry and per-thread
lease prevent different Codex processes from claiming the same turn.

Threads are independent only when started fresh. A continuation inherits its
earlier frame. Give every thread a distinct topic and role, then let Codex
synthesize disagreements without voting.

## Claude Subagents

Use the `agents` option to define focused roles when one Claude lead should own
the synthesis. A non-fork subagent has a fresh context and receives its own
prompt, project instructions, and delegation message, not the lead's full chat.
It can preload skills, discover other skills through the Skill tool, retain
optional scoped memory, and use worktree isolation. Current Claude Code supports
nested subagents with a fixed depth limit; nesting is a tool, not a default.

For safe advisor work, define read-only tools and `permissionMode: plan`; never
place bypass permissions, write-capable tools, hooks, or arbitrary MCP servers
inside an advisor-supplied agent definition. Use `--append-subagent-system-prompt`
for a shared evidence/boundary reminder. For workers, keep file ownership
disjoint and within the bridge's exact `writeFiles` postflight scope.

## Agent Teams

Teams are experimental and must not be enabled by the normal bridge profiles.
Use them only after explicit opt-in when peer messaging, a shared task list, and
sustained parallel work are essential. Start with research/review and roughly
three focused, independent roles. Give each teammate a clear deliverable and
separate file ownership; the lead must monitor, steer, wait, and verify.

Known boundaries include no reliable in-process teammate restoration after
`/resume`, one team per session, no nested teams, lagging task state, and slow
shutdown. A teammate receives project context and its spawn prompt, not the
lead's conversation history. Team tasks may persist, but that is not equivalent
to resumable live teammates.

Because teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and have a wider
coordination/write surface, add a dedicated bridge profile and tests before
production use; do not smuggle the environment flag through an ordinary run.
