# Managed Runs And Tmux

Use `gemini_ask` for quick compatible calls. Use `gemini_run` when a Gemini CLI
or Antigravity CLI call needs observation, retry/stop control, logs, or timeout
diagnosis.

## Role Fit

Use Gemini when the work benefits from an independent, adversarial second look:
hidden assumptions, lifecycle/process tails, timeout boundaries, tool visibility,
model comparison, or research where a different model family may notice a
different failure.

Do not call Gemini just to duplicate Codex or Claude. If the task has no
distinct external role, answer inline. If the task is a long observable CLI
review, prefer `gemini_run`; if it must survive MCP churn, set `useTmux: true`.

## Before The Run

Check these assumptions before spending a live run:

- Role: Gemini has a named lens, not "check everything".
- Claim: the prompt says what Codex believes or wants challenged.
- Access: `cwd` and `includeDirectories` expose the real files.
- Evidence: the answer must cite files, logs, command output, or missing
  evidence.
- Mode: quick call, normal managed run, or tmux run is chosen intentionally.
- Tail: Codex will check `result` plus process/session state before closeout.

If any item is missing and changes the outcome, fix the brief before `ask` or
`run`.

## Modes

- Normal managed run: default `spawn` backend, repo-local `runs/<run_id>/`
  state, stdout/stderr logs, report, `observe/peek/wait/result/kill`.
- Tmux managed run: set `useTmux: true` only for long CLI sessions that should
  survive MCP client/server churn.

## Tmux Behavior

`useTmux: true` creates a detached session named `gemini-mcp-<run_id>`.
The pane waits on a `tmux wait-for` start channel before Gemini starts, the
server attaches `pipe-pane -o` to `tmux-pane.log`, then releases the pane.
Completion writes `exit-code.txt` and signals a done channel with `wait-for -S`.

`gemini_observe` / `gemini_peek` read ordinary logs, include `activity`, and
may include `tmux_capture` from `capture-pane` while the session is still alive.
`gemini_kill` closes only the saved session with `kill-session`; never kill
broad tmux state.

## Activity Trace

For hour-scale runs, poll `gemini_observe` with the last `next_cursor`. Use
`activity` to inspect elapsed time, stdout/stderr line counts, recent visible
logs, tool-like log lines, tmux capture availability, and stop hint. This is the
observable work trail, not Gemini's private thinking.

## Relay And Agent Behavior

Managed reports include `chat_relay.text`, `chat_relay.truncated`, and
`chat_relay.full_text_file`. Relay `chat_relay.text` for ordinary answers; if it
is truncated, read `full_text_file` before digging into raw logs.

`agent_behavior` is the closeout card for reusable external reviews: it reports
the backend control surface, observable trace, relay/full-text state, warnings,
and process or tmux tail status. Codex should use it to judge the Gemini run,
not just Gemini's findings.

## Cost Tail Check

After using Gemini as an external agent, do not close the conversation while the
managed run is still `running`, `running_orphaned`, or `killing`.

- After `gemini_wait` or `gemini_result`, confirm the status is terminal:
  `completed`, `failed`, `killed`, or safely `orphaned`.
- For tmux runs, confirm the saved `tmux_session` is gone with
  `tmux has-session -t <tmux_session>` or an equivalent session listing.
- If the MCP server was launched as a direct stdio process, confirm the
  matching `node .../experiments/gemini-mcp/src/server.js` process exits after
  the client closes.
- If the run is still alive, use `gemini_kill` and then re-check.
- If status stays `killing` after a short re-check, call `gemini_kill` once
  more; the runner may escalate the saved process group instead of broad
  killing by process name.
- Do not ask Gemini to start background dev servers or detached daemons inside
  an ordinary review run. If a task truly needs a long service, make the
  service lifecycle explicit, prefer `useTmux: true`, and keep checking the
  saved run/session until it is stopped or accounted for.
- Never kill unrelated Gemini or tmux processes; only act on the saved run id,
  saved session name, server path, or fingerprinted process.

## Timeouts And Failures

`gemini_wait.timeoutMs` waits for a report or tmux done signal. It does not kill
Gemini and is separate from Codex/MCP client timeout. If a wait times out but
the session is alive, use `observe`, `peek`, or `kill`.

If tmux is missing, run without `useTmux` or install tmux. If the session is
alive without an exit code, status is `running_orphaned`; if the session is gone
without an exit code, status is `orphaned`.

`control mode` and `remain-on-exit` are intentionally unused in this version:
durable logs, `capture-pane`, `pipe-pane`, `wait-for`, and conservative
`kill-session` cover the current workflow with less surface area.

## Brief Shape

Prefer narrow audit prompts:

```xml
<role>Independent adversarial reviewer.</role>
<lens>Hidden assumptions, timeout boundaries, and process-tail safety.</lens>
<task>Audit these files for real bugs only.</task>
<claim>Codex believes wait timeout cannot be confused with a dead CLI process.</claim>
<sources>List exact files and includeDirectories.</sources>
<criteria>List the relevant criteria files.</criteria>
<evidence>For each finding, cite file/function/log evidence or say missing evidence.</evidence>
<output>Findings first; no broad rewrite; stop after P0-P2 issues.</output>
```

Avoid prompts like "review the whole MCP" unless the user explicitly wants a
broad exploratory run and accepts the cost/noise tradeoff.
