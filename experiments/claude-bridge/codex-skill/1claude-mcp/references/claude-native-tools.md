# Claude Native Tool Routing

Read this only when the outcome depends on a named Claude tool, `Skill`, MCP
capability, subagent, monitor or workflow.

## Runtime Rule

The exact tool set is session-local and can change with Claude Code version,
provider, mode, permissions and settings. Do not paste a static inventory into
the advisor brief. Describe the needed capability and let Claude choose its
visible native tools.

- Do not add manual directories. Native sessions retain settings, skills,
  hooks, MCP and deferred tool discovery, and can use any OS-accessible path.
- Name a `Skill` when that specific reusable workflow is required.
- Name the MCP capability or server when it matters; `ToolSearch` discovers
  deferred schemas on demand.
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
- <https://code.claude.com/docs/en/agent-sdk/tool-search>
- <https://code.claude.com/docs/en/workflows>
