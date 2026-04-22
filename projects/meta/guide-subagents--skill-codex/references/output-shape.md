# Output Shape

Use this compact structure in chat by default:

```md
## Main agent does now
- ...

## Subagents launched
1. <name> — <role and job>

## Why this split
...
```

If assumptions materially affected the split, add:

```md
## Assumptions
- ...
```

If `_state/` is absent or does not change the split, omit `State signal`. If it matters, add:

```md
## State signal
- ...
```

If you decide not to launch subagents, replace `## Subagents launched` with:

```md
## No subagents launched
- <one-line reason>
```

Do not paste full launch briefs by default.

If the user explicitly asks to inspect or approve the split before launch, you may use this longer plan-first shape:

```md
## Main agent does now
- ...

## Proposed subagents
1. <name> — <role and job>

## Launch briefs
### <name>
<brief>

## Why this split
...
```
