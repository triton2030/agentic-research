# Launch Brief Template

Use this shape. Keep it short, sharp, and owned.
Use it internally by default. Paste it into chat only if the user explicitly asked to inspect the split first or a boundary decision needs visibility.

Prefer role, behavior, and success criteria over step-by-step instructions.
Add ordered steps only when sequence is load-bearing, safety-critical, or required by the task.

```md
**Subagent:** <name and role>
**Why this subagent exists:** <one sentence>
**Parallel status:** <parallel-ready | needs local work first>
**Owned scope:** <files, module slice, question, or workstream>
**Role behavior:** <how this subagent should approach the work and what stance it should keep>
**Objective:** <concrete ask>
**State signal:** <optional - the `_state/` criterion, remaining gap, or compliance-vs-distance nuance that makes this work useful now>
**Inputs:** <paths, facts, constraints, prior decisions>
**Success criteria:** <what must be true for this work to count as done>
**Deliverable:** <what must come back>
**Evidence required:** <diff, file list, citations, command result, structured notes>
**Must not:** <overlap, scope drift, invention, or decorative output>
**Escalate if:** <what should trigger a return without forcing a guess>
```

Add for coding workers:

`You are not alone in the codebase. Do not revert other people's changes, and keep to the owned scope above.`

Add for validation or critique:

`Do not infer the intended answer from my wording. Use the evidence and say if the evidence is insufficient.`
