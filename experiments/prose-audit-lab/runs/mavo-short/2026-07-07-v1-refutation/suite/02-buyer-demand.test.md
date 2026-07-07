---
description: "Reader-decision-chain test for MAVO buyer request, trust, and direct studio payment risk."
depends-on:
  - "[[experiments/prose-audit-lab/docs/RUN-CONTRACT|Run Contract]]"
  - "[[experiments/prose-audit-lab/schemas/source-strength|Source Strength]]"
---

# Buyer Demand And Trust

## Test Metadata

- id: MAVO-BUYER-02
- class: reader-decision-chain
- oracle: trace-plus-reader-proxy-plus-refutation
- required_roles: trace-auditor, buyer-skeptic, challenger

## Question

Does the corpus support a plausible chain that a buyer would use a studio's
MAVO vitrine, submit a structured request, and then continue through the
studio-side acceptance/payment path?

## Actor Boundary

The buyer does not press paid `Принять`. The buyer reaches `Отправить заявку`;
the studio later decides `Принять`; MAVO's paid event is studio-side.

## Required Chain

1. Buyer pain or job-to-be-done.
2. MAVO promise to the buyer.
3. Product mechanism that makes the promise concrete.
4. Trust / risk handling for direct studio payment, production, pickup,
   cancellation, defect, and returns.
5. Why the buyer does not simply use chat, marketplace, Kaspi-like flow, or an
   existing studio site.
6. Primary evidence required after launch.

## Passing Standard

If the chain reaches only `Отправить заявку`, say so. Do not promote submitted
request to purchase intent without evidence.
