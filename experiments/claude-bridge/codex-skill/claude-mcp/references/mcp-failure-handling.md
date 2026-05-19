# MCP Failure Handling

Use this when Claude cannot perform the role requested by the user or by Codex.

Goal: make the Claude run work as an external agent. Do not silently replace it
with Codex's own reasoning or a weaker local summary.

## Check First

- Failure class: decide whether this is tool visibility, runtime/auth,
  context access, answer quality, or lifecycle/tail state before blaming Claude
  or replacing the review.
- Tool surface: are `claude_run`, `peek`, `wait`, `result`, and `kill`
  callable? If not, treat it as MCP registration or current-session tool
  exposure, then try the repo-local CLI bridge.
- Runtime: run `claude_doctor` or CLI `doctor` and report the failing layer.
- Local installs: prefer the native `~/.local/bin/claude` that the bridge
  resolves first. A stale lower-priority Homebrew cask can trigger Claude's
  multiple-install warning without breaking bridge runs.
- Profile: switch to the profile that matches the task before downgrading the
  task: `normal`, `read-only`, `skill-audit`, `no-memory`, or `turbo`.
- Context: fix `cwd`, `addDir`, prompt files, tools, permissions, or budget so
  Claude can inspect the required files itself.
- Read-only context: if an external folder is read-only, Claude returns
  findings, text, patches, or edit instructions; Codex writes only after local
  criteria are applied.
- Capability: local verification showed Claude Code can read outside the repo
  with `--add-dir` and access the web through `Bash`.
- Evidence: use bridge logs or `claude_audit_skill` when the task depends on
  proving that Claude read a target path.
- Long output: if `chat_relay.truncated` is true or the visible answer is cut,
  inspect `stdout.log`, `events.ndjson`, or other bridge artifacts before
  reporting Claude's final answer.
- Tail check: treat Codex-held `server.js` MCP transports as tool plumbing, not
  model work. The expensive tail to stop is the saved `claude` run/process
  group surfaced by `result`, not every bridge server process in `ps`.

## Allowed Recovery

- Rerun with corrected profile, context roots, tools, or budget.
- Use the controlled CLI bridge fallback when MCP tools are absent.
- Recover a long answer from logs, and say that the visible relay was
  truncated.
- Narrow the external review only if the user agrees or the task was already
  intentionally evidence-bounded.

## Not Allowed

- Do not present Codex's own file reading as Claude's review.
- Do not paste a tiny excerpt and call it equivalent to Claude inspecting the
  project when full project access was needed.
- Do not use an uncontrolled raw `claude` command for work that needs logs,
  observation, or read evidence.
- Do not treat a missing MCP tool list as a Claude reasoning failure.

## Report

Return: requested role, failing layer, recovery tried, current status, and the
next concrete fix. If recovery fails, mark the external review blocked instead
of completing it locally.
