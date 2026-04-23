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

If a current-reality artifact materially changed the split, add:

```md
## Current-reality signal
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
