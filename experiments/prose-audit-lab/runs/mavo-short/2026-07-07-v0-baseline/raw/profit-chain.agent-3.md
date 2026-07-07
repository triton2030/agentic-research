# PROFIT-01 raw audit — agent-3

Verdict: **yellow**

Коротко: current SaaS-витрина держит трассируемую цепь выручки без опоры на future marketplace/commission logic: студия платит MAVO за открытый комплект по принятой позиции, покупатель платит студии напрямую, комиссия в собственном канале = 0%. Но до green не дотягивает cost/profit слой: модель честно называет VarOps, амортизацию SKU, bad debt, setup/support и studio acquisition, но ключевые стоимости не оцифрованы. Это не конфликт и не future-smuggling, а недосчитанный unit-economics gap.

## Scope and tool coverage

- Target corpus: `/Users/triton/Documents/mavo-short/`.
- Harness: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/`.
- Test: `suite/profit-chain.test.md`.
- Primary corpus boundary confirmed in `corpus.md`: current corpus includes `README.md`, `AGENTS.md`, `_ops/GOAL.md`, `_context-base/*.md`, `Данные_снаружи/*.md`, `01_Описание_бизнеса/**/*.md`, `02_Веб_приложение/**/*.md`, `03_Создание_загрузка_дизайнов/**/*.md`, `Бизнес_Анализ/**/*.md`; `04_Доп_проекты/**/*.md` is secondary/context-only and future-only material must not be promoted into current canon.
- `md status /Users/triton/Documents/mavo-short --json`: state `FRESH`, index exists, no drift, excluded scope includes `_workspace/*`, `_ops/plans/*`, `_ops/findings/*`, `.claude/*`, `.codex/*`.
- Reads used: root `README.md`, `AGENTS.md`, `_ops/GOAL.md`; local `AGENTS.md` for `01_Описание_бизнеса`, `01_Что_такое_МАВО`, `03_Как_это_работает`, `04_Как_запускаем`, `Бизнес_Анализ`, `04_Доп_проекты`, `04_Доп_проекты/Будущее`; owner files listed below. Target corpus was not edited.

## Chain links

### 1. Current revenue source

- Claim: MAVO earns in the current model from the studio, not from the end buyer: the paid event is `Принять`, when MAVO opens print-ready kits for accepted positions.
- Data anchor:
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8` defines MAVO as a Web-to-Print SaaS / white-label storefront; studio remains seller/executor; MAVO opens print-ready kits on `Принять`.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:38-50` says buyer pays studio, studio pays MAVO for accepted positions; paid boundary is `Принять`, not submitted request and not `Оплачено`.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10-23` states the money rule and diagram: buyer -> studio for product; studio -> MAVO for opening kit per position.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория.md:10-21` says buyer pays studio, studio pays MAVO; MAVO earns on the studio, not the buyer.
- Warrant: The same rule appears in first business answer, finance owner, and audience owner; the finance owner is explicitly routed as the owner of product money.
- Qualifier: current canon / product rule.
- Rebuttal or defeater: no valid `Принять` -> no file opening and no paid MAVO line; if studios do not pay after trial openings, the wedge fails.

### 2. Amount / pricing corridor

- Claim: Current pricing mechanism is a fixed service fee per accepted position / opened kit, not subscription and not commission; levels are 300 / 700 / 1500 KZT by design complexity.
- Data anchor:
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:15-26` defines the fee and levels: simple 300 KZT, medium 700 KZT, expensive 1500 KZT.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:32-40` says the fee is charged on `Принять`, except free corridor, insufficient balance, no accept, or confirmed MAVO error.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Экономика_заказа.md:9-21` marks all numbers as `гипотеза` or `рабочий коридор`; service fee levels are canon, free openings and minimum top-up are corridors/hypotheses.
  - `/Users/triton/Documents/mavo-short/_context-base/CTX-028_Сбор_предоплата_цены_студии.md:22-42` compresses the monetary frame: fixed fee by design level, not percent of buyer price, prepaid balance, studio controls final buyer price.
- Warrant: Pricing is anchored in the finance detail file and repeated through CTX compression; the corpus separates canonical fee levels from not-yet-proven economics.
- Qualifier: fee levels are current canon; free openings and minimum top-up are working corridor/hypothesis; not public offer.
- Rebuttal or defeater: if fixed levels do not cover AI/interactive cost, or studios do not understand/accept the three levels, CTX-028 says the frame is revisited.

### 3. Cost structure

- Claim: The corpus names the expected cost buckets for one paid opening/order and one studio/channel, but does not yet quantify the most important variable costs.
- Data anchor:
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:50-64` lists variable costs per paid opening: VarOps, catalog amortization, bad debt/disputes; and fixed monthly costs: tools 25,000-50,000 KZT, hosting 10,000-25,000 KZT, acquiring 2-3.5%, founder time.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:91-98` says the model needs V, A, B, coefficient from units to paid positions, and real level mix to be quantified.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Экономика_каналов.md:12-23` rejects "zero CAC": onboarding, support, catalog creation, and narrow advertising/local channels cost MAVO money and time.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Экономика_каналов.md:35-45` lists counting positions: contribution per accepted request, CAC per registered/published studio, amortized studio acquisition cost per paid `Принять`, cost per published SKU, support per published studio, payback of acquisition + setup/support.
- Warrant: Cost categories cover both per-order and per-studio/channel economics, but the file itself says the dangerous numbers are unknown.
- Qualifier: partial / hypothesis / unquantified; fixed monthly costs have rough ranges, V/A/B do not.
- Rebuttal or defeater: if V + A + B exceeds the service fee, unit contribution is negative; if setup/support depends on founder heroics, channel economics are not scalable.

### 4. Unit or period economics

- Claim: The corpus can express unit and monthly economics as formulas and scenarios, but only as a model skeleton until V/A/B, real paid-position volume, and mix are measured.
- Data anchor:
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:25-31` defines paid unit as an opened position, not physical item; personalization can multiply positions.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:33-48` gives monthly revenue formula and scenarios: pessimism 6,800 KZT/month, base 27,000 KZT/month, optimism 62,000 KZT/month per studio.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:65-75` gives unit contribution formula and warns that if fee is below V/A/B, volume accelerates losses.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:76-89` gives break-even formula and illustrative break-even: base 3-4 studios, pessimism 12-13, optimism 2, under the assumption V/A/B <= 40% of fee and fixed costs 50,000 KZT/month.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:64-79` explicitly lists the missing economic proof: pessimistic unit table, V/A/B, payback threshold, fee pass-through to studio margin.
- Warrant: Profit chain is internally computable as a formula, and the corpus names what is not yet known instead of pretending the profit is proven.
- Qualifier: model skeleton; scenario assumptions; idea alive but unproven.
- Rebuttal or defeater: negative contribution, high V/A/B, low accepted/submitted, poor paid-position volume, or fees eating studio margin breaks the economics.

### 5. Sensitivity / kill conditions

- Claim: The corpus has explicit kill/sensitivity rules for monetization and economics.
- Data anchor:
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:46-54` lists the business chain, including paid `Принять`, trust in direct payment, and economics as hypotheses.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:56-63` gives kill criteria: studios do not pay after trials, contribution remains negative, insufficient sample is not market verdict, pessimistic unit table fails, direct payment breaks trust.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:60-69` maps pilot outcomes, including `pivot economics` when VarOps, catalog cost, or studio acquisition eat the service fee.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Экономика_каналов.md:21-33` says the channel is viable only when acquisition cost is below contribution; B2B expansion triggers are hypotheses until real requests/payments.
- Warrant: The corpus does not merely say "we will earn"; it states which assumptions can kill the model and where to pivot.
- Qualifier: hypotheses until pilot data.
- Rebuttal or defeater: a weak sample is not a kill; first repair activation/share/trust before judging market demand.

### 6. Reality check / cheapest experiment

- Claim: The cheapest next proof is not building the whole marketplace or full web product; it is pre-pilot/pilot evidence around factory cost, print-ready fit, paid `Принять`, and pessimistic unit table.
- Data anchor:
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:80-82` says the cheapest next proof is a pre-pilot packet: manual factory run, print-ready trial with first studio, and pessimistic unit table across fee levels.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-31` defines the first accepted request with paid position.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Пилот.md:32-52` gives a minimal path: one city, 3-5 studios, 20-50 designs in 1-2 categories, shared storefronts, first request, then accept/opening/paid record.
  - `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:45-58` gives go/no-go sample and economic sample: 3+ storefronts, 2+ sharing studios, 20+ submitted or 3+ accepted in one studio/category, plus 20-30 accepted requests for economic sample.
  - `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:57-60` defines product money events: paid `Принять`, write-off rows, free openings, balance top-ups, source of request.
- Warrant: The reality check measures weakest links directly: willingness to pay, contribution, SKU cost, support, and accepted requests, without invoking future marketplace demand.
- Qualifier: pre-pilot/pilot hypothesis test, not business proof.
- Rebuttal or defeater: if sample is insufficient, the verdict is insufficient sample; if accepted requests exist but economics are negative, pivot economics before scaling.

## Missing or weak links

1. **V/A/B not quantified.** The profit model has the correct buckets, but VarOps, SKU creation/amortization, bad debt/disputes are explicitly "not quantified" in `/Бизнес_Анализ/Расчёт_прибыли.md:52-57` and are the central reason for yellow.
2. **Studio setup/support payback not quantified.** `/Бизнес_Анализ/Экономика_каналов.md:39-45` names CAC, support per published studio, and acquisition + setup/support payback, but does not provide numbers or thresholds.
3. **Fee pass-through to studio margin is unresolved.** `/Бизнес_Анализ/Ставка_MAVO.md:73-75` says medium/expensive levels may eat studio margin or require raising buyer price; this is a real economic weak point, not a wording issue.
4. **No final pessimistic unit table.** The corpus asks for it in `/Бизнес_Анализ/Ставка_MAVO.md:72-73` and `/Бизнес_Анализ/Расчёт_прибыли.md:91-98`; until it exists, green would overstate internal calculability.

## Conflicts / future-smuggling

Verdict: **no material future-smuggling into the current profit chain**.

- Current canon blocks commission: `/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:25-32` says MAVO does not charge for acquisition in the studio's own channel; commission = 0%, revenue remains service fee.
- Contract repeats the same boundary: `/01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:29-36` says "your storefront, your client, your money"; buyer pays studio directly, MAVO earns via service fee.
- Future owner is explicit: `/04_Доп_проекты/Будущее/AGENTS.md:21-47` says future-only ideas must not govern current canon and Post-MVP gallery/commission has a Promotion Rule.
- Future money file is well-contained: `/04_Доп_проекты/Будущее/Этап-3/Post-MVP_общая_галерея/Деньги_и_комиссия.md:10-35` says future commission appears only if MAVO brings demand via platform channel; 12% is not MVP/current/public offer.
- Future hub confirms separation: `/04_Доп_проекты/Будущее/Этап-3/Post-MVP_общая_галерея/Post-MVP_общая_галерея.md:20-40` contrasts current service fee vs future service fee + possible commission.
- Search over current primary corpus found commission/marketplace mentions mostly as boundaries, UX analogies, or future routing, not as current revenue. The risky phrase "маскировка под маркетплейс" appears in UI/product context, but it does not introduce commission logic into current profit.

## Reality gap

The documentation is internally coherent enough to show how MAVO *could* earn under the SaaS-vitrine model, but it does not prove that it *will* earn.

- `/Бизнес_Анализ/Ставка_MAVO.md:80-82` verdict: idea is alive, not proven; risk moved to positioning and economics.
- `/Бизнес_Анализ/Ставка_MAVO.md:68-79` lists the exact proof gaps: no factory run, no print-ready contract, no minimal pipeline, no pessimistic unit table, no fee pass-through proof, no legal/IP gate, no measured wedge.
- `/Бизнес_Анализ/Проверка_пилота.md:45-58` requires real pilot sample before hard inference.
- Therefore yellow is not "docs incoherent"; yellow is "traceable current chain with declared economic unknowns that still block a green profit-chain verdict."

## Final auditor opinion

PROFIT-01 passes the **current/future boundary** and mostly passes **traceability**. It fails full green on **cost calculability**. The strongest part is the repeated owner-consistent revenue rule: service fee per accepted/opened position. The weakest part is exactly where it should be weak at this stage: no measured V/A/B, setup/support payback, or fee pass-through. The right repair is not to mention marketplace less; it is to add the pessimistic unit table and pilot measurement thresholds at the existing owners.
