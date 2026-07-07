# PROFIT-01 raw audit - agent-1

Target corpus: `/Users/triton/Documents/mavo-short/`
Harness: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/`
Test: `suite/profit-chain.test.md`
Auditor: independent Chain Auditor, read-only target corpus

## Verdict

**YELLOW.**

The corpus holds a traceable current-model profit chain: MAVO is a Web-to-Print / white-label SaaS storefront, the buyer pays the studio, the studio pays MAVO for opening print-ready kits on accepted positions at `Принять`, and future marketplace / commission logic is explicitly parked outside current canon.

It is not green because the profitability side is still a quantified skeleton, not a completed model. Revenue mechanics and fee tiers are clear; cost and unit economics are routed and named, but the dangerous variables `V/A/B` and cost-to-serve per active/published studio are not measured. The docs say this honestly, so the state is not red.

## Tooling and corpus boundary

- `md status /Users/triton/Documents/mavo-short --json` ended `FRESH`, `pending_chunks: 0`, no `NO_INDEX` / `NEEDS_WARMUP`.
- First `md search-read` attempt hit `index_busy`; I recorded this as transient tool friction and continued with `rg` / direct `nl` reads.
- Later `md search-read` succeeded and returned the same owner cluster: `Бизнес_Анализ/Расчёт_прибыли.md`, `01_Описание_бизнеса/04_Как_запускаем/Стратегия_запуска.md`, and money-owner files.
- Primary current corpus scope came from harness `corpus.md`: root docs, `_context-base`, `Данные_снаружи`, `01_Описание_бизнеса`, `02`, `03`, `Бизнес_Анализ`; `04_Доп_проекты` is secondary/context-only and future-only material must not be promoted.
- Target corpus was not edited.

## Chain Links

### 1. Current model and revenue source

**Claim:** In the current model MAVO earns from studios, not buyers: studio pays MAVO for accepted positions / opened print-ready kits at `Принять`.

**Data anchor:**
- `README.md:43-47` fixes the current frame as studio SaaS-vitrine and warns that money / paid request contradictions need owner verification.
- `_ops/GOAL.md:12-14`, `34-41` sets current model and core: buyer pays studio directly; MAVO is not the seller/cashier; `Принять` is the paid file gate.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8-19`, `38-50`, `70-77`.
- `01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10-23`.
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:94-103`.
- `_context-base/CTX-013_Принять_открывает_файл.md:19-30`.

**Warrant:** Multiple current owners describe the same money event: `Принять` fixes the snapshot, opens the kit, and creates MAVO's paid event. This is stronger than a single isolated sentence.

**Qualifier:** Current canon / accepted model, not market proof.

**Rebuttal / defeater:** No valid `Принять`, no open kit, free opening, insufficient balance, or confirmed MAVO error means no paid MAVO event.

### 2. Amount / pricing corridor

**Claim:** Current monetization is a fixed service fee per opened kit / accepted position, with three fee levels: `300 / 700 / 1500 ₸`; free openings and minimum top-up are working hypotheses/corridors.

**Data anchor:**
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:15-26`, `32-39`, `41-53`.
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Экономика_заказа.md:9-21`, `25-27`.
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Кредитная_система.md:14-25`, `36-41`.
- `_context-base/CTX-022_Плата_по_позициям.md:20-31`, `33-41`.
- `_context-base/CTX-028_Сбор_предоплата_цены_студии.md:22-42`.

**Warrant:** The fee amount is not inferred from future marketplace pricing; it is stated directly in the current financial owner and repeated in the current context compression layer.

**Qualifier:** Fee levels are canon; free openings and minimum refill are `рабочий коридор` / `гипотеза`.

**Rebuttal / defeater:** The fee is not a subscription, not a commission from buyer price, not a surface fee, and not one fee per whole multi-position request.

### 3. Money boundary: no current commission

**Claim:** The current SaaS-vitrine model does not rely on marketplace commission or platform demand commission.

