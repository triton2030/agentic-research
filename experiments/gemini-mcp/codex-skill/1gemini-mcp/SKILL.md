---
name: 1gemini-mcp
description: >
  Use when Codex should run Gemini as a controlled External Peer Review agent
  through repo MCP/Antigravity CLI: second opinion, code/opinion check, bug
  hunt, architecture or instruction audit, web/file research, Gemini 3.5 Flash
  via Antigravity CLI, behavior comparison with Claude, or observable
  run/peek/wait/kill work with logs, full relay, agent-behavior evidence, and
  tail cleanup; skip ordinary web lookup, generic Gemini docs questions, and raw
  `agy`/`gemini` calls that do not need control.
---

# Gemini MCP

Use the repo-contained Gemini MCP server when Gemini should act as a controlled
external peer reviewer: reviewer, research agent, strategy critic,
model-comparison judge, or checker of a Codex claim. In the current Google One
path the default backend is account-backed Antigravity CLI with Gemini 3.5
Flash; API/SDK/Vertex fallbacks are not part of this skill.

## Active Contract

- **Entry:** controlled External Peer Review through Gemini, not ordinary
  lookup or inline Codex answering.
- **Boundary:** use MCP controls for work that needs observation, evidence,
  logs, or stop control; raw `gemini` is not a substitute for controlled work.
- **Handoff:** return to Codex after Gemini's report, warnings,
  `agent_behavior`, and evidence are available, or after the exact missing
  layer is named.
- **Stop:** done only when the answer/evidence is relayed and the managed
  run/process or saved tmux session is terminal or honestly unknown.

## Default Path

1. Before starting, state the distinct Gemini role: what independent criticism,
   audit, research, or Codex claim-check Gemini adds. If there is no distinct
   role, answer inline instead.
2. For setup changes, run `npm run smoke` in the server root before claiming the
   surface works.
3. Use `gemini_status` before live work to confirm backend, model/model label,
   thinking level, CLI path/version, auth mode, cwd/include-directory defaults,
   and tmux availability without a network call.
4. Use `gemini_ask` for short compatible calls. In the current Google One path
   `auto` should resolve to Antigravity via `agy` and Gemini 3.5 Flash; set
   `GEMINI_MCP_BACKEND=antigravity` if you need to force it. The bridge is
   account-backed only; API/SDK/Vertex routes are not supported fallbacks. Use
   `gemini_run`/`gemini_observe`/`gemini_peek`/`gemini_wait`/`gemini_result`/
   `gemini_kill` for Gemini CLI or Antigravity CLI managed runs where
   observation, stop control, logs, or timeout diagnosis matter.
5. For Antigravity read-only review, leave `approvalMode` unset. For an
   explicitly approved write run, pass `approvalMode: "yolo"` and constrain
   absolute `cwd` plus absolute `includeDirectories` to the allowed folder.
6. Set `useTmux: true` only for long Gemini CLI runs that should survive
   MCP client/server churn. Ordinary calls must work without tmux.
7. After `wait`, `result`, or `kill`, check the run is not still running and no
   saved `tmux_session` remains alive before closing the conversation. A
   `server.js` process owned by Codex app-server is an active MCP transport, not
   a Gemini run.
8. Give Gemini a complete brief: role, lens, task, Codex claim to check,
   project sources, relevant criteria, targets, evidence/output shape, and stop
   condition.
9. Pass the right `cwd` and `includeDirectories`; do not leave Gemini trapped in
   the MCP server directory when project or computer-wide files matter.
10. Treat Gemini's findings as external evidence, not automatic task scope. If a
   finding describes a real current problem but strategy has not decided action,
   Codex may stage it in `_ops/findings/**` after local review instead of
   promoting it directly to `_ops/plans/**` or owner rule documents.

## External Peer Review

Use this as the main reusable scenario across projects.

Quick user intent: "дай Gemini проверить `/path` на баги/архитектуру/инструкции"
means: build a read-only context packet from that project, confirm the
account-backed backend with `gemini_status`, run Gemini on the real sources,
observe progress, then return findings plus run-quality evidence.

**Brief Gemini as an adversarial reviewer, not a vague chatbot.** Default
boundary:

- read files/logs through `cwd` and absolute `includeDirectories`;
- for read-only review, leave `approvalMode` unset;
- do not edit files or create plans unless the user explicitly approved
  `approvalMode: "yolo"` and the allowed folders are absolute;
- return findings, missing evidence, false-positive risk, and the recommended
  next move;
- stop after the report.

**Codex closeout after Gemini returns:**

- summarize Gemini's findings separately from Codex's local judgment;
- name false positives or unverified claims;
- include `agent_behavior`: backend/model, observed progress, full relay,
  warnings, and tail status;
- apply or stage changes only after Codex rereads local criteria.

## Evidence

Report model/model label/thinking level, requested/effective backend, CLI
path/version when used, auth mode, account CLI env sanitization,
cwd/includeDirectories, whether the call was live or smoke/status only,
run_id/log_dir/status for managed runs, `use_tmux` when relevant,
`agent_behavior`, `chat_relay.full_text_file` when available, activity trace,
warnings, and whether any answer came through direct CLI recovery instead of
MCP. `activity` is observable logs/tmux/tool-like progress, not private
chain-of-thought. For managed runs, include the external process/session tail
check; do not count Codex-held MCP server transports as model tails.

## Stop Rule

If no backend is available, the server smoke fails, a successful-looking answer
has empty `text`, MCP tools are missing, or the current session returns
`Transport closed`, fix the Gemini/MCP surface or use the repo-local controlled
runner fallback once and report that recovery path as not a clean MCP call. If
recovery fails, stop with the exact missing layer. Do not silently replace the
external review with Codex's own answer.

## References

- Read [references/antigravity-cli-and-gemini-3.5-flash.md](references/antigravity-cli-and-gemini-3.5-flash.md)
  for current Antigravity CLI / Gemini 3.5 Flash calls and model-control limits.
- Read [references/managed-runs-and-tmux.md](references/managed-runs-and-tmux.md)
  for role-fit, audit briefs, `run/peek/wait/result/kill`, tmux, timeout, or
  process-tail work.
- Read [references/mcp-failure-handling.md](references/mcp-failure-handling.md)
  when tools, backend/auth/config, direct recovery, or empty `text` fail.
