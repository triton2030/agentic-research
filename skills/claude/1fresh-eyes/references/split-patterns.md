---
description: "Worked examples for splits that look similar but create different decision inputs."
---

# Split Patterns

Read only when fresh-eyes is triggered but the smallest useful split is not
obvious. Core admission and fan-out rules remain in
[`Split И Dialogue`](../SKILL.md#split-и-dialogue); these examples only resolve
borderline cases.

## Two Roles, One Artifact

A pricing proposal may need `business-critic` for willingness-to-pay and
`developer-critic` for delivery cost. The first can reverse the offer; the
second can reverse feasibility. Give each role its own question and reversal
result. Shared artifact does not make the products duplicate.

The zones differ even though the artifact is shared: willingness-to-pay lives in
customer evidence, comparable offers and unit economics, delivery cost lives in
the code path, dependencies and operational load. The proposal page is context
for both and the main entry for neither.

## One Role, Disjoint Artifacts

Five unrelated adapters may be split across several `developer-critic` agents
when each adapter can fail independently. This is parallel evidence production
inside one lens, not several professional votes on the same claim.

## Critic Plus Scout

When an `architecture-critic` needs corpus-wide ownership evidence, run a
separate `md-scout` for addresses, actual coverage and gaps. The scout does not
confirm the architecture verdict; main verifies the packet and returns the
supported evidence to the decision.

## False Split

“Frontend risk” and “backend risk” can look like different lenses while both
questions are implementation feasibility. If they concern one coupled change,
use one `developer-critic`; if they are genuinely independent artifacts, split
by artifact without treating agreement as stronger proof. The swap test catches
this before spawn: either brief reads correctly in the other agent's hands.
