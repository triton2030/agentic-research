# MCP Failure Handling

Use this when Gemini cannot perform the role requested by the user or by Codex.

Goal: make the Gemini run work as an external agent. Do not silently replace it
with Codex's own reasoning, file reading, or a weaker local summary.

## Check First

- Failure class: decide whether this is tool visibility, backend/auth,
  context access, empty/weak answer, or lifecycle/tail state before blaming
  Gemini or replacing the review.
- Tool surface: are `gemini_status` and `gemini_ask` callable? If not, report
  MCP registration or current-session tool exposure as the failing layer. This
  is not a Gemini model failure.
- Server: run `npm run smoke` in the server root after server or environment
  changes.
- Backend: check `gemini_status` for Antigravity CLI or legacy Gemini CLI
  account auth. The current Google One / individual-user backend is
  Antigravity CLI.
- CLI path/version: before a live CLI call, confirm the exact command and
  version. In this workspace the verified Antigravity CLI is
  `/Users/triton/.local/bin/agy` `1.0.0`. The verified legacy Gemini CLI is
  `/Users/triton/.local/bin/gemini`; `/opt/homebrew/bin/gemini` is older.
- Capability: Antigravity CLI has verified `agy -p` print mode and
  `--add-dir`; legacy Gemini CLI has verified local file, web,
  `--include-directories`, and `--approval-mode yolo` support.
- Controls: if the CLI backend drops first-class controls such as model,
  thinking level, temperature, or approval mode, report that limitation before
  trusting the answer.
- Empty text: a successful-looking call with empty `text` is an error. Rerun or
  recover; do not treat empty text as Gemini's answer.
- Timeouts: distinguish the server CLI timeout (`timeoutMs` or
  `GEMINI_CLI_TIMEOUT_MS`) from the Codex MCP/client timeout.
- Tail checks: no `agy`, legacy `gemini`, or `gemini-mcp-*` tmux session should
  remain after a call/run. A `node .../src/server.js` process whose parent is
  Codex app-server is the active MCP transport, not a runaway Gemini call.

## Allowed Recovery

- Fix auth, backend selection, MCP registration, session reload, `cwd`, or
  `includeDirectories`.
- Set `GEMINI_MCP_BACKEND=antigravity` and
  `ANTIGRAVITY_CLI_PATH=/Users/triton/.local/bin/agy` for the current Google
  One / individual-user path.
- Set `GEMINI_CLI_PATH=/Users/triton/.local/bin/gemini` when the wrong Gemini
  CLI is selected for legacy managed runs.
- Increase `timeoutMs` or the server timeout when the child process times out;
  restart/retry the Codex MCP call when the client timeout fires first.
- Switch to Antigravity CLI for Gemini 3.5 Flash work when available.
- Use direct `agy`/Gemini CLI only as recovery, and report that the final answer came
  from direct CLI recovery rather than a clean MCP call.
- Use excerpts or diffs only for an intentionally bounded evidence review, and
  say that Gemini is judging only supplied evidence.

## Not Allowed

- Do not present Codex's own file reading as Gemini's review.
- Do not call a prompt-only answer a full project inspection.
- Do not accept empty `text` as success.
- Do not call direct CLI recovery a clean MCP result.
- Do not add API/SDK/Vertex recovery paths when the chosen contract is
  account-backed CLI.

## Report

Return: requested role, failing layer, recovery tried, current status, and the
next concrete fix. If recovery fails, mark the external review blocked instead
of completing it locally.
