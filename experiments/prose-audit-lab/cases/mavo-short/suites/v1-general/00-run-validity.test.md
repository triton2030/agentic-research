---
description: "Validity gate for owner inputs, corpus scope, and actor boundary before MAVO audit synthesis."
depends-on:
  - "[[experiments/prose-audit-lab/docs/RUN-CONTRACT|Run Contract]]"
---

# Run Validity And Actor Boundary

## Test Metadata

- id: MAVO-VALIDITY-00
- class: validity
- oracle: deterministic-plus-auditor
- required_roles: auditor

## Question

Are the owner inputs, corpus scope, and audit questions valid enough to run
without silently repairing the test during execution?

## Required Checks

1. Owner intent and criteria approval status.
2. Current corpus boundary versus future/context material.
3. Actor boundary:
   - buyer submits a structured request;
   - studio decides `Принять`;
   - MAVO paid event is created by studio action.
4. Test cards do not smuggle a false premise.
5. Any invalid question returns `invalid-test`, not yellow.

## Passing Standard

The run may continue with draft inputs, but the report must carry
`needs-owner-approval`. Any false actor premise must be named before synthesis.
