---
name: 1readable-code
description: >
  Use before editing code whenever the change is more than a one-liner: adding
  a rule, check, flag, helper, layer or dependency; deciding where new behavior
  goes; touching logic that already exists in more than one place; refactoring,
  restructuring or reviewing code. Name the owner before the first edit, then
  re-enter at each further structural choice in the session. Interface or seam
  contracts → `codebase-design`.
---

# Readable Code

## Goal

Behavior lands in the unit that already owns it, and the next agent pays for
one read instead of a re-tour. Cheap navigation is the product; correctness is
the precondition, not the achievement.

## Success criteria

- The owning unit is named with file and line before the first edit.
- Each structural choice states what it removes; "adds a wrapper" alone fails.
- The change touches the smallest set of units that can fail together.
- One executable check fails when the changed behavior is wrong, run against
  the artifact that was requested rather than a demo path around it.
- Data-layer edges — queries, ORM, migrations, transactions — are read before
  they are written.
- Obsolete paths the change exposed are listed; unrelated cleanup is absent.

## Invariants

Symptom location is not ownership. The file where a failure surfaces is
usually right and the layer is usually wrong; editing where you found it is
the most common structural failure there is.

Scatter costs more than a redundant wrapper. Spreading the same complexity
across more units adds navigation cost; pulling it back into the unit that
owns it removes cost. Prefer one saturated unit over a spread of thin ones.

Comments, intent-shaped names and prose carry no boundary. Only code, types,
errors and a failing check do.

Explicit beats convention. Behavior a reader must infer from a framework,
decorator, metaclass or naming rule is behavior the next agent will miss.

Nothing here overrides an explicit requirement, correctness, data integrity
or security. Surface the conflict instead of trading it away.

## Delta

Writing working code is not the deficit. Unaided, the model:

- edits at the layer where it saw the symptom;
- starts editing on the first step, before ownership is known;
- adds a unit instead of removing one, and spreads instead of gathering;
- reads a structural rule once and drifts back to default as the session grows;
- treats a passing suite as proof of what was asked.

Missing operator:

```text
name owner (file:line) → say what disappears → smallest set that fails together
→ one check on the requested artifact → re-enter at the next choice
```

## Known failures

`when → failure → cost → where`

- symptom found → edited at that layer → right file, wrong layer; the
  regression survives a green suite → Invariants, ownership
- behavior has no obvious home → a helper family, flag or folder pattern is
  added → duplication and per-unit complexity grow every iteration → Mechanics
- interface or seam is being designed → structure invented ad hoc → a spread
  of thin modules that agents repair far worse than one fat unit → open
  `codebase-design`
- a check exists → the check is satisfied and the artifact left hollow → suite
  green, requested unit absent → Mechanics, step 5
- session grew long → the gate ran once at the start → compliance decays with
  each generated unit and late choices go unguarded → Mechanics, step 6
- no architecture owner, or several claim the same truth → another summary is
  written → a second source of truth → `1ia-audit`

## Mechanics

Run this at each structural choice, not once per task.

1. **Name the owner.** File and line of the unit that already owns this
   behavior; for new behavior, the unit whose contract it extends. Cannot name
   it? Keep reading — do not edit.
2. **Say what disappears.** A concept, mode, dependency, flag or duplicate.
   Nothing disappears and something is added: the change is a cost, state it
   as one.
3. **Bound the change.** Units that can fail independently stay separate; units
   that fail together stay whole. Symmetry is not a reason.
4. **Read the data edge first** when queries, ORM, migrations or transactions
   are touched: this is where constrained changes break most.
5. **Prove the requested thing.** Smallest check that fails when the behavior
   is wrong, run against the artifact that was asked for, not a path built to
   satisfy the check.
6. **Re-enter at the next choice.** Compliance falls as the session generates
   more units; the gate fires again rather than being remembered.

## Completion

Owner named, removal stated, change bounded, one check run and reported with
its output. Unrun checks, assumptions and remaining structural risk named.
A self-report that a step was "already handled" does not close anything.
