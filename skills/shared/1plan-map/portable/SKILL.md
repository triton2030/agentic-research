---
name: 1plan-map
description: >-
  Use when the epic map is created, audited or changed, or the owner asks to
  work on epics: read all product frames and principles, then shape epics
  from GOAL with the dashboard. Not for task files.
---

# Plan map — epics and the top level of the whole project

The map is the owner's instrument panel from the current state to "Done
means" in `GOAL.md`: it answers "where are we and how much is left" without
a retelling. Epics are the order of the work; tasks live inside them and
depend on them. The exact map root folder and the verifying instrument are
named by the project instruction; this skill owns the forms and the
requirement that the instrument exists.

## Goal

In hand: epic folders that pass [map-form](references/map-form.md), the
owner dashboard per [dashboard](references/dashboard.md), and every map
change visible with a reason line — so the owner sees the path, the stuck
points and the deferred without opening a single epic.

## Protocol

1. **Frames and principles first.** Before any composition judgment read all
   product frames and product principles, and `GOAL.md`; frames drive
   whether an epic exists, what it contains and its order — no frames → the
   goal file. Run `1use-principles` over the composition. Every epic's
   «Принципы» section names its principle files — tasks will be built on
   them; no pair fits → `1product-shaping`, and an explicit
   `нет принципа — <reason>` line.
2. **Then one of three moves.** Create the map once — and if the project
   instruction does not yet name the map root or the instrument, creating
   the map includes writing them there and creating the instrument: a bar
   verified by the hand that draws it is worse than none. Or audit/refactor
   the current map. Or edit on events — an epic closes by its criterion per
   the form, with an «Апдейты» line and released blockers in the same move,
   and the frontier advances.
3. **Composition rules.** Epics express results, never overlap and are
   commensurate in volume; `порядок` and `зависит-от` are the only links.
   Order by dependencies → riskiest-first → external gates, and give every
   epic a "why here" line; cross-cutting work is its own epic.
4. **Proof comes only from the carrier** — code, a run, an artifact, never
   plans, documents or the executor's word: composition states each epic's
   current status by its carrier's address, and `✅` lands only with
   evidence accepted from it. A closed epic stays on the map forever;
   leaving the path is `⏳` with a reason line — an epic is never deleted.
5. **The map changes only visibly.** Composition is approved by the owner's
   word with a chat-recall address — silence does not approve; editing a
   status as work proceeds is normal, editing the composition "while we're
   at it" is not. The instrument verifies the machine invariants; a
   divergence is a finding, not a silent fix.

## Boundaries

Task files inside epics — `1plan-task` · choosing what to start —
`1planning` · project goal — `1goal` · creating principles —
`1product-shaping`.
