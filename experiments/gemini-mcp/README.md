# Gemini MCP

Small repo-contained MCP server that exposes Gemini 3.1 Pro as an explicit
tool.

This repo-contained MCP server is registered in Codex as `gemini-mcp`. It does
not edit `~/.claude` or `~/.gemini`.

Defaults follow the current Google docs for the strongest Gemini reasoning
path:

- model: `gemini-3.1-pro-preview`
- thinking level: `high`
- optional env overrides: `GEMINI_MODEL`, `GEMINI_THINKING_LEVEL`

## Tools

- `gemini_status` reports the requested/effective backend, visible auth modes,
  model, and thinking level without making a network call.
- `gemini_ask` sends a one-shot prompt to the Gemini API with high thinking by
  default when using the SDK backend. It can also call the installed Gemini CLI
  as an explicit local backend.

## Setup

Supported SDK paths:

```bash
npm install
export GEMINI_API_KEY=<your_api_key>
```

`GOOGLE_API_KEY` is also supported and takes precedence when both variables are
set, matching the Google GenAI SDK behavior.

Vertex AI without an API key:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your_project_id>
export GOOGLE_CLOUD_LOCATION=global
gcloud auth application-default login
```

Local Gemini CLI backend, for machines already authenticated with Gemini CLI:

```bash
export GEMINI_MCP_BACKEND=cli
```

`gemini_ask` will auto-detect this backend when no SDK auth is available and
`~/.gemini/oauth_creds.json` exists. This path shells out to `gemini -p`; it is
useful for local peer-review workflows but does not expose SDK-level controls
for `thinkingLevel`, `temperature`, or `maxOutputTokens`.

Optional overrides:

```bash
export GEMINI_MODEL=gemini-3.1-pro-preview
export GEMINI_THINKING_LEVEL=high
export GEMINI_CLI_PATH=/opt/homebrew/bin/gemini
```

For Gemini 3, prefer leaving `temperature` unset so the API default is used.
The Google docs warn that lowering temperature can degrade complex reasoning.

## Local Checks

```bash
npm run smoke
```

The smoke test verifies MCP startup and the missing-key error path. It does not
make a live Gemini API call; it uses a fake Gemini CLI for CLI-backend coverage.

## Run MCP Server

```bash
npm run mcp
```

Manual Gemini CLI registration, if you choose to test it there:

```bash
gemini mcp add gemini-ask node /Users/triton/Documents/GitHub/agentic-research/experiments/gemini-mcp/src/server.js
```

For Codex or Claude, register the same command in the relevant MCP config only
after the local smoke test passes and the use case proves useful. The Codex
registration for this workspace already uses the command above.
