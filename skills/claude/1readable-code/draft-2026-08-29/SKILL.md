---
name: 1readable-code
description: >-
  Use for nontrivial code changes, refactors, or reviews: make code cheap for
  the next coding agent.
  Skip mechanical edits.
  Contract decisions use codebase-design (1codebase-design in Codex).
---

# Readable Code

## Unique Context

Readable code lowers the cost of the next change for coding agents.

It never substitutes for correctness, data integrity, or security.

## User Goals

- Changed or reviewed behavior has one obvious semantic owner in the project's
  established vocabulary.
- The owning unit concentrates each rule instead of scattering it across
  callers.
- Each implementation or review claim has a falsifier at its owning boundary.

## Protocol

1. When the change touches queries, ORM, migrations, or transactions, read that
   data edge before naming the owner, editing, or making a nontrivial review
   claim.
2. Before the first edit or a nontrivial review claim, name the existing or
   proposed owner by file and symbol.
3. If choosing that owner changes a contract, use `codebase-design`
   (`1codebase-design` in Codex) for that decision.
4. Within an already chosen contract, keep behavior that changes together in
   one owning unit.
5. Keep behavior that changes independently separate.
6. When a surface is added solely for readability, add it only if it reduces
   rule copies or callers that must know the rule.
7. Finish with the owner.
8. For each implementation or review claim, give its owning-boundary falsifier
   and observed result.
9. Mark unavailable evidence unverified.
