---
name: 1readable-code
description: >
  Use before editing code whenever the change is more than a one-liner: adding
  a rule, check, flag, helper, layer or dependency; deciding where new behavior
  goes; touching logic that already exists in more than one place; refactoring,
  restructuring or reviewing code. Name the owner before the first edit, then
  re-enter at each further structural choice in the session. Interface or seam
  contracts → `codebase-design`, installed as `1codebase-design` on Codex: a
  spread of thin modules is what agents repair worst.
---

# Readable Code

## Goal

Cleanliness does not raise the odds of a correct change; it lowers what the
change costs — file revisits and tokens. Correctness, data integrity and
security stay preconditions: surface the conflict instead of trading one away.

## Success criteria

Empty on purpose: every criterion here restated an operation below. Each
operation names its own trace.

## Invariants

Truth about behavior lives where it executes and where one unit owns it.

Scatter costs more than a redundant wrapper: gathering complexity into its
owner removes cost, spreading the same complexity adds it.

## Delta

The model writes working code and, as of 2026-08-11 on Opus 5, finds an obvious
owner on its own. What it does not do: give the owner's address, inventory what
its change removed, read the data edge before writing it, and keep holding any
of this as the session grows.

## Known failures

- behavior has no obvious home → a helper family, flag or folder pattern is
  added → duplication and per-unit complexity grow every iteration → Mechanics

## Mechanics

1. **Name the owner before the first edit** — file and line of the unit that
   already owns this behavior, or whose contract new behavior extends. Cannot
   name it, do not edit.
2. **Inventory what disappears** — the concepts, modes, dependencies, flags or
   duplicates this change removes.
3. **Bound the change** — units that fail together stay whole, units that fail
   independently stay separate.
4. **Read the data edge first** — queries, ORM, migrations, transactions: where
   constrained changes break most.
5. **Prove the requested thing** — smallest check that fails when the behavior
   is wrong, run against the artifact that was asked for, not a path built to
   satisfy it. Cannot run it, say so rather than reporting a pass.
6. **Re-enter at the next structural choice** — compliance falls with each unit
   the session generates, so the gate fires again rather than being remembered.

## Completion

Six traces in the report, or the missing one named with its reason.
