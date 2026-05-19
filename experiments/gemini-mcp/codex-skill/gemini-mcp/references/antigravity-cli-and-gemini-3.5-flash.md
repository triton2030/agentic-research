# Antigravity CLI And Gemini 3.5 Flash

Use this reference when composing `prompt`, `systemInstruction`, or Gemini MCP
call parameters for the Antigravity CLI backend.

Sources:

- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/download
- https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/

## Defaults

- Use `GEMINI_MCP_BACKEND=antigravity` for the Google One / individual-user
  path.
- Use `/Users/triton/.local/bin/agy` as the verified local Antigravity CLI.
- Treat the current effective model label as `Gemini 3.5 Flash (High)` unless
  `gemini_status` or the Antigravity UI proves it changed.
- Do not claim first-class per-call model, temperature, or thinking controls:
  the current `agy -p` surface uses Antigravity's configured model picker.
- Prefer structured output or tool parameters for machine-readable results
  instead of relying only on prose format instructions.

## Prompt Shape

Use a direct, structured prompt:

```xml
<role>What Gemini is responsible for.</role>
<task>The exact outcome to produce.</task>
<context>Only facts that change the answer.</context>
<constraints>Allowed moves, must-not rules, tools, and boundaries.</constraints>
<output>Required answer shape and stop condition.</output>
```

Markdown headings are also fine; keep one delimiter style inside one prompt.

## Rules

- Be precise and direct. Avoid persuasive filler and vague goals.
- Define ambiguous terms, success criteria, and constraints explicitly.
- Add context that the model cannot infer reliably.
- Use a few consistent examples when format, tone, or classification boundaries
  are fragile.
- For heavy reasoning, rely on `thinkingLevel: "high"` and simple prompts
  before adding chain-of-thought style instructions.
- Do not ask for hidden reasoning in the final answer. Ask for conclusion,
  checks, assumptions, and evidence instead.
- For current, obscure, or factual claims, tell Gemini whether it should use
  its own available web/search capability or return uncertainty for Codex to
  verify separately.
- For arithmetic, counting, or code-like calculation, prefer a tool or code
  execution path when available.
- Keep permission-sensitive work explicit. For normal review, leave
  `approvalMode` unset. For a user-approved write run, pass
  `approvalMode: "yolo"` with absolute `cwd` and absolute
  `includeDirectories`; this maps to `--dangerously-skip-permissions` for that
  one call.

## Antigravity Notes

- `gemini_ask` maps `includeDirectories` to repeated `agy --add-dir` flags.
- `approvalMode: "yolo"` maps to `agy --dangerously-skip-permissions`; use it
  only when the allowed write folder is explicit. The server rejects this mode
  without absolute `cwd` and absolute `includeDirectories`.
- `gemini_run`/`peek`/`wait`/`result`/`kill` are still legacy Gemini CLI managed
  run controls; do not present them as Antigravity managed-run support.
- If `agy -p` returns empty text, treat it as a failed surface, then inspect the
  log or run interactively. Do not silently replace Gemini's role with Codex's
  own answer.
- If Antigravity asks for first-run setup, finish login/theme/trust once, then
  retry `agy -p` before changing MCP code.
