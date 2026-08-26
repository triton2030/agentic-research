# Claude Native Tool Routing

Read this only when the outcome depends on a named Claude tool, `Skill`, MCP
capability, subagent, monitor or workflow.

## Runtime Rule

The exact tool set is session-local and can change with Claude Code version,
provider, mode, permissions and settings. Do not paste a static inventory into
the advisor brief. Describe the needed capability and let Claude choose its
visible native tools.

- Do not add manual directories. Fresh bridge sessions keep Claude Code's native
  tools and the project `cwd`, but omit filesystem-sourced user/project/local
  instructions, custom skills, hooks, MCP integrations, plugins, and auto-memory.
  Managed policy and account state remain runtime-owned, and resumed sessions
  retain their prior conversation. Claude may deliberately read any OS-accessible
  instruction or evidence file when the task makes it relevant.
- A named `Skill` or MCP capability is not automatically available in the clean
  route. If the task truly requires one, include its exact file/address or
  capability owner in `<context>` and let Claude inspect what is available.
- Use `Agent` for one genuinely independent sizeable evidence stream.
  `SendMessage` can continue a useful subagent instead of starting another.
- Use `Monitor` when the task must react to an ongoing command, log, file or
  event stream.
- Request `Workflow` only for large, repeatable orchestration across many
  agents. It is not the default for a normal review or a few independent tasks.

Opus 5 delegates readily. Keep small work in the root advisor; if one subagent
is enough, use one. Internal Claude agents are not an independent model-family
opinion.

## Evidence Boundary

`claude_ask` returns one terminal answer, model/session metadata and warnings.
The optional session adapter can expose bounded normalized tool names and
subagent progress, but never raw tool inputs/outputs or a structured audit log.
Claude's final claim or an activity label is not proof of an exact invocation.
If named-tool use is itself an acceptance criterion, mark it unverified or run a
separate runtime diagnostic.

Official volatile owners:

- <https://code.claude.com/docs/en/tools-reference>
- <https://code.claude.com/docs/en/agent-sdk/claude-code-features>