**Data anchor:**
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:31-36`, `56-69`.
- `01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:25-31`.
- `01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Карта_рубежей.md:15-21`, `23-30`.
- `04_Доп_проекты/Будущее/Этап-3/Общая_галерея_и_платформенный_канал.md:29-34`.
- `04_Доп_проекты/Будущее/Этап-3/Post-MVP_общая_галерея/Деньги_и_комиссия.md:10-35`.

**Warrant:** Current owners say own-channel commission is `0%`; future owner says future commission appears only in platform channel if MAVO brings demand.

**Qualifier:** Current canon. Future commission is a future-only hypothesis.

**Rebuttal / defeater:** If MAVO starts bringing buyers through a common gallery / platform channel, the current own-channel rule no longer answers that case; future promotion would be required.

### 4. Cost structure

**Claim:** The corpus names the relevant cost structure, but does not yet quantify the most important variables.

**Data anchor:**
- `Бизнес_Анализ/Расчёт_прибыли.md:50-63` lists variable costs `V/A/B` and fixed monthly costs.
- `Бизнес_Анализ/Расчёт_прибыли.md:65-74` gives unit contribution formula.
- `Бизнес_Анализ/Экономика_каналов.md:12-23`, `35-45` names onboarding, support, catalog, CAC, setup/support per studio, and manual operations as count positions.
- `Бизнес_Анализ/Выгода_студии_в_цифрах.md:11-23` gives studio-side cost/margin proxy, useful for willingness-to-pay but not MAVO's own cost proof.

**Warrant:** The chain does not hand-wave costs: it separates per-order variable cost, catalog amortization, bad-debt/dispute buffer, fixed tooling/hosting, acquisition/setup/support, and founder time.

**Qualifier:** `гипотеза` / `допущение`; V, A, B are explicitly "not quantified".

**Rebuttal / defeater:** If V+A+B exceeds the fixed service fee at realistic paid volume, revenue growth accelerates loss.

### 5. Unit / period economics

**Claim:** The corpus has a period-economic model and break-even scenarios, but they depend on an unvalidated assumption that V+A+B consume <= 40% of fee.

**Data anchor:**
- `Бизнес_Анализ/Расчёт_прибыли.md:25-31` defines paid unit as opened position, not physical item.
- `Бизнес_Анализ/Расчёт_прибыли.md:33-48` gives revenue/studio/month scenarios: 6,800 / 27,000 / 62,000 ₸.
- `Бизнес_Анализ/Расчёт_прибыли.md:76-89` gives contribution and break-even: base ~3-4 studios, pessimism ~12-13, optimism ~2, under the <=40% V+A+B assumption.
- `Бизнес_Анализ/Расчёт_прибыли.md:91-98` names what must be measured before the model truly counts.

**Warrant:** The economic chain can be followed from fee level -> paid positions -> revenue/studio -> contribution -> fixed monthly break-even.

**Qualifier:** Scenario math, not proof. Mix levels, real paid positions, and V/A/B are assumptions until pilot/pre-pilot data.

**Rebuttal / defeater:** Low paid position volume, low accepted/submitted, high free openings, high support/manual cost, high catalog amortization, or high dispute rate breaks the model.

### 6. Sensitivity / kill conditions

**Claim:** The corpus has explicit kill conditions and sensitivity points for the profit chain.

**Data anchor:**
- `Бизнес_Анализ/Ставка_MAVO.md:46-54` lists money chain hypotheses, especially paid `Принять` and economics.
- `Бизнес_Анализ/Ставка_MAVO.md:56-63` gives kill criteria.
- `Бизнес_Анализ/Ставка_MAVO.md:64-79` lists current evidence holes.
- `Бизнес_Анализ/Проверка_пилота.md:45-69` gives go / pivot / no-go rules.
- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:46-58` says pilot validates willingness to pay and unit economics, but does not close the full model.

**Warrant:** The docs do not only say "we earn"; they describe what falsifies the chain.

**Qualifier:** Business-test layer, not product rule layer.

**Rebuttal / defeater:** Studio non-payment after free openings, negative contribution, insufficient sample, direct-payment trust failure, or fee larger than perceived prepress/sales savings.

### 7. Reality check / cheapest experiment

**Claim:** The corpus provides a concrete next evidence path: pre-pilot packet plus pilot metrics, not a future marketplace bet.

