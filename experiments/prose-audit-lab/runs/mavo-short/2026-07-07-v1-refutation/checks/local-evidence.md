---
description: "Local deterministic and exact-read evidence collected before agent synthesis."
depends-on: []
---

# Local Evidence

## Corpus State

Command:

```bash
md status /Users/triton/Documents/mavo-short --json
```

Result summary:

- state: `FRESH`
- pending_chunks: `0`
- drift_count: `0`
- excluded by target corpus: `_workspace`, `_ops/plans`, `_ops/findings`,
  `.claude`, `.codex`, and other runtime/scratch folders.

## Current Model Boundary

Source: `/Users/triton/Documents/mavo-short/_ops/GOAL.md:12-14`

The current model is SaaS-vitrine with MAVO catalog, structured request, and
paid `Принять`. Future gallery, buyer choice among studios, marketplace/channel
mechanics, and commission for brought demand live outside current canon.

Source: `/Users/triton/Documents/mavo-short/_ops/GOAL.md:34-42`

Core invariants:

- `Принять` is the paid boundary;
- buyer pays studio directly;
- MAVO is not cashier/seller;
- studio owns production/payment/returns.

## Buyer Actor Boundary

Source:
`/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:31-37`

The buyer gathers and sends a request. The studio decides `Принять`. After
`Принять`, the studio invoices, takes payment, prints, and hands off the
physical order.

Source:
`/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:94-103`

The money flow is split: buyer pays studio for the physical item; studio pays
MAVO for opening print-ready kits on accepted positions.

## Profit Weak Points

Source: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:46-54`

The main chain marks paid `Принять`, direct-payment trust, SKU factory,
economics, solo execution, and defense as `гипотеза` or `допущение`.

Source: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:72-76`

The document names missing proof for the pessimistic unit table, fee pass-through
to studio margin, and the unanswered "why not Kaspi" substitute pressure.

Source: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:52-57`

V/A/B are not quantified: VarOps, catalog amortization, and bad-debt/dispute
buffer remain open.

## Existing Owner Protocol

Source: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/AGENTS.md:39-49`

`Ставка_MAVO.md` already has a due-diligence protocol: skeptical investor
posture, read-only check against canon/outside ground/threshold owners, five
lenses, and invalidity of "идея жива" without the first two lenses.

Implication: the generic prose-audit should be an execution/reporting harness
around this owner protocol for MAVO, not a competing weaker oracle.
