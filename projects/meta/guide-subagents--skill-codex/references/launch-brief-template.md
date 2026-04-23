# Launch Brief Template

Use this shape. Keep it owned. Keep it as short or as detailed as the deliverable requires.
Use it internally by default. Paste it into chat only if the user explicitly asked to inspect the split first or a boundary decision needs visibility.

Prefer role, task, work boundaries, and quality criteria over step-by-step instructions.
Default to a non-procedural brief. Add ordered steps only when sequence is load-bearing, safety-critical, or the task is fragile enough that free-form execution would likely drift or break.

```md
**Subagent:** <name and role>
**Why this subagent exists:** <one sentence>
**Parallel status:** <parallel-ready | needs local work first>
**Owned scope:** <files, module slice, question, or workstream>
**Known dirty files at launch:** <none | path + note about preexisting dirtiness>
**Task:** <the job this subagent owns>
**Role behavior:** <how this subagent should approach the work and what stance it should keep>
**Allowed moves:** <what this subagent is allowed to do inside the owned task>
**Must not do:** <what is outside bounds, forbidden, or belongs to someone else>
**Current-reality signal:** <optional - current gap, snapshot, or local state that makes this work useful now>
**Inputs:** <paths, facts, constraints, prior decisions>
**Quality criteria:** <what makes this work high-quality, useful, and complete>
**Verification scope:** <only the checks this subagent may honestly claim>
**Deliverable:** <what must come back; patch, file edits, memo, critique, options analysis, chat answer, etc.>
**Evidence required:** <diff, file list, citations, command result, structured notes>
**Report discipline:** Report only your owned scope. Match length and format to the deliverable above. Do not summarize adjacent workers. Do not launch more subagents. Do not comment on launcher or tool availability unless it blocks the owned task.
**Escalate if:** <what should trigger a return without forcing a guess>
```

Add for coding workers:

`You are not alone in the codebase. Do not revert other people's changes, and keep to the owned scope above.`

`If your owned file was already dirty before you edited it, say so explicitly and describe only your delta.`

Add for validation or critique:

`Do not infer the intended answer from my wording. Use the evidence and say if the evidence is insufficient.`

Add for business, strategy, writing, or analysis workers when the deliverable is prose in chat:

`A substantive answer is allowed when that is the owned deliverable. Stay inside scope and make the structure useful, not artificially short.`

Add when the task is not safety-critical and the worker needs judgment:

`Do not treat this brief as a fixed algorithm. Use judgment inside the owned task, allowed moves, must-not-do boundaries, and quality criteria above.`
