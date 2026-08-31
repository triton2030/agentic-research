# Review round 3 — 2026-08-29

Scope: second and final repeat of the full check for the uninstalled Codex
candidate after round-2 corrections and the owner's same-turn corrections about
topic selection and `context-note`.

## Directly verified progress

- Ordinary Capture now requires reading `_ops/chat-recall/topics.md` in full
  before every quote, comparing all topic boundaries semantically, reusing the
  nearest existing topic, and creating a topic only when none fits.
- Ordinary Capture now defines `context-note` as short keyword-like noun
  phrases limited to missing referents, stable artifact names, and useful search
  synonyms; prose, paraphrase, current truth, and scope widening are excluded.
- A clean executor followed that route in an isolated corpus, chose
  `chat-recall-corpus` over neighboring topics, and wrote
  `локальный корпус 1chat-recall; формат записей корпуса; chat recall corpus`.
- The candidate still passes `quick_validate.py`; no tracked or installed live
  owner was changed.

## Independent findings

1. Repair/backfill can write a `quote` without explicitly reading
   `_ops/chat-recall/topics.md` in full. Its phrase “the same searchable metadata
   as fresh Capture” is not sufficient because Repair is an independent mode
   and does not load Capture. This violates the owner's correction at
   `_ops/chat-recall/2026-08-29-150002-codex-01a04cf3.md:18`.
2. `Skip assent` is too broad. The corpus contains a valid opaque selection,
   “Да давай так и сделаем”, whose chosen referent is recoverable only from
   metadata. Topic-map reading and keyword-like `context-note` are explicit for
   quotes but not for selections.
3. The skill has no self-contained goal telling the agent to preserve useful
   owner speech, obtain an applicable position or `abstain`, and then continue
   the original work. The body currently acts only as a mode router.
4. The declared instruction budget is not proven. The prior count treated a
   numbered paragraph containing several independently violable obligations as
   one unit. A conservative split by independent behavior puts every selected
   mode above 20; this is a counting/design defect, not a table-only defect.
5. Both reviewers independently retained the unresolved topology conflict:
   ordinary Capture and Retrieval are reference-only, while the specific owner
   correction at
   `_ops/chat-recall/2026-08-19-135233-codex-01a01922.md:30` warns that these
   ordinary protocols belong in the guaranteed-read body. Newer general
   reference guidance and clean probes do not literally rescind that decision.

## Stop decision

The candidate is not ready to install. In accordance with the two-repeat stop
rule, do not silently start another rewrite/check loop. Present these residuals
and the exact draft to the owner. Continue only after the owner decides the
Capture/Retrieval topology; the next revision must also propagate the topic and
keyword-metadata protocol to every quote/selection write path, add the
self-contained goal, and re-establish the instruction budget by atomic behavior
rather than numbered paragraphs.
