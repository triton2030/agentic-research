---
name: 1t3
description: >-
  Use when work goes to a T3 Code thread — launch, wait, follow-up, close —
  when subscription limits matter, or audio, video or PDF needs Gemini. Whom
  to call and with which model: 1orchestration.
---

# T3 Code threads

First find where you run: the T3 tools differ, and the wrong ones launch
executors as detached top-level threads (2026-11-05).

- **Inside a T3 thread** — `mcp__t3-code__*` tools are among your tools,
  deferred ones included. Use only them; the `t3` server (`mcp__t3__*`) is
  often connected too, but it is the route from plain Claude Code.
- **Outside, in plain Claude Code** — no `mcp__t3-code__*` tools; use
  `mcp__t3__*`. If a `t3-code` call answers `thread_credential_required`, you
  are outside too.

Then read `references/common.md`, and `references/inside-t3.md` or
`references/claude-code.md` for your case. Audio, video or PDF for Gemini:
`references/gemini-media.md`.
