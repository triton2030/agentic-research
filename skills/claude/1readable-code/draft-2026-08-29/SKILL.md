---
name: 1readable-code
description: >-
  Use before writing or changing any code: shift from reactive to strategic
  engineering for readable, stable systems. Contract choices go first to
  codebase-design (Claude) or 1codebase-design (Codex).
---

# Readable Code

## Unique Context

Task-focused coding agents often program reactively and miss the system-wide
shape and future development costs an architect or CTO would notice.

Practice names are compressed handles for knowledge the agent already has; a
tutorial adds no new context.

## User Goals

- Before coding, the approach is judged from the system's future, not only the
  current task.
- Resulting code stays coherent and keeps likely future change local and
  readable.

## Protocol

1. Before the first edit, apply Ousterhout's strategic programming.
2. Check Brooks's conceptual integrity.
3. Check Ousterhout's deep modules.
4. Let a material future cost change the approach before editing.
5. If no material strategic uncertainty remains and the owner has not directly
   requested an outside view, proceed without ceremony.
6. If material strategic uncertainty remains or the owner directly requests an
   outside view, ask one fresh subagent to challenge the approach from the
   future system's perspective.
7. Address the subagent's strongest stability or maintainability objection
   before editing.
8. If a contract choice appears, follow the description's neighbor route before
   deciding it.
9. After implementation, run a check that would fail if the requested behavior
   were absent or wrong.
