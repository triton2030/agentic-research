---
description: "Corrected MAVO prose-audit report using claim-status matrix instead of single-color verdict."
depends-on:
  - run.md
  - evidence-ledger.tsv
  - checks/local-evidence.md
  - raw/md-scout.md
  - raw/business-critic.md
  - raw/architecture-critic.md
---

# Prose Audit Report — MAVO Short — v1 Refutation

Target corpus: `/Users/triton/Documents/mavo-short/`

Run: `2026-07-07-v1-refutation`

## Verdict

MAVO's documents are **business-auditable**. The business is **not proven**.

The corrected audit does not return an overall `yellow`. That would repeat the
v0 failure. The useful result is a matrix:

- current/future boundary: traceable;
- buyer/studio/money actor boundary: traceable;
- profit model: structurally described, not decision-supported;
- buyer demand/trust: plausible, not demand-proof;
- studio adoption/retention: owner hypothesis, not validated audience decision;
- small-studio wedge: current chosen corridor, not earned by primary evidence.

## Run Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| owner/input approval | `needs-owner-approval` | case inputs are `.draft.md` |
| corpus freshness | `pass` | `md status` returned `FRESH`, pending/drift/stale `0` |
| test validity | `pass-with-warning` | v1 suite fixes v0 buyer/`Принять` actor error |
| refutation | `pass` | `raw/business-critic.md`, `raw/local-defender.md` |
| source-strength ledger | `pass-with-warnings` | decision-ground rows are intentionally weak `self_canon` |
| primary reality | `reality-open` | no live buyer/studio/pilot evidence in this run |

## Claim-Status Matrix

| Claim | Chain Completeness | Evidence Strength | Decision Status | Reality Open | Cheapest Disconfirming Test |
| --- | --- | --- | --- | --- | --- |
| Current/future boundary | `complete` | `self_canon` | `supported-as-canon` | no | N/A unless owner changes GOAL |
| Actor/money boundary | `complete` | `self_canon` | `supported-as-canon` | no | N/A unless product/payment design changes |
| Current profit model | `partial/complete` | `self_canon` + model skeleton | `decision-risk` | yes | pessimistic unit table + V/A/B + 20-30 accepted paid positions |
| Buyer demand/trust | `partial` | `self_canon` + derived/external risk proxies | `decision-not-supported` | yes | observed funnel through submit -> studio accept -> direct payment does not break |
| Studio adoption/retention | `partial` | `self_canon` + derived proxies | `decision-not-supported` | yes | 3-5 published vitrines, 2+ real shares, repeat paid `Принять` after free openings |
| Small-studio first wedge | `partial` | `self_canon` + conflicting external proxy | `owner-hypothesis` | yes | segment duel with primary calls / pilot by segment |

## What Is Actually Supported

### 1. Current / Future Boundary

The current model is a SaaS studio vitrine with MAVO catalog, structured
request, and paid `Принять`. Future marketplace/gallery/commission logic is out
of current canon.

Evidence:

- `_ops/GOAL.md:12-14`
- `_ops/GOAL.md:34-42`
- `evidence-ledger.tsv` rows `MAVO-GATE-003`, `MAVO-GATE-004`

Status: `supported-as-canon`.

This is not market proof. It is a clean scope boundary.

### 2. Buyer / Studio / Money Actor Boundary

The v0 audit asked the buyer chain as if the buyer reached paid `Принять`.
That was wrong. The v1 suite fixes it:

- buyer reaches `Отправить заявку`;
- studio decides `Принять`;
- MAVO paid event is studio-side;
- buyer pays studio directly;
- MAVO is not cashier/seller.

Evidence:

- `_Путь_покупателя.md:31-37`
- `_Путь_покупателя.md:94-103`
- `raw/md-scout.md`

Status: `supported-as-canon`.

## What Is Not Supported

### 3. Current Profit Model

The documents contain a coherent profit skeleton. They do not support the
decision claim "this profit model works."

Reasons:

- paid `Принять` is marked as `гипотеза`;
- V/A/B are not quantified;
- break-even depends on `V+A+B <= 40%`;
- fee pass-through to studio margin is unproven;
- "why not Kaspi" is explicitly unwritten;
- no 20-30 accepted paid-position sample exists.

Evidence:

- `Ставка_MAVO.md:46-54`
- `Ставка_MAVO.md:72-76`
- `Расчёт_прибыли.md:52-57`
- `Расчёт_прибыли.md:83-89`
- `raw/business-critic.md`

Decision status: `decision-risk`.

Better wording: **profit is structurally modeled, not validated.**

