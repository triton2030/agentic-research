# Prose Audit Report — MAVO Short — 2026-07-07

Target corpus: `/Users/triton/Documents/mavo-short/`
Harness: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/`

This is a pilot of prose-audit as a traceability audit. It does not prove market
truth. Reality oracle remains pilot / interviews / paid usage.

## Run Summary

| Test | Runs | Raw verdicts | Synthesis |
|---|---:|---|---|
| `PROFIT-01` | 3 | yellow, green-for-traceability, yellow | **yellow** |
| `CUSTOMER-01` | 3 | yellow, yellow, yellow | **yellow** |
| `STUDIO-01` | 3 | yellow, yellow, yellow | **yellow** |

Overall: **yellow**.

The documentation is not a black hole. All three chains are present, owner-
anchored, and mostly falsifiable. But none of the three questions can honestly
be closed as green business truth because the decisive links are still reality-
gated hypotheses.

Reality oracle: **0 / 3 closed**.

## Tool And Execution Evidence

- Native Codex subagents were used: 9 chain-auditor runs.
- Raw outputs are under `runs/2026-07-07/raw/`.
- Raw file count: 9.
- Total raw evidence: 2369 lines.
- `md status /Users/triton/Documents/mavo-short --json` returned `FRESH`,
  with no pending chunks and no active lock at local verification time.
- Several subagents saw transient `md search-read index_busy` during concurrent
  semantic search. They treated it as tooling friction and fell back to direct
  reads via `rg`, `sed`, and `nl`.
- Target corpus stayed read-only. Writes were limited to this audit harness.

## PROFIT-01 — MAVO Can Earn Money

Synthesis verdict: **yellow**.

Traceability: **passes**.
Business proof: **not closed**.

The corpus contains a coherent current profit chain:

- buyer pays the studio for the physical product;
- studio pays MAVO for opening a ready package on accepted positions;
- the paid boundary is `Принять`;
- MAVO is not the checkout, seller, or marketplace commission collector;
- future platform/gallery commission is quarantined outside current canon.

Key anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:23`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:15`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:25`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:56`

Weak links:

- V / A / B are named but not quantified: opening cost, SKU amortization,
  dispute/bad-debt buffer.
- Paid positions per studio/month and mix of fee levels are scenario inputs,
  not measured facts.
- Studio setup/support payback is listed but not priced.
- Fee pass-through to studio margin is unresolved.
- No real paid `Принять` sample exists.

Why yellow, not red:

The chain exists and the gaps are honestly named. There is no material current
commission smuggling.

Why yellow, not green:

The test asks for cost structure, sensitivity, and reality check. Those are
present as formulas and hypotheses, not as measured proof.

## CUSTOMER-01 — Buyers Have A Reason To Use It

Synthesis verdict: **yellow**.

Traceability: **passes**.
Demand proof: **not closed**.

All three auditors converged on the same finding: the buyer chain is coherent,
but direct payment / trust handoff is the weak joint.

The corpus contains a chain:

- buyer wants a personal item without chat chaos;
- MAVO gives a studio-specific storefront, SKU, preview, safe personalization,
  cart/request, stable request link;
- studio later decides `Принять`;
- MAVO paid event is created by studio action, not by buyer checkout.

Key anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:13`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:31`
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Подготовка_к_разработке/Поведение_веб_продукта_L6.md:50`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:16`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:49`

Weak links:

- Direct payment to the studio may break buyer trust.
- The UI/page layer is weaker than the business psychology layer on concrete
  trust mitigations: order ID, invoice/receipt, cancellation-before-print,
  defect/remake path.
- It is not yet proven that buyers prefer this over direct WhatsApp/chat.
- It is not yet proven that studios will not pull the process back into chat
  after request submission.

Harness finding:

The test wording was slightly wrong. It said the buyer reaches the paid
`Принять` boundary. In current MAVO, the buyer reaches `Отправить заявку`; the
studio reaches `Принять`. The correct chain is cross-actor:

`buyer pain -> submitted structured request -> studio accepts -> MAVO paid event`.

## STUDIO-01 — Studios Have A Reason To Connect And Continue

Synthesis verdict: **yellow**.

Traceability: **passes**.
Adoption / retention proof: **not closed**.

The corpus contains a strong studio path:

- studio pain: chat, unpaid prepress, designer/manager load, weak order
  boundaries;
