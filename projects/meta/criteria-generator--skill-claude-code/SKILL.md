---
name: criteria-generator
description: Use BEFORE implementing any non-trivial task to augment the user prompt with LLM-proof acceptance criteria. Analyze project context through CLAUDE.md, AGENTS.md, READMEs, docs/, `ops/`, memory, and recent git to infer true intent, load strategic direction from `ops/NORTH-STAR.md`, and if `ops/` or that north-star note is missing, create them before deeper criteria generation. Any operational files the skill needs for its own execution belong in `ops/`. Output is the augmented prompt plus only the minimal `ops/` support files needed for the skill itself — never task implementation.
---

# Criteria Generator

Turn an ambiguous user task into a prompt armored with LLM-proof acceptance criteria.

Announce at start: "I'm using the criteria-generator skill to produce acceptance criteria."

## When to use

- Non-trivial task where execution quality matters.
- Task formulation is vague or could be interpreted multiple ways.
- Before delegating a task to another agent or subagent.
- Before starting work on anything whose "done" state is not obvious.

## When NOT to use

- Trivial one-line fixes such as obvious renames or typos.
- Pure questions that do not request action.
- Tasks already accompanied by explicit acceptance criteria.

## Hard gate

Do not implement the user's task while running this skill.

Allowed side effects are limited to the skill's own operational layer in `ops/`:

- create `ops/` if it does not exist;
- create or refresh a minimal `ops/NORTH-STAR.md` if the project lacks one;
- write any other criteria-generator support files only inside `ops/`.

Do not write support files for this skill anywhere else unless repository instructions explicitly override `ops/`.

## Process

Create one `TodoWrite` item per step below. Each step has a required artifact. Do not advance without producing it.

### Step 1: Capture

Quote the user's original task verbatim. This becomes the `Original task` block in the final output.

Artifact: verbatim quote of user input, stored for Step 9.

### Step 2: Discovery

Probe for available context sources. Do not assume; check.

Required probes unless the path clearly cannot exist:

- `CWD/CLAUDE.md`, `~/.claude/CLAUDE.md`
- `CWD/AGENTS.md`, `CWD/GEMINI.md`
- `CWD/README*`
- `CWD/docs/`
- `CWD/ops/`, especially `CWD/ops/NORTH-STAR.md`
- `CWD/knowledge/`, `CWD/projects/` (or legacy `CWD/_research/`, `CWD/_random-guides/`)
- Memory index such as `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- Git: `git log --oneline -20` and `git status` if `.git` exists in CWD or an ancestor

For non-standard project layouts see `references/discovery-map.md`.

Artifact: list of paths found, grouped as `will read` vs `noted, skipped`.

If `ops/` is missing, create it before going deeper.

If `ops/NORTH-STAR.md` is missing, write a minimal note first and then read it. Keep it short:

- why this project exists;
- who it is for;
- what must become easier;
- what wrong success should be avoided.

Any other operational files created by this skill must also live under `ops/`.

### Step 3: Selective read

Read only the sources likely relevant to the task topic. For each read, record one sentence of what changed in your understanding.

Red flag: reading everything "just in case". That is rationalization. Pick by topic match.

Artifact: bulleted list of `<path>: <one-line takeaway>`.

If `ops/NORTH-STAR.md` exists, read it before deeper intent reconstruction. Treat it as evidence, not unquestioned truth.

### Step 4: Intent distillation

Produce two blocks:

- **Understood intent** (1-3 sentences): what the agent must actually do.
- **Unknowns**: explicit list of facts that would change the criteria if known.

Artifact: both blocks written out.

### Step 5: EVPI gate

For each unknown, answer two questions:

1. Does available context resolve it? If yes, resolve and continue.
2. If not, does asking the user one targeted question materially change the criteria?

If 1-3 unknowns pass the EVPI test, stop and ask the user via `AskUserQuestion` when available. If that interface is unavailable, ask directly in chat. Wait for answers before continuing.

Otherwise record each surviving unknown as an explicit Assumption in the output.

Artifact: either user answers captured, or an Assumptions list finalized.

### Step 6: Draft criteria

Draft three buckets:

- **Must** — conditions that, if missing, mean the task is not done.
- **Must not** — anti-patterns that would look correct but represent a bypass.
- **Verification protocol** — concrete commands or actions that prove the Must items.

Every Must item requires an `Evidence:` subfield naming the observable artifact that proves it: file contents, command output, URL, specific number, screenshot, or another inspectable trace.

See `references/format-examples.md` for worked examples across task types.

Artifact: draft of all three buckets.

### Step 7: Adversarial pass

Play a lazy agent. For each Must item answer: "How would I formally pass this while doing the task badly?"

For every bypass you name, add or strengthen a criterion until the bypass is blocked.

Common bypasses to probe are listed in `references/failure-modes.md`.

Artifact: list of bypasses found plus the criterion that now closes each.

### Step 8: Quality gate

Check each criterion against three axes:

- **Observable** — does it name a concrete artifact, not "I checked"?
- **Unambiguous** — can only one reading pass it?
- **Non-bypassable** — can Step 7 find a formal-pass-bad-work route? If yes, return to Step 7.

Drop or rewrite any criterion that fails any axis.

Artifact: final criteria set with all three axes satisfied.

### Step 9: Emit output

Print the augmented prompt in this exact format. Emit nothing else outside this block:

    ## Original task
    <verbatim quote>

    ## Understood intent
    <1-3 sentences>

    ## Assumptions (not verified with user)
    - ...

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] <criterion> — **Evidence**: <artifact>

    ### Must not (anti-patterns)
    - [ ] <forbidden pattern> — **Why this would be bypassed**: <bypass mechanic>

    ### Verification protocol
    1. <command or action>
       Expected: <observable output>

If there is nothing to put in Assumptions or Must not, omit that heading entirely rather than leaving it empty.

Artifact: full output in chat.

### Step 10: Offer execution

Ask the user exactly one question:

> "Acceptance criteria generated. Want me to execute the task using these criteria as a hard contract?"

If yes: stop this skill; proceed to execution treating each Must item as blocking and each Must-not as forbidden. Announce the transition.
If no: stop. Return control.

## Red flags

| You catch yourself thinking | Actually |
|---|---|
| "Task is obvious, skip Discovery" | Discovery is always cheap. Skipping is the #1 source of wrong criteria. |
| "Adversarial pass is overkill here" | The skill exists for this step. If you skip it, use a different tool. |
| "User context is thin, make a judgment call" | That is exactly when the EVPI gate matters. Ask. |
| "Evidence field is implied by the criterion" | Implied ≠ enforced. LLMs skip implied. Write it out. |
| "Three axes are a formality" | Each one blocks a distinct failure mode. Run them. |
| "One-shot is faster than 10 steps" | Speed is not the goal. Non-bypassability is. |

## Output constraint

The skill produces the augmented prompt and, when needed, only the minimal `ops/` support files required for criteria generation. No task code, no task implementation, no partial delivery of the user's requested work. Implementation begins only after the user answers Step 10.
