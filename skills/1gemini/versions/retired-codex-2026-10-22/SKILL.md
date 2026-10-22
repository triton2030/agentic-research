---
name: 1gemini
description: >-
  Use when the user explicitly asks for Gemini or Antigravity, a Gemini-family
  second opinion, an existing Gemini session, or Gemini analysis of one
  audio/video file. Not for web research or images.
---

# Gemini through Antigravity

Return a Gemini answer together with runtime evidence from Google's official
`agy` executable. Keep the root agent responsible for the final decision.

## Route

- Text, code, or project advice: pass a self-contained brief or selected
  excerpts. The wrapper runs Antigravity in a disposable directory; it does not
  attach the source project as Antigravity's workspace.
- Audio or video: first read [references/media.md](references/media.md), then
  pass exactly one `--media` path. That reference owns the required disclosure
  and procedure.
- Account, model, or CLI failure: read
  [references/runtime.md](references/runtime.md). Do not replace the account
  route with an API key, SDK, private backend, or extracted OAuth token.

For a fresh text call, send the complete brief on stdin:

```bash
python3 /Users/triton/.codex/skills/1gemini/scripts/gemini_advisor.py \
  --cwd /absolute/project/path <<'EOF'
<brief with task, constraints, and requested output>
EOF
```

For project-document review, stdin must include the selected excerpts and their
source addresses. `--cwd` is only the logical context root; it does not expose
project files to Gemini.

Resume only a text conversation and keep the same logical context root:

```bash
python3 /Users/triton/.codex/skills/1gemini/scripts/gemini_advisor.py \
  --cwd /absolute/project/path --resume <conversation-id> <<'EOF'
<follow-up>
EOF
```

Use `--model` only for an explicit Gemini model choice. The default is
`gemini-3.1-pro-high`; never accept a non-Gemini fallback.

When useful independent work remains after launch, run the same wrapper command
through the native yielded `functions.exec` terminal-wake pattern. The cell
first returns a small `family: gemini, phase: started` receipt, then calls
`yield_control()` and owns the exec session. Every yielded cell emits exactly
one final `notify()`. After an observed process exit, store the parsed wrapper
JSON or a bounded malformed-output diagnostic under a unique task-scoped
`result_ref`, then notify only `observer: terminal`, `process: exited`, the exit
code, the exec `session_id`, `result: parsed|malformed`, and that opaque
reference. A caught cell or transport failure before an observed exit stores
its diagnostic under `failure_ref` and notifies `observer: failed`,
`process: unknown`, `external: unknown`, and known addresses. Load the reference
after wake and apply the existing evidence contract. Never retry an uncertain
call. This is a direct external process, not a native Codex subagent. Do not
send progress notifications. If the command finishes before yielding a session,
handle its ordinary direct result.

## Evidence contract

Execution is proven only when the wrapper exits zero and returns all of:

- `ok: true` and `session.status: SUCCESS`;
- a non-empty `response` and `session.conversation_id`;
- `requested.model == resolved.model` and both identify Gemini;
- `requested.context_root` is the intended source project and
  `resolved.cwd != requested.context_root`;
- for text, `resolved.mode == "isolated-text"` and
  `isolation.source_project_workspace_attached == false`;
- for media, `resolved.mode == "isolated-media"` and `media.viewed: true`,
  backed by a completed `view_file` event for the staged file; audio additionally
  reports `delivery: audio-mp4-carrier` and `audio_transcoded_for_delivery: true`.

Workspace separation is not an OS-level denial of every absolute source-project
path. The wrapper rejects completed reads of other media paths.

Anything else is a failed call, even if a plausible answer appears in output.
Report the exact failure and stop; do not present configuration, a prior
conversation, or a soft-denied tool action as Gemini's answer.

## Completion

Return the response, resolved model, conversation ID, and compact usage. For
media, follow the completion and disclosure contract in `references/media.md`.
`session.duration_seconds` and `usage` are upstream `agy` fields;
`session.wrapper_elapsed_seconds` is the locally measured process time. On
resume, do not infer per-turn or conversation-wide scope beyond the emitted
`usage_scope`.
The source project was not attached as Antigravity's workspace. Do not imply
that OS-level access was impossible or that Gemini read or changed files not
included in the brief.
