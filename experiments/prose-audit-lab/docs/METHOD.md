---
description: "Method for running prose audits across domains without pretending coherence is truth."
depends-on:
  - "[[experiments/prose-audit-lab/schemas/artifact-anchor|Artifact Anchor]]"
  - "[[experiments/prose-audit-lab/schemas/case-contract|Case Contract]]"
  - "[[experiments/prose-audit-lab/schemas/source-strength|Source Strength]]"
  - "[[experiments/prose-audit-lab/schemas/verdicts|Verdicts]]"
---

# Method

`prose-audit` is a decision-audit method for prose-heavy artifacts. It is for
places where a normal test suite cannot know the right answer: "will buyers
care?", "does this film premise work?", "does this deck persuade?", "does this
design communicate trust?", "is this business memo grounded?".

## The Central Constraint

The audit must not collapse into:

> "The text is internally coherent, therefore the decision is probably true."

Internal coherence is one useful signal. It is not independent validation.

## Three Working Layers

### 1. Deterministic Layer

Checks that do not require taste:

- input files exist;
- audit questions match the artifact;
- local anchors resolve to in-range, non-blank lines, with an optional verbatim check;
- numbers can be recomputed or marked uncomputed;
- source labels are valid;
- owner approval is present or explicitly missing.

This layer may produce hard failures: `invalid-test`, `missing-anchor`,
`bad-ledger`, `needs-owner-approval`.

### 2. Argument Layer

Checks the reasoning shape:

- claim;
- data / anchor;
- warrant;
- qualifier;
- backing;
- rebuttal;
- strongest defeater.

This layer uses Toulmin-style argument structure, argumentation-scheme critical
questions, and design-rationale practice. It asks whether the evidence actually
supports the claim, not merely whether the text mentions the claim.

### 3. Reader / Reality Layer

Checks what would happen outside the document:

- likely reader reaction;
- missing primary evidence;
- user/customer/viewer/critic proxy signals;
- real observation needed to close the claim.

This layer can propose experiments, interviews, usability tests, A/B tests,
viewer panels, or field checks. It cannot promote simulated agreement to truth.

## Two Axes

Every substantial finding gets two ratings, not one color.

| Axis | Meaning | Example |
| --- | --- | --- |
| `chain_completeness` | Is the argument structurally complete? | missing warrant, complete chain, invalid question |
| `evidence_strength` | How close is support to outside reality? | self-canon, external secondary, primary observation |

A claim may be structurally complete and weakly grounded. That is often the
most important result.

## Heterogeneous Oracles

Use different oracle types for different questions:

| Oracle | Good For | Cannot Prove |
| --- | --- | --- |
| deterministic script | existence, format, line refs, arithmetic, source labels | taste, persuasion, buyer intent |
| traceability auditor | whether the corpus contains the chain | whether the chain is true |
| challenger | strongest defeater and missing alternative | final truth |
| judge | weighing defender vs challenger | reality without evidence |
| reader persona | expected perception | real conversion or adoption |
| external primary evidence | observed behavior, interviews, payments, viewer tests | universal truth |

Same prompt repeated five times is a stability sample, not a heterogeneous
oracle.

## Refutation Posture

For any important claim, the audit must actively ask:

- What would make this claim false?
- Which alternative explanation fits the same evidence?
- Which audience or condition would reject the claim?
- Is the decision under test already smuggled into the premise?

The challenger is not a paragraph inside the defender's answer. It is a separate
artifact or role.

## What Counts As Better Than Yellow

Old single-color verdicts are deprecated. Use:

- `invalid-test` when the question is wrong for the corpus;
- `traceable-self-canon` when support is internal only;
- `traceable-external-secondary` when support is outside but derived;
- `primary-supported` when direct interviews, observations, measurements, or
  artifact-specific evidence exist;
- `reality-closed` only when the agreed reality test has actually run.

Green on `traceability` is allowed only if it is visibly not green on `truth`.

## Minimum Run

For a cheap first pass:

1. Create `cases/<case-id>/inputs/` and a case contract.
2. Create a suite with 1-3 questions.
3. Run deterministic checks.
4. Run one trace auditor and one challenger.
5. Write a report with two axes and a source ledger.

For high-stakes claims, add heterogeneous model families, primary evidence,
reader panels, or domain experts.
