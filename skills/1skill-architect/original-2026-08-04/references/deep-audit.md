# Deep Audit Of Skill Landscape

Rare mode: full audit of a skill/runtime/control-surface landscape, not design
or repair of one skill. Use this when the user asks for a broad audit or when
the system keeps adding surfaces without a clear owner.

## Contents

- Eight Steps
- Lenses
- Output Shape

## Eight Steps

Keep the order. Current-state map and forces come before failure scan.

### 1. Telos

Read the live owner docs that constrain the audit: root/local instructions,
goal/README/task files if present, and the user's current request.

Done when goal, scope, stop rule, and constraining owners are explicit. If the
upstream layer is missing or stale, report that instead of compensating with
general architecture.

### 2. As-is Map

Inventory actual capabilities before diagnosing failures:

- skills and their trigger boundaries;
- agents and tool policies;
- hooks, permissions, validators, lifecycle rules;
- instruction layers and precedence;
- scripts or commands that already enforce behavior;
- mismatches between text and reality.

Use exact handles, not classes. "Hook exists" is too vague; name event, matcher,
and action.

### 3. Forces

Name 2-3 current design constraints that could age the recommendation: model
shift, tool-surface change, repo growth, new task class, owner change.

Each force needs an early signal and a design constraint. Generic future change
without a signal is out of scope.

### 4. Failure Classes

Group concrete failures by root cause. Tie each failure to a place the current
system permits it and to an existing surface that should have covered it but
does not.

Done when failures are classes, not a flat patch list.

### 5. Leverage

Prefer one intervention that removes a class over several one-off patches.

- `high`: covers 3+ failures;
- `medium`: covers 2;
- `low`: covers 1.

Do not recommend a new surface until reuse-first has failed.

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

### Readability - Step 4

- Default behavior: does the model know what to do when no special branch
  applies?
- Drift and contradiction: do layers repeat or disagree?
- Current trace: did this conversation show skipped truth, wrong surface,
  premature editing, or weak verification?

### Cognitive Effect - Steps 4-6

- Necessity: does each cognitive skill make its natural default, causal harm,
  and corrective mechanism intelligible, or merely assert good practice?
- Transformation: can the claimed change be written as a concrete `A -> B`,
  with tells and operators that a fresh agent can apply?
- Deficit/proxy: is the missing control act behaviorally named, and has unreliable
  introspection been translated into an observable check?
- Local control: does the failure require a changed success measure, phase
  boundary, commitment anchor, or labor inversion, and is only that lever used?
- Demonstrations: do examples teach the decision transition and plausible
  anti-example, or only the final output shape?
- Form: does the skill's own latent genre demonstrate the decision structure it
  asks the reader to continue beyond literal rule coverage?
- Controller: what reusable frame, rule, map, or proof obligation remains after
  the primary act?
- Transfer: what unshown decision or later behavior proves the mechanism rather
  than checklist compliance?

### Pressure - Step 7

- Still alive: does the rule still serve its backlink?
- Overlap: do two rules cover one problem without a single owner?
- Chesterton's fence: what breaks if this old thing is removed?

### Decision - Steps 5-6

- Reversibility: does proof match undo cost?
- Blast radius: what breaks if wrong?
- Owner clarity: which file or runtime owns the rule?
- Simplicity under pressure: what signal tells us the rule has aged badly?

## Output Shape

Use for long audits. Compress for smaller tasks.

```md
## Evidence Type
- `direct trace` | `source audit` | `structure-only`
- Limitation: ...

## References Applied
- references/deep-audit.md
- <other files actually read>

## 1. Telos
- Outcome:
- Applicable owners:
- Truth layer: `hot` | `cold` | `unknown`

## 2. As-is Map
- Skills:
- Agents:
- Hooks / permissions:
- Instruction layers:
- Scripts / validators:
- Mismatches:

## 3. Forces
- Force 1:
  - Early signal:
  - Design constraint:
- Force 2:

## 4. Failure Classes
### Class A: <name>
- Root:
- Concrete failures:
- Existing coverage and why it misses:

## 5. Leverage
### Cluster 1
- Systemic fix:
- Covers:
- Rank: `high` | `medium` | `low`

## 6. Prescriptions
### Prescription 1
- Reuse-first gate:
- Fix layer:
- Owner:
- Backlink:
- Natural default / operational gap:
- Necessity and mechanism:
- Thought demonstration / exact tool advantage:
- Observable signal:
- Sunset signal:
- Validation:

## 7. Minimize Pass
- Deleted:
- Merged:
- Left in place despite suspicion:

## 8. Handoff + Verification
- Default route for fresh session:
- Owner handoff:
- Validation performed:
- Residual risk:
```

Rules:

- Do not publish prescriptions without reuse-first gate, owner, observable
  signal, and validation.
- Include minimize pass even when nothing was removed.
- Use folder audit only when folders are actually in scope.
