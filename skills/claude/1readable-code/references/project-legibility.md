---
description: "Legibility test and fact-delta contract for an existing architecture owner."
---

# Project Legibility

Read only after the parent skill's Architecture Owner Gate passes, or when an
existing architecture owner may be stale or competing.

## Legibility Test

A future agent should answer these without mapping the whole tree:

- Where does the program start at runtime?
- Which subsystem owns the behavior being changed?
- What are the important data or control flows?
- Which dependencies, external/persistence edges and invariants constrain it?

Read inherited/local instructions and the root README or project index. Follow
only an explicitly routed existing owner such as `ARCHITECTURE.md`,
`docs/architecture.md` or a project-specific equivalent. Archive, generated
docs, vendor trees and temporary workspaces cannot become canonical by search
rank.

No routed owner, or several candidates claim the same truth → report the exact
gap/conflict and hand the placement/ownership decision to `1ia-audit`. Adding or
changing a durable AGENTS/CLAUDE route belongs to `1instruction-layer`.

## Existing-Owner Delta

During an authorized code change, update the existing owner only when touched
code changes a durable fact needed by the legibility test:

- runtime entry point or system boundary;
- subsystem ownership or dependency direction;
- material data/control flow;
- external system, persistence edge or invariant.

Link to code, schemas, ADRs and deeper owners instead of copying them. Exclude
file/symbol catalogs, task state, backlog/history, session narrative and desired
future architecture presented as current truth. Omit unchanged facts.

## Action Boundary

| Situation | Action |
|---|---|
| Existing owner; touched durable fact changed | Update that fact and cite code/runtime evidence |
| Existing owner; no durable fact changed | No documentation edit |
| No owner or competing owners | IA handoff; do not create another summary |
| Instruction route missing/stale | Instruction-layer handoff |
| Touched owner conflicts with touched code | Repair within current authority and show evidence |
| Unrelated architecture drift | Report it; do not widen the task |
| Review/diagnosis without edit authority | Report only |
| Parent gate does not pass | Do not open or create architecture documentation |

Architecture documentation reduces mapping cost; executable checks still prove
behavior.
