---
description: "Decision-chain test for MAVO studio adoption, first orders, and retention after trial usage."
depends-on:
  - "[[experiments/prose-audit-lab/docs/RUN-CONTRACT|Run Contract]]"
  - "[[experiments/prose-audit-lab/schemas/source-strength|Source Strength]]"
---

# Studio Adoption And Retention

## Test Metadata

- id: MAVO-STUDIO-03
- class: decision-chain
- oracle: trace-plus-refutation
- required_roles: trace-auditor, studio-skeptic, challenger

## Question

Does the corpus support a decision that studios have a reason to connect, use
MAVO for first orders, and continue after the first trial period?

## Required Chain

1. Studio pain or business job.
2. Why MAVO's current model is better than current alternatives.
3. Which studio segment is being assumed and why.
4. Switching cost / onboarding friction.
5. Retention mechanism after first orders.
6. Risk handling: quality remains with studio, buyer pays studio, MAVO does not
   police production like a marketplace.
7. Primary evidence required to validate adoption and retention.

## Refutation Requirement

The challenger must test whether the chosen studio segment is assumed rather
than earned.

## Passing Standard

Do not treat "small studios" as a fixed premise if the corpus contains or needs
a small-versus-mature-studio decision.
