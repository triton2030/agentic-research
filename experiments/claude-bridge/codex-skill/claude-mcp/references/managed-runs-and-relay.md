# Managed Runs And Relay

Use Claude Bridge when Claude should be a controlled external agent, not a raw
one-off `claude` command.

## Role Fit

Use Claude when the work benefits from a careful external reviewer that can read
files, follow a structured brief, inspect logs, and produce evidence-bound
findings. Good Claude runs usually check one claim, one subsystem, or one
instruction contract.

Do not call Claude just to make an ordinary Codex answer feel more validated.
If the task has no distinct external role, answer inline and save the bridge for
work where observation, context access, or independent judgment changes quality.

## Before The Run

Check these assumptions before spending a live run:

- Role: Claude has a named lens, not "look at everything".
- Claim: the prompt says what Codex believes or wants checked.
- Access: `cwd`/`addDir` points at the real files, not only a summary.
- Evidence: the answer must cite files, logs, tool evidence, or missing
  evidence.
- Stop: Claude knows when to stop and what not to start in the background.
- Tail: Codex will check `result`/process state before final closeout.

If any item is missing and changes the outcome, fix the brief before `run`.

## Managed Run Flow

- `claude_doctor`: check local bridge/CLI capability before setup-sensitive work.
- `claude_profiles`: inspect available control profiles when default is not
  enough.
- `claude_run`: start a controlled run with profile, cwd/addDir, prompt, and
  first-class controls.
- `claude_peek`: observe milestones and relay updates with cursor.
- `claude_wait` or `claude_result`: get the final report and chat-ready answer.
- `claude_kill`: stop a looping or wrong run.
- `claude_cleanup_runs`: dry-run first; delete only with confirmation.

## Cost Tail Check

After using Claude as an external agent, do not close the conversation while the
managed run is still `running`, `running_orphaned`, or `killing`.

- After `claude_wait` or `claude_result`, confirm the status is terminal:
  `completed`, `failed`, `killed`, or safely `orphaned`.
- If the run is still alive, use `claude_kill` and then re-check with
  `claude_result`.
- If status stays `killing` after a short re-check, call `claude_kill` once
  more; the bridge may escalate the saved process group instead of broad
  killing by process name.
- Do not ask Claude to start background dev servers or detached daemons inside
  an ordinary review run. If a task truly needs a long service, make the
  service lifecycle explicit in the brief and keep the run open until the
  saved run/process tail is stopped or accounted for.
- If the MCP server was launched as a direct stdio fallback, confirm the
  matching `node .../experiments/claude-bridge/src/server.js` process exits
  after the client closes.
- After restart, kill only when the bridge fingerprint matches the saved run;
  never kill broad `claude` or bridge processes by name.
- Include the final process-tail status in Codex closeout when Claude was used.

## Brief Shape

Give Claude a complete brief: role, lens, task, goal/current state, claim,
project sources, criteria, unknowns, boundaries, expected evidence, output
shape, and stop condition. Do not ask Claude to judge only a Codex summary when
files or logs matter.

Prefer narrow audit prompts:

```xml
<role>Read-only external reviewer.</role>
<lens>Lifecycle, status truth, and process-tail safety.</lens>
<task>Audit these files for real bugs only.</task>
<goal>User goal and current project state.</goal>
<claim>Codex believes kill/status/report are now safe.</claim>
<sources>List exact files or addDir roots.</sources>
<criteria>List the relevant criteria files.</criteria>
<unknowns>List assumptions and facts Claude must treat as unknown if not evidenced.</unknowns>
<boundaries>Allowed moves, read/write policy, tools, and must-not rules.</boundaries>
<evidence>For each finding, cite file/function/log evidence or say missing evidence.</evidence>
<output>Findings first; no broad rewrite; stop after P0-P2 issues.</output>
```

Avoid prompts like "review the whole bridge" unless the user explicitly wants a
broad exploratory run and accepts the cost/noise tradeoff.

## Chat Relay

MCP cannot push directly into Codex chat. Bridge reports include
`chat_relay.text`, `chat_relay.markdown`, and `chat_relay.truncated`.
Relay `chat_relay.text` when the user needs Claude's answer. If it is truncated
or visibly cut, recover the full answer from bridge logs before reporting.

## Evidence And Failure

Do not treat Claude self-report as proof that a skill or context was read.
Use `claude_audit_skill` or logs when evidence matters.

If MCP tools are absent, treat it as registration/session exposure. Use the
controlled repo CLI fallback only; do not silently switch to an unmanaged raw
`claude` command for work that needs observation or evidence.
