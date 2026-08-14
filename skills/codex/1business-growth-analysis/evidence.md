# Evidence

## Support Envelope

- Target: Codex `gpt-5.6-sol`, reasoning `high` or stronger.
- Harness: Codex skill catalog and same-thread named subagents.
- Required tools: skill discovery, `business-growth-analyst`, project-document
  reading, `1chat-recall` Retrieval, optional web research.
- Required isolation: subagent invocation with `fork_turns="none"`.

## Acceptance

- `qv-skill` passed on the installed package; `rumdl` reported no Markdown
  issues; Python `tomllib` parsed the custom-agent configuration.
- Tracked owner and installed projections are byte-identical
  (`sync_simple_projections.py --check`); the installed custom-agent TOML is
  byte-identical to its tracked owner.
- Direct activation, Codex CLI `0.148.0-alpha.9`, `gpt-5.6-sol`, 2026-08-14:
  the bare prompt `Какую цену поставить новому тарифу?` autonomously opened
  the skill — earned by the **pre-2026-08-14-evening** description.

## Not claimed (2026-08-14 evening rewrite)

- The rewritten description has NOT been re-run on Codex. Codex acceptance
  above belongs to the previous text.
- Named-agent behavior on Codex still unclaimed: the desktop thread that
  installed the agent predates the catalog reload.
- The seven-section rewrite of `developer_instructions` (family parity with the
  ten live Codex critics) is a structural change only — no behavioral run.
