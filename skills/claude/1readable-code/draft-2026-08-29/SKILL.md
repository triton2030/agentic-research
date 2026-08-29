---
name: 1readable-code
description: >-
  Use for nontrivial code changes, refactors, and reviews: keep behavior easy
  for coding agents to locate, understand, change, and verify. Skip mechanical
  edits; contract decisions use 1codebase-design.
---

# Readable Code

## Unique Context

A strong coding agent can make a working local change while leaving the next
change expensive: clean code mainly reduces navigation and token cost, while
agents still struggle with cross-file structure.

## User Goals

- Changed behavior has one obvious semantic owner and uses the project's
  conceptual vocabulary consistently.
- The code concentrates complexity behind stable, legible units instead of
  multiplying concepts or scattering one rule across callers.
- The requested behavior is proved at the smallest owning boundary without
  trading away correctness, data integrity, or security.

## Decision Contract

Name the current owner by file and symbol before editing; if no existing unit
can honestly own the behavior, do not invent one as readability work.

Keep units that fail together together and units that fail independently
separate.

An added wrapper, flag, mode, dependency, or helper earns its cost only when it
removes more caller knowledge, duplication, or change radius than it adds.

When the change touches queries, ORM, migrations, or transactions, read that
data edge before changing its callers.

## Evidence and Stop

Run the smallest check that would fail if the requested behavior were wrong,
through the artifact or boundary the request actually depends on; otherwise
mark the claim unverified.

Report the owner, knowledge or concepts removed or concentrated, check result,
and remaining structural risk.

Stop rather than reshape unrelated code or change a public contract merely to
make the code look cleaner.
