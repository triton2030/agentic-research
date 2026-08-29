# Review round 2 — 2026-08-29

Scope: full uninstalled Codex candidate after round-1 corrections.

## Independent findings

- The trajectory checker found that Retrieval → Recovery → Retrieval was still
  a reference chain and accumulated 28 units instead of one independent mode.
- The literal checker conservatively split the body into at least 16 units, so
  the declared 9 + reference count was not credible.
- The special older hot-body decision remains unresolved and still requires an
  explicit owner choice before installation.
- The description omitted recovery/restoration/validation/backfill triggers,
  and the runtime candidate omitted the English `agents/openai.yaml` surface.
- Structural validation entered transcript Repair steps that did not apply.
- Repair incorrectly routed every current-session duplicate to Capture, although
  Capture can correct only `session-context`.
- Capture left the applicable kinds for `context-note` and `session-context`
  implicit.

## Decisions for the final draft

1. Reduce the body to two context units, six mode routes, and one completion
   protocol; count body plus the one selected reference.
2. Close Retrieval with a complete `recovery-needed` handoff. Recovery becomes
   independently decision-ready and ends with a position or `abstain`.
3. Give structural validation its own reference and terminal receipt.
4. Cover every mode in a sub-200-character `Use when` description and add the
   English Codex UI manifest.
5. Route only a current-session duplicate whose sole correction is
   `session-context` back to Capture; keep every other diagnosed defect in
   Repair.
6. Limit `context-note` to quotes and `session-context` to quotes/selections.

## Final-draft falsifier

The draft fails if one selected mode needs another reference, body plus that
reference exceeds 20 independently violable units, a trigger is absent from the
description, or a terminal receipt can be only a candidate list.