**Data anchor:**
- `Бизнес_Анализ/Ставка_MAVO.md:80-82` says the cheapest next proof is a pre-pilot packet: manual factory run, print-ready test, pessimistic unit table.
- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-30` defines the first accepted request with paid position.
- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:32-48` defines minimal path and what the pilot validates.
- `Бизнес_Анализ/Проверка_пилота.md:45-58` defines minimum sample and economic sample.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:44-59` defines request/money metrics: repeated `Принять`, paid MAVO lines, balance top-ups, contribution/CAC/cost positions.

**Warrant:** The reality check measures the weakest current assumptions: paid `Принять`, paid repeat after free openings, unit contribution, cost per SKU, and studio share/adoption.

**Qualifier:** Planned validation; no evidence that it has run yet.

**Rebuttal / defeater:** Without real paid unlocks and V/A/B measurement, the docs remain internally coherent but commercially unproven.

## Missing or weak links

1. **No measured V/A/B.** `Расчёт_прибыли` correctly names VarOps, CatalogAmortization, BadDebt/Dispute, but they are unquantified.
2. **No cost per active/published studio.** `Экономика_каналов` lists CAC, setup/support and founder-touch positions, but no actual cost values.
3. **No real paid unlock sample.** The chain requires repeat paid `Принять` after free openings / balance top-ups; current docs define this, but do not report observed data.
4. **No measured accepted/submitted and paid-position mix.** Revenue scenarios depend on paid positions/month and mix of simple/medium/expensive designs.
5. **No proven fee pass-through.** Studio margin proxy is tight: `Выгода_студии_в_цифрах.md:21-23` says working margin is 300-500 ₸ per order, while fee tiers can be 700/1500 ₸. `Ставка_MAVO.md:73-75` calls this out.
6. **No legal/IP gate proof before paid pilot.** `Ставка_MAVO.md:76-77` flags legal/IP and first compatible SKU/studio availability holes.

These are not hidden contradictions; they are stated gaps. That is why verdict is yellow, not red.

## Conflicts / future-smuggling

**No current future-smuggling found in the primary current chain.**

The current files consistently say:
- own-channel commission is `0%`;
- MAVO does not take buyer payment;
- fee is fixed by service-fee level, not percentage of buyer price;
- marketplace / common gallery / platform demand commission is future-only.

Future material is correctly quarantined:
- `04_Доп_проекты/Будущее/AGENTS.md:21-47` says future ideas must not become current canon without promotion.
- `04_Доп_проекты/Будущее/Этап-3/Почему_маркетплейс_отложен.md:11-16`, `96-100` marks marketplace as delayed/future.
- `04_Доп_проекты/Будущее/Этап-3/Общая_галерея_и_платформенный_канал.md:29-34` says no current common gallery, studio choice, automatic transfer, or commission for platform demand.
- `04_Доп_проекты/Будущее/Этап-3/Post-MVP_общая_галерея/Деньги_и_комиссия.md:31-35` says `12%` is future-only and commission must not appear in the personal studio storefront just because MAVO is a platform.

**Smuggling risk to watch:** external evidence mentions percentage / commission-like test corridors (`Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:120-122`, `164-166`). Those lines are external hypotheses, not current MAVO pricing. Current owner files override them.

## Reality Gap

The documents prove internal traceability, not business truth. The largest reality gap is quantitative: the chain can be read, but not yet trusted as a profit engine until it has:

- real cost per opening;
- cost per published SKU and average openings/SKU;
- dispute/bad-debt/error rate;
- paid positions per active studio/month;
- mix of 300/700/1500 tiers;
- studio willingness to pay after free openings;
- support/onboarding cost per published studio;
- accepted/submitted and downstream paid conversion.

The corpus already names the cheapest next proof: manual pre-pilot unit table + first studio print-ready test + pilot window with paid `Принять` after free openings. That is the right reality gate for PROFIT-01.

## Final audit position

PROFIT-01 should pass as **YELLOW / traceable-but-unproven**:

- **Traceability:** holds.
- **Current/future boundary:** holds.
- **Revenue source:** holds.
- **Pricing mechanism:** holds.
- **Cost and unit economics:** present but under-measured.
- **Kill criteria and reality check:** holds.

Recommended repair if this corpus is being moved toward green: create or update one owner section, probably in `Бизнес_Анализ/Расчёт_прибыли.md`, with a tiny pessimistic unit table for the three service-fee levels. Rows: fee, VarOps estimate, catalog amortization estimate, bad-debt/dispute buffer, contribution, confidence, measurement method. Do not import future commission or subscription pricing into current model to patch the hole.
