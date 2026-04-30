---
name: gemini-mcp
description: Use when Codex should call Gemini through the repo-contained Gemini MCP server, inspect or register Gemini MCP config, compose Gemini 3.1 Pro prompts with high thinking, or use Gemini alongside Claude MCP; skip ordinary web lookup, generic Gemini docs questions, and raw `gemini` CLI calls that do not need MCP control.
---

# Gemini MCP

Use the repo-contained Gemini MCP server when the user wants Gemini as a
controlled peer to `claude-mcp`, especially for comparison, second-opinion,
reasoning-heavy prompts, or MCP registration work.

## Locate Server

- Server root:
  `/Users/triton/Documents/GitHub/agentic-research/experiments/gemini-mcp`
- Default model: `gemini-3.1-pro-preview`.
- Default thinking level: `high`.
- Supported backends:
  - Gemini Developer API with `GOOGLE_API_KEY` or `GEMINI_API_KEY`;
  - Vertex AI with `GOOGLE_GENAI_USE_VERTEXAI=true`,
    `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and ADC;
  - explicit local Gemini CLI backend with `GEMINI_MCP_BACKEND=cli`.
- Registered Codex MCP name: `gemini-mcp`.
- MCP command:
  `node /Users/triton/Documents/GitHub/agentic-research/experiments/gemini-mcp/src/server.js`

Do not edit `~/.gemini`, `~/.claude`, or other global MCP config unless the
user asks for installation, registration, or a persistent MCP surface.

## Default Flow

1. For fresh or changed setup, run `npm run smoke` in the server root before
   claiming the MCP surface works.
2. Use `gemini_status` to confirm requested/effective backend, visible auth
   mode, default model, and thinking level without making a network call.
3. Use `gemini_ask` for one-shot Gemini prompts. Leave `thinkingLevel` unset
   unless the user explicitly wants a lower setting; the server default is
   `high`.
4. When prompt quality matters, read
   `references/gemini-3.1-pro-prompting.md` before composing
   `prompt` or `systemInstruction`.
5. If `gemini_status.effective_backend` is `null`, do not say Gemini is broken
   only because there is no API key. Report the missing auth layer precisely:
   API key, Vertex AI/ADC config, or explicit `GEMINI_MCP_BACKEND=cli`.
6. If Codex MCP tools for `gemini-mcp` are unavailable, use the same server
   command as the stdio fallback or report that MCP registration is missing.

## Prompt Controls

Use first-class tool fields instead of burying controls inside the prompt:

- model: `model`, only when overriding `gemini-3.1-pro-preview`;
- reasoning depth: `thinkingLevel`, default `high`;
- behavior frame: `systemInstruction`;
- output length: `maxOutputTokens`;
- temperature: omit by default for Gemini 3 unless the user asks.

The Gemini CLI backend is a local fallback through the installed `gemini`
command. It does not expose first-class controls for `thinkingLevel`,
`temperature`, or `maxOutputTokens`; report those limitations from
`gemini_ask.warnings` instead of pretending the controls were enforced.

## Evidence

Report:

- model and thinking level used;
- requested/effective backend and whether API key, Vertex AI/ADC, or Gemini CLI
  auth was visible, without printing secrets;
- whether the call was live or only a smoke/status check;
- returned text, `usageMetadata` when available, and warnings when the Gemini
  CLI backend was used;
- validation command and result after server or skill edits.

## Stop Rule

If the MCP server is missing, smoke fails, no backend is available for a live
call, or official docs contradict the model/thinking defaults, stop and report
the exact missing layer instead of falling back to generic Gemini advice.
