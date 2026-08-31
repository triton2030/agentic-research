# Compaction Safety

Read when a refactor target map leads to deleting text in a live corpus:
deduplication, compression, moving answers between owners. The skill still
stops at mapping — these are the obligations the map must carry so the
accepted execution task cannot create silent loss.

Domain boundary: this file owns document-corpus compaction. Refactoring a
skill or an instruction set belongs to the meta-skills' refactor procedure.

The default failure is not «compressed too little» but **silent loss**: text
deleted as «derivable from the owner», the owner does not have it, the link
resolves and every linter is green.

## Entry gate

Before the first cut, every target gets a row:

```text
baseline path#locator | removed obligation | final owner path#locator |
local delta | protected IDs and consumers
```

No `final owner path#locator` — it is not deduplication; stop: owner choice
and repair → `1ia-audit`, holders and graph impact → `1md-graph`. A cut that
removes or changes the very definition of an operation, entity or enum other
files reference is not deduplication: until the new home carries the full
contract, the original definition stays.

## Home before cut, owners frozen

«Both sides of a link got compressed» is a consequence of wave decomposition:
file A cut with a pointer to B, B cut in another wave with a pointer to A, the
answer lives nowhere.

- The home of every contested answer is named before the first wave;
  `owner unresolved` blocks cutting both sides.
- The owning side is **frozen** for the whole campaign — it enters no wave as
  a compression target. A final full pass verifies the invariant; it is not
  the way to find holes the plan allowed.

## Coverage test

Deleting is allowed only when the final owner **semantically covers the whole
removed obligation**: check scope, actors, modality, conditions, timing,
defaults and exceptions against addressable evidence. A matching phrase
without the needed condition is not coverage. Partial coverage → the uncovered
part stays as a local delta. Owner pointing back («X owns…» ↔ «owned by X») is
a circle, not deduction — `1ia-audit` resolves it; cutting before that is
forbidden.

## What is not a duplicate

The map names these classes explicitly, or the executor cuts them as
«retelling»:

- **Locators.** IDs and anchors are an address surface, not prose. Before
  delete/rename: Markdown holders → `1md-graph`; exact references from
  code/spec/tests → `1cli-tools`. Any live consumer blocks the cut; surviving
  IDs are never renumbered.
- **Inactive contracts.** For `deferred`/`planned`/flagged claims the owner
  must keep the activation trigger, post-activation rule, scope, defaults and
  exceptions — the loss surfaces at activation.
- **Local coordination delta.** A link between foreign rules — timing,
  responsibility, sequence — is a protected claim of the artifact the live
  contract assigns it to.
- **Data-shape obligations.** Default, cardinality, requiredness, mutual
  exclusion and fixation moment are not derivable from a behavioral rule.

## Loss ledger

The cut is verified by someone who did not cut (form → [delegation](delegation.md)).
The wave verifier returns an addressable ledger: baseline claims present
neither in the new version nor at the named owner — quote, address, why not
derivable. Every finding gets an outcome: `restored`, `covered-at-owner`
(with address), `retained-local-delta` or `owner-unresolved`. **A non-empty
ledger without outcomes blocks the next wave and closeout.** The end-to-end
verifier compares baseline with the final corpus and aggregates wave ledgers;
any `missing`/`partial`/`owner-unresolved` blocks closeout. It works from the
pre-cut revision and never sees the executor's self-report.

## Checks that prove nothing

Green link checker · matching headings/anchors/frontmatter · intact field or
row counts · grep instead of `md impact` (misses wikilink/anchor holders).

## Form after the cut

A column or section left with only dashes is form without content — delete it
and keep one owner pointer. An empty-heading section is filled or its inbound
pointers are redirected. An unexplained ID-numbering gap reads as loss and
usually is one.

## Calibration

The goal is zero silent losses, not maximum percent. Systematic verifier
returns mean the corpus holds more of its own truth than «retelling» suggests
— report the result together with the number of returns and their outcomes,
not the reduction alone.
