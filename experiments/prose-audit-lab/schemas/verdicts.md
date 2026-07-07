---
description: "Verdict vocabulary for prose-audit runs."
depends-on:
  - "[[experiments/prose-audit-lab/schemas/source-strength|Source Strength]]"
---

# Verdicts

Use controlled verdicts. Avoid a single green/yellow/red unless the axis is
named.

## Validity

| Verdict | Meaning |
| --- | --- |
| `valid` | question matches artifact and corpus |
| `invalid-test` | question is wrong or smuggles a false premise |
| `needs-owner-approval` | inputs are draft / not confirmed |
| `out-of-scope` | question asks for evidence outside declared corpus |

## Chain Completeness

| Verdict | Meaning |
| --- | --- |
| `complete` | claim, data, warrant, qualifier, rebuttal, and reality gap are named |
| `partial` | chain exists but one or more links are weak |
| `missing-link` | important link is absent |
| `circular` | claim mostly rests on its own restatement |

## Evidence Strength

Use source-strength labels from [Source Strength](source-strength.md).

## Decision Status

| Verdict | Meaning |
| --- | --- |
| `decision-supported` | argument survives challenger and has sufficient evidence for this decision price |
| `decision-risk` | plausible, but one or more high-cost assumptions remain weak |
| `decision-not-supported` | defeater or missing evidence blocks the decision |
| `reality-open` | no real-world observation yet; next validation named |

## Deprecated

`green`, `yellow`, and `red` are allowed only inside a named axis:

- `traceability: green`;
- `decision: yellow`;
- `reality: red/open`.

Never write plain "overall green" for a prose artifact unless the report also
states which reality test was actually passed.