- MAVO value: own storefront, MAVO catalog, structured request, paid file-open
  gate, no marketplace control;
- onboarding: self-serve registration, capability, commercial availability,
  pricing, request fields;
- first order: accept/reject, file opening, paid row, execution remains with
  studio;
- risk boundary: MAVO does not become cashier, seller, quality arbiter, or
  production police.

Key anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_студии.md:10`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Настройка_поверхностей.md:11`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Обработка_заявок.md:12`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Привлечение_студий.md:20`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:100`

Weak links:

- Month-three retention is mostly instrumentation and hypothesis, not an owned
  mechanism.
- Willingness to pay after free openings is unproven.
- Current alternatives beyond direct chat are under-defeated: Kaspi/free
  substitutes, W2P/MIS, simple forms, existing websites.
- First real print-ready package and legal/IP gate remain open.
- Employee/owner operational access still has founder-gap signals in the web
  layer.

Why yellow, not red:

The adoption chain is not missing. It is precise enough to audit and to build a
pilot around.

Why yellow, not green:

The requested "continue after month three" claim is not supported by observed
studio behavior. Current docs contain a retention thesis and metrics, not proof.

## Cross-Test Findings

### F1 — The corpus is better than expected as a black-box target

The documentation can answer all three questions with traceable chains. This is
the strongest result of the pilot. The audit did not collapse into "LLM vibes".
Subagents consistently found current owner files, constraints, and reality gaps.

### F2 — The main failure mode is not contradiction, but reality debt

Most gaps are not "the docs contradict themselves". They are:

- not measured yet;
- explicitly marked hypothesis;
- routed to pilot;
- dependent on first paid usage.

That is a healthy failure mode for this stage.

### F3 — The current/future boundary mostly holds

Profit auditors did not find material future commission smuggling into current
profit logic. Future common gallery / platform commission appears quarantined.

Phrase-level risk remains: terms like "marketplace-like" or "маскировка под
маркетплейс" could confuse a future reader if extracted without boundary lines.

### F4 — Trust/payment is the buyer-side load-bearing gap

The model's core boundary is clean: MAVO is not cashier/seller. But that makes
buyer trust the critical weak link, not a copywriting detail.

The buyer-side chain likely needs a concrete trust handoff card:

- visible studio identity;
- request/order number;
- payment instruction / invoice / receipt expectation;
- cancellation-before-print rule;
- defect/remake responsibility;
- who handles what when something goes wrong.

### F5 — Retention needs an owner-level loop, not just metrics

For studios, the docs measure repeat paid `Принять`, stopped returns, share, and
manual-prepress fallback. That is necessary. It is not yet a retention mechanism.

The missing owner question:

> What exactly makes a studio keep using MAVO in month three after novelty and
> free openings are gone?

## Recommended Next Repair

Do not rewrite the whole corpus. The pilot found three narrow repairs.

1. Update the audit harness wording for `CUSTOMER-01`:
   buyer submits request; studio does paid `Принять`.

2. Add a pessimistic unit table in `Бизнес_Анализ/Расчёт_прибыли.md`:
   fee level, VarOps, catalog amortization, dispute buffer, contribution,
   confidence, measurement method.

3. Add one owner section for studio retention:
   month-three loop, observed signals, what counts as retained, and what means
   "returned to WhatsApp/manual prepress".

Optional fourth repair:

4. Strengthen buyer trust handoff in the relevant buyer/payment/page owner:
   make direct payment mitigations concrete without turning MAVO into cashier.

## Raw Outputs

- `raw/profit-chain.agent-1.md`
- `raw/profit-chain.agent-2.md`
- `raw/profit-chain.agent-3.md`
- `raw/customer-demand-chain.agent-1.md`
- `raw/customer-demand-chain.agent-2.md`
- `raw/customer-demand-chain.agent-3.md`
- `raw/studio-adoption-chain.agent-1.md`
- `raw/studio-adoption-chain.agent-2.md`
- `raw/studio-adoption-chain.agent-3.md`

## Auditor Opinion

The pilot worked. It found a useful middle state: MAVO's prose is not empty or
generic, but it is also not market proof.

I would not spend the next step on more abstract audit framework. The next
highest-value move is to apply the three narrow repairs above, then rerun only
the affected tests. A full suite rerun before those repairs would mostly
reconfirm the same yellow verdicts.

