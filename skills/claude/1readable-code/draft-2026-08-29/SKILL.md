---
name: 1readable-code
description: >-
  Use whenever work is about to write or change code: switch from reactive
  execution to strategic engineering for readable, stable systems.
  Contract choices use codebase-design/1codebase-design.
---

# Readable Code

## Unique Context

Coding agents often focus on the immediate task and program reactively.
They can miss the system-wide shape and future development costs an architect
or CTO would notice.

Use practice names as compressed handles for knowledge the agent already has.
Do not turn known engineering practices into a tutorial.

## User Goals

- Before coding, the approach is judged from the system's future, not only the
  current task.
- Code preserves conceptual integrity and concentrates complexity in deep
  modules, so future change stays local and readable.
- Material long-term stability risk gets a fresh outside challenge before
  implementation.

## Protocol

1. At the transition to writing or changing code, pause before the first edit.
2. Name the strategic design choice and the future development cost it avoids.
3. Use Ousterhout's strategic programming and deep modules plus Brooks's
   conceptual integrity as the governing lens.
4. Do not expand those practices into a generic checklist.
5. For coding beyond one obvious local edit, ask one fresh subagent to
   challenge the proposed approach from the future system's perspective.
6. Address its strongest stability or maintainability objection before editing.
7. If the approach requires a contract choice, use `codebase-design`
   (`1codebase-design` in Codex) for that decision.
8. After implementation, falsify the requested behavior.
9. Name the likely future change that this structure keeps local.
10. Mark unavailable evidence unverified.
