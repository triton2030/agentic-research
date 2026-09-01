---
description: "Design-mode forms for choosing one owner axis and optional views across a second reading axis."
read-when: "Design mode needs a form for new or cross-cutting material; not for existing-surface audit."
---

# Design Patterns

Choose the smallest compositional form that serves the reader action without
creating a second truth.

These patterns nominate candidates. The parent `SKILL.md` operation pair, not
the ladder below, decides whether a candidate improves the bounded surface.

## Start From The Live Axis

Keep the current owner/convention while it still provides a short edit path,
cohesive updates and clear validation. A prettier taxonomy is not evidence for
reorganization.

Two common axes are legitimate:

| Axis | Strong signal |
|---|---|
| Project / feature | Material changes and is validated with one project or feature |
| Domain / capability | One owner compares or updates the material across projects; it has an independent lifecycle/check |

File count, a second reader or one reusable note is only a signal. A separate
axis needs recurring workflow pressure.

## Cohesion And Seam

Keep together what is usually read, changed and checked together. Split only
when the parts have an independent owner, lifecycle, retrieval/update path or
validation. If a reader still needs both parts for the same operation, the seam
may only add hops.

## One Truth, Optional Views

- **Truth** owns durable rules, decisions and updates.
- **View** owns navigation, selection rationale and short synthesis for a
  reading path. It may not introduce competing durable rules.

When two reading axes are regular, choose one truth axis and serve the other
through a view:

| Need | Form | Guardrail |
|---|---|---|
| One cohesive obligation | One file/section at the live owner | No speculative container |
| Independent local owner/lifecycle | Separate owner file or folder | Explicit backlink/route |
| Curated second reading path | MOC or hub with links | Navigation, not copied truth |
| Dynamic filtered set | Generated/Base/query view | Metadata discipline; view remains derived |
| Two stable axes with typed owners | Hub-and-spoke | One side owns truth; the other composes it |

For hub-and-spoke, make direction explicit: the hub names the reading context
and links to owner spokes; each spoke identifies its hub/consumer. Do not
require symmetric folders or reciprocal ownership.

## Decision Ladder

1. One section or file at the live owner.
2. Separate container only after an independent owner/lifecycle/check appears.
3. Truth + view when a second reading axis becomes regular.
4. Dynamic view only when the set changes often enough to justify metadata and
   tooling.

Use [`ia-smell-catalog.md`](ia-smell-catalog.md) when the candidate form shows
duplicate truth, blind atomization, speculative scaffolding, view-as-truth or
taxonomy aesthetics; do not repeat that catalog here.
