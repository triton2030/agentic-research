# Output Shape

Use this structure in chat:

```md
## Task
...

## Why subagents might help
...

## Assumptions
- ...

## Main agent does now
- ...

## Proposed subagents
1. <name> — <role and job>

## Launch briefs
### <name>
<brief>

## Why this split
...

Хотите, чтобы я вызвал субагентов?
```

If there are no meaningful assumptions, omit that section.

If you recommend no launch, keep the same shape, say so clearly under `Proposed subagents` and `Why this split`, and still end with `Хотите, чтобы я вызвал субагентов?`
