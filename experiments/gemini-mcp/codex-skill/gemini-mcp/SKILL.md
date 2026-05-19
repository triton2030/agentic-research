---
name: gemini-mcp
description: Use when Codex should manually call Gemini for a second opinion, code/opinion check, web research, computer-wide file research, Gemini 3.1 Pro high-thinking prompt, repo-contained Gemini MCP config work, or comparison alongside Claude MCP; skip ordinary web lookup, generic Gemini docs questions, and raw `gemini` CLI calls that do not need MCP control.
---

# Gemini MCP

Use the repo-contained Gemini MCP server when Gemini should act as a controlled
peer agent: reviewer, research agent, strategy critic, model-comparison judge,
or checker of a Codex claim.

## Active Contract

- **Entry:** controlled Gemini peer work, not ordinary lookup or inline Codex
  answering.
- **Boundary:** use MCP controls for work that needs observation, evidence,
  logs, or stop control; raw `gemini` is not a substitute for controlled work.
- **Handoff:** return to Codex after Gemini's report, warnings, and evidence are
  available, or after the exact missing layer is named.
- **Stop:** done only when the answer/evidence is relayed and the managed
  run/process or saved tmux session is terminal or honestly unknown.

## Default Path

1. Before starting, state the distinct Gemini role: what independent criticism,
   audit, research, or Codex claim-check Gemini adds. If there is no distinct
   role, answer inline instead.
2. For setup changes, run `npm run smoke` in the server root before claiming the
   surface works.
3. Use `gemini_status` before live work to confirm backend, model, thinking
   level, CLI path/version, auth mode, cwd/include-directory defaults, and tmux
   availability without a network call.
4. Use `gemini_ask` for short compatible calls. Use
   `gemini_run`/`gemini_peek`/`gemini_wait`/`gemini_result`/`gemini_kill` when
   observation, stop control, logs, or timeout diagnosis matter.
5. Set `useTmux: true` only for long Gemini CLI runs that should survive
   MCP client/server churn. Ordinary calls must work without tmux.
6. After `wait`, `result`, or `kill`, check the run is not still running and no
   saved `tmux_session` remains alive before closing the conversation.
7. Give Gemini a complete brief: role, lens, task, Codex claim to check,
   project sources, relevant criteria, targets, evidence/output shape, and stop
   condition.
8. Pass the right `cwd` and `includeDirectories`; do not leave Gemini trapped in
   the MCP server directory when project or computer-wide files matter.
9. Treat Gemini's findings as external evidence, not automatic task scope. If a
   finding describes a real current problem but strategy has not decided action,
   Codex may stage it in `_ops/problems/**` after local review instead of
   promoting it directly to `_ops/plans/**` or `_ops/criteria/*.md`.

## Evidence

Report model/thinking level, requested/effective backend, CLI path/version when
used, cwd/includeDirectories, whether the call was live or smoke/status only,
run_id/log_dir/status for managed runs, `use_tmux` when relevant, warnings, and
whether any answer came through direct CLI recovery instead of MCP. For managed
runs, include the process/session tail check.

## Stop Rule

If no backend is available, the server smoke fails, a successful-looking answer
has empty `text`, or MCP tools are missing in the current session, fix the
Gemini/MCP surface or stop with the exact missing layer. Do not silently replace
the external review with Codex's own answer.

## References

- Read [references/gemini-3.1-pro-prompting.md](references/gemini-3.1-pro-prompting.md)
  for complex briefs or model/thinking changes.
- Read [references/managed-runs-and-tmux.md](references/managed-runs-and-tmux.md)
  for role-fit, audit briefs, `run/peek/wait/result/kill`, tmux, timeout, or
  process-tail work.
- Read [references/mcp-failure-handling.md](references/mcp-failure-handling.md)
  when tools, backend/auth/config, direct recovery, or empty `text` fail.
