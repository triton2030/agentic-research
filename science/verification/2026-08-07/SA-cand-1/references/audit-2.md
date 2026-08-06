# Deep audit 2

## Eight Steps

### 6. Prescriptions

For each recommendation include:

- existing partial coverage and gap;
- fix layer: runtime, skill, agent, instruction text, planning handoff, or human
  checkpoint;
- owner;
- backlink to goal, instruction, or runtime risk;
- observable signal;
- sunset signal;
- validation.

Prompt-level fixes are acceptable only when runtime/skill/agent alternatives are
unnecessary or too costly for the risk.

### 7. Minimize

Before finalizing, remove or merge what the new design makes redundant. If
uncertain, use a Chesterton's fence check: what breaks if this old piece is
removed?

Emit one of: deleted, merged, left in place despite suspicion, or nothing to
remove.

### 8. Handoff + Verification

State default route for a fresh session, owner handoff, validation performed,
and residual risk.

For load-bearing routing or enforcement changes, use an empirical probe when
reasonable. For small text-only edits, structural validation plus manual
criteria check is enough.

## Lenses

Apply lenses during the steps, not as a ritual.

### Reality - Step 2

- Capability reality: does the referenced skill/tool/hook/agent/CLI actually
  exist and work here?
- Capability visibility: can a fresh session and the human operator discover it?
- Runtime match: does the chosen surface match what must route or enforce?

### Navigation - Steps 2, 4, 7

- Human navigation: can the user find the owner quickly?
- Fresh-session navigation: can a new AI session identify what to read first?
- Priority clarity: if root/local/skill/runtime disagree, is precedence clear?
- Truth routing: is durable truth owned once?
- Progressive disclosure: is depth behind conditional references?
