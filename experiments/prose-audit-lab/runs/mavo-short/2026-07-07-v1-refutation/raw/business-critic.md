# Business Critic Raw Output

Verdict: `better_path_found`

## Finding 1 — Avoid A Better-Looking v0

The current route could still make "best v0": traceability cleaner, but business
claims still reported as `yellow/plausible`.

Evidence:

- The run states `Primary reality: none` and `reality-open`.
- The contract says missing primary/reality evidence cannot close market truth.
- Source schema says `self_canon` does not make a high-stakes claim true.
- At review time `check_run.py` failed because `report.md` was missing,
  `raw/` was empty, and `decision_ground` rows used weak `self_canon`.

Alternative: final format should be a claim-status matrix:
`chain_completeness`, `evidence_strength`, `decision_status`, `reality_open`,
`cheapest_disconfirming_test`.

Demand: prohibit general `yellow` summary. For each claim, write `traceable but
unsupported by reality` or `decision-not-supported until X`.

## Finding 2 — Current Profit Claim Unsupported

This is not "profit exists"; it is "there is a formula and named kill gates".

Evidence:

- `_ops/GOAL.md:34-42` defines paid `Принять`, direct studio payment, and MAVO
  not as cashier.
- `Ставка_MAVO.md:46-54` marks key links as `гипотеза/допущение`.
- `Расчёт_прибыли.md:52-57` leaves V/A/B unquantified.
- `Расчёт_прибыли.md:83-89` depends on `V+A+B <= 40%`.
- `Ставка_MAVO.md:72-76` names missing pessimistic unit table, fee
  pass-through, and "why not Kaspi".

Alternative: `profit_current_model = chain partial/complete; evidence
self_canon; decision-risk or decision-not-supported; reality-open`.

Demand: before `profit-supported`, require pessimistic unit table for
300/700/1500 KZT, V/A/B, margin pass-through, Kaspi/free substitute answer, and
20-30 accepted paid-position sample.

## Finding 3 — Buyer Demand / Trust Not Proven

Trust is not a UX detail; it is a load-bearing business risk.

Evidence:

- `_Путь_покупателя.md:31-37`: buyer sends request, studio does `Принять`.
- `_Путь_покупателя.md:94-103`: buyer pays studio directly; MAVO does not hold
  buyer money.
- `Проверка_пилота.md:16-25` and `87-99`: need proof of the route through
  request, studio decision, paid `Принять`, and downstream signal.
- Kaspi has relevant substitute surfaces, including examples for custom mug and
  T-shirt printing.

Alternative: buyer claim should be `plausible JTBD, not demand-proof`.

Demand: require trust-handoff evidence: order number, invoice/receipt
expectation, cancellation-before-print, defect/remake responsibility, and
observed drop-off at direct payment.

## Finding 4 — Studio Adoption / Retention Is Still Owner Hypothesis

Evidence:

- `Что_такое_MAVO.md:52-58` chooses small studios in one city.
- `Проверка_пилота.md:35-43` marks segment ladder as `гипотеза`.
- `Проверка_пилота.md:100-112` leaves willingness to pay, adoption bottleneck,
  WhatsApp fallback, breakeven, and channel open.
- `Привлечение_студий.md:16-18` calls visible PLG a hypothesis and says growth
  relies on leverage channels.

Alternative: `audience_decision = owner hypothesis requiring primary evidence`.
Compare micro-studio vs mature W2P/MIS-capable studio by pain, willingness to
pay, activation friction, buyer traffic, and retention likelihood.

Demand: report must include decision-duel result: small studios are the current
chosen wedge, but not earned until 3-5 published vitrines, 2+ real shares, 20+
submitted or 3+ accepted in one category, and paid usage after free openings.

## Finding 5 — Generic Harness Must Not Weaken MAVO Owner Protocol

Evidence:

- `Бизнес_Анализ/AGENTS.md:39-49` already requires due-diligence posture,
  outside market, economics, and kill-check.
- `RUN-CONTRACT.md` requires `needs-owner-approval`, `reality-open`, and
  `refutation-gap`.

Alternative: treat prose-audit as reporting/execution harness around MAVO's
`Ставка_MAVO` protocol, not replacement.

Demand: corrected report must explicitly say all four business claims remain
unsupported as reality claims. Supported: current/future boundary, actor/money
boundary, hypothesis map, and validation gates.

## Bottom Line

The v1 suite direction holds only if the report refuses comfort. Corrected MAVO
result should say: documents are business-auditable; business is not yet proven.
