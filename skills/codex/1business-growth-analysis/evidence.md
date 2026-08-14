# Evidence

## Support Envelope

- Target: Codex `gpt-5.6-sol`, reasoning `high` or stronger.
- Harness: Codex skill catalog and same-thread named subagents.
- Required tools: skill discovery, `business-growth-analyst`, project-document
  reading, `1chat-recall` Retrieval, optional web research.
- Required isolation: subagent invocation with `fork_turns="none"`.

## Acceptance

- `quick_validate.py` and `qv-skill` passed; `rumdl` reported no Markdown
  issues; Python `tomllib` parsed the custom-agent configuration.
- Tracked owner and installed skill projection are byte-identical; the
  installed custom-agent TOML is byte-identical to its tracked owner.
- Direct activation, Codex CLI `0.148.0-alpha.9`, `gpt-5.6-sol`, 2026-08-14:
  the bare prompt `Какую цену поставить новому тарифу?` autonomously opened
  `1business-growth-analysis` without its name in the prompt.
- The current desktop thread started before installation and does not expose
  the new `business-growth-analyst` type. Real named-agent behavior remains
  unclaimed until a fresh Codex thread reloads the agent catalog.