### 4. Buyer Demand And Trust

The corpus supports a plausible buyer JTBD: short path to a personal product
without painful chat. It does not prove demand.

The load-bearing risk is not only UI clarity. It is trust at direct payment:
the buyer pays the studio, not MAVO. If that handoff feels unsafe, the chain
breaks after the request.

Evidence:

- `Проверка_пилота.md:16-25`
- `Проверка_пилота.md:87-99`
- `Доверие_покупателя_к_студии.md` findings from `raw/md-scout.md`
- external substitute/risk references in `evidence-ledger.tsv` rows
  `MAVO-EXT-001`, `MAVO-EXT-002`

Decision status: `decision-not-supported`.

Better wording: **plausible JTBD, not demand-proof.**

### 5. Studio Adoption And Retention

The corpus names why studios might try MAVO: less chat/prepress, ready SKU,
structured request, pay only on accepted/opened positions. It does not prove
that studios will keep using it after trial openings.

Open risks:

- willingness to pay after free openings;
- return to WhatsApp/manual prepress;
- founder-touch onboarding;
- retention based on workflow advantage, not structural lock;
- segment fit by size and operational maturity.

Evidence:

- `Проверка_пилота.md:35-43`
- `Проверка_пилота.md:100-112`
- `raw/md-scout.md`
- `raw/business-critic.md`

Decision status: `decision-not-supported`.

Better wording: **adoption thesis is explicit, retention unproven.**

### 6. Audience Decision Duel

The chosen wedge is micro/small studios in one city. The audit does not validate
that this is the best first segment.

The current evidence supports a narrower claim:

> small studios are the current owner-chosen working corridor.

It does not support:

> small studios are proven to be the best first buyers.

The external/derived evidence also warns that the smallest studios may have the
highest pain but lower ability to pay, weaker process discipline, and weaker
retention.

Decision status: `owner-hypothesis`.

Cheapest next check: compare micro/small versus mature W2P/MIS-capable studios
on pain, willingness to pay, activation friction, traffic, and retention in
primary calls or a split pilot.

## v0 Failure Map

| v0 Failure | v1 Mechanism | Evidence It Fired |
| --- | --- | --- |
| MAVO-specific folder | renamed to `prose-audit-lab`; MAVO moved under `cases/` and `runs/` | `README.md`, `cases/mavo-short/` |
| single-color `yellow` summary | claim-status matrix; no overall color | this report |
| buyer `Принять` actor error | explicit actor boundary in suite and report | `suite/02-buyer-demand.test.md` |
| Kaspi missed in profit | substitute pressure required in profit suite and report | `suite/01-profit-current-model.test.md`, ledger `MAVO-PROFIT-004` |
| self-canon treated too strongly | source-strength ledger and warnings for weak decision-ground | `evidence-ledger.tsv`, `check_run.py` |
| no separate refutation | business critic + local defender + main judge | `raw/business-critic.md`, `raw/local-defender.md` |
| Markdown-only anchor model | artifact-anchor schema added | `schemas/artifact-anchor.md` |
| gates as prose only | role manifest + validator | `role-manifest.tsv`, `scripts/check_run.py` |

## Lab Architecture Note

Architecture critic accepted the central model but found a real risk: the lab
was still too Markdown/MAVO-shaped. That is now partially repaired:

- `schemas/artifact-anchor.md` introduces modality + locator contracts;
- `schemas/case-contract.md` introduces artifact/decision taxonomy;
- `case-contract.md` for MAVO states this case only validates
  `markdown_corpus`;
- `check_run.py` validates ledger modality/locator and role manifest.

Residual architecture risk remains: the lab still needs a non-MAVO visual or
landing-page case before claiming cross-domain validation.

## Acceptance Audit

The first acceptance audit failed the run because the auditor role was still
pending, run metadata was stale, and subagent execution evidence was not
attached inside the run folder.

Those blockers were resolved after the audit:

- `raw/auditor.md` preserves the failed audit output;
- `checks/auditor-resolution.md` records the fixes;
- `checks/subagent-execution.md` records native subagent ids and raw files;
- `role-manifest.tsv` marks the roles completed.

Remaining checker warnings about `self_canon` decision-ground are intentional:
they are the audit result, not a metadata defect.

## Final Line

The corrected MAVO result:

> Documents are business-auditable; business is not yet proven.

Do not build confidence from same-family LLM convergence. Build confidence by
closing named reality gates: pessimistic economics, substitute positioning,
buyer direct-payment trust, studio willingness to pay, retention, and audience
segment proof.
