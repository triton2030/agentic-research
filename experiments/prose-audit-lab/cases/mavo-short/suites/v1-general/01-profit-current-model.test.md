---
description: "Decision-chain test for whether the current MAVO model can support profit without future marketplace logic."
depends-on:
  - "[[experiments/prose-audit-lab/docs/RUN-CONTRACT|Run Contract]]"
  - "[[experiments/prose-audit-lab/schemas/source-strength|Source Strength]]"
---

# Current Model Profit

## Test Metadata

- id: MAVO-PROFIT-01
- class: decision-chain
- oracle: deterministic-trace-plus-refutation
- required_roles: trace-auditor, challenger, judge

## Question

Does the current MAVO model have a decision-supportable path to profit without
using future marketplace/gallery/commission logic?

## Required Chain

1. Who pays MAVO and for what.
2. Current price / fee corridor and its status: fact, canon decision,
   hypothesis, assumption, or measured reality.
3. Direct and indirect cost buckets.
4. Unit or period economics under pessimistic assumptions.
5. Substitute pressure: why a studio pays MAVO instead of using free / cheaper
   alternatives, including Kaspi-like channels when present in the corpus.
6. Kill conditions and cheapest primary evidence.

## Refutation Requirement

A challenger must state the strongest reason this profit path fails even if the
internal money chain is coherent.

## Passing Standard

The report must separate:

- `chain_completeness`;
- `evidence_strength`;
- `decision_status`;
- `reality_open`.

`self_canon` pricing can support traceability, not truth.
