# CUSTOMER-01 raw audit — agent-3

Target corpus: `/Users/triton/Documents/mavo-short/`  
Harness: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/`  
Question: does the corpus hold a traceable chain for why a buyer reaches a submitted request and the studio-paid `Принять` boundary?

## Verdict

**yellow**

The chain exists and is mostly traceable: buyer pain -> MAVO promise -> concrete storefront/request mechanism -> studio decision -> paid `Принять` -> pilot metrics. It is not green because the riskiest business step is explicitly still a hypothesis: direct payment to the studio must not break buyer trust, and the current UI/page layer does not fully materialize the stronger trust needs named by the psychology layer: order ID / invoice or receipt / cancellation-before-print / remake-on-defect policy.

Important semantic boundary: the buyer does **not** personally reach a "paid `Принять`" action. The buyer reaches `Отправить заявку`; the studio later presses `Принять`, which creates MAVO's paid event. The corpus states this clearly, but the CUSTOMER-01 wording can blur it. I treat the valid chain as: buyer motivation -> submitted structured request -> studio can accept -> MAVO paid event.

## Tool / Scope Notes

- Read startup docs: `README.md`, `AGENTS.md`, `_ops/GOAL.md`.
- Read harness `README.md`, `corpus.md`, and `suite/customer-demand-chain.test.md`.
- `md status . --json` on target corpus returned `FRESH`, index exists, drift 0, with `_workspace/*`, `_ops/plans/*`, `.claude/*`, `.codex/*`, etc. excluded from indexed scope.
- One `md search-read` query succeeded and identified the main holders: `Психология_покупателя.md`, `_Путь_покупателя.md`, `Контракт_сторон.md`. Parallel `md search-read` calls hit `index_busy`; I treated this as a tool gap and continued via `rg`, `sed`, and exact `nl -ba` reads.
- A future-only search result, `04_Доп_проекты/Будущее/Этап-3/Почему_маркетплейс_отложен.md`, was not promoted into current verdict.
- I did not edit the target corpus.

## Chain Links

### 1. Buyer Pain / Job To Be Done

**Claim:** the buyer has a real reason to try the MAVO vitrine: they want a personal/custom item without slow, anxious chat and unclear result/payment/schedule.

**Data / anchor:**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:13-22` — current custom order is WhatsApp/Instagram chat, idea explanation, waiting for mockup, later payment agreement; pain includes invisible result, unclear price/time, fear of misunderstanding, payment/defect/date anxiety.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:22-25` — primary desire is a non-generic item; secondary axis is the familiar online catalog habit; product form follows as ready SKU, 0-3 fields, preview, request.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:83-85` — target path: choose ready SKU, configure allowed fields, submit request in 3-5 minutes; "fast" means fast to `Отправить заявку`.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:114-128` — JTBD scenarios: gift, home/office aesthetic, self-expression without editor, quick B2B add-on.
- `Бизнес_Анализ/Суть_рынка.md:8-14` — market thesis: buyer wants a personal thing without editor/chat; studio wants demand without prepress chaos.

**Warrant:** if the buyer already wants a personal item and the old route forces them into chat, design explanation, mockup waiting, and unclear payment, a familiar catalog-plus-preview path lowers the effort enough to generate submitted requests.

**Qualifier:** this is explicitly a `гипотеза` until pilot. The corpus says the online-catalog habit transfer is unproven before pilot.

**Rebuttal:** online buying trust does not transfer automatically to custom studio payment. `Проблемы_покупателей.md:31-34` and `Психология_покупателя.md:30-33` both warn that the catalog front can transfer while deal/payment trust may not.

**Local verdict:** green/yellow. The pain/JTBD link is present and well anchored, but still hypothesis-grade.

### 2. MAVO Promise To The Buyer

**Claim:** MAVO promises the buyer a short, simple path inside a specific studio's storefront: choose, personalize safely, see preview/price/studio context, submit a structured request.

**Data / anchor:**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8` — MAVO is a Web-to-Print SaaS / white-label storefront; buyer enters a specific studio's vitrine, chooses product/design, fills allowed fields, submits request to the studio; studio remains seller/executor.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:22-27` — north star: ordering from a small studio should be easy/simple; structured request replaces chaotic request with product/design/valid params/preview/contact.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:52-56` — buyers get a short path to personal goods without painful chat.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:14-20` — buyer gets understandable choice before sending, number/stable link/summary/visible studio after sending, and next studio step after `Принять`; MAVO does not promise production/delivery/physical warranty.

**Warrant:** the promise directly answers the old-flow pain: reduce explanation work, show a concrete product/result, and preserve the studio as seller.

**Qualifier:** the promise is deliberately narrow. MAVO does not promise buyer checkout, production tracking, delivery, or guarantee.

**Rebuttal:** if buyers need marketplace-like protection or MAVO-as-seller, the promise may be too thin. The corpus treats that as a model risk, not a feature gap.

**Local verdict:** green. The promise is clear and consistently bounded.

### 3. Product-Surface Mechanism

**Claim:** the current web/product docs make the promise concrete enough for a designer/developer to implement or violate it.

**Data / anchor:**

- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:31-37` — structured stages: collected in vitrine, sent, visible to studio, `Принять`, after `Принять`.
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:53-63` — before request, buyer sees studio-branded vitrine, product as ready picture, allowed personalization fields, price/time/pickup, contact fields.
- `02_Веб_приложение/Реестр_возможностей/Покупатель.md:70-79` — path and screen decisions: vitrine, SKU, personalization, cart, request page, payment context.
- `02_Веб_приложение/Страницы/Карта_страниц_и_пути/10_Путь_покупателя.md:15-27` — route: vitrine -> product -> managed personalization -> request -> stable link -> status -> direct studio payment.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Главная/Главная.md:28-36` — home shows studio banner, quick occasion entries, thematic SKU carousels, trust block, catalog transition.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Каталог/Каталог.md:37-45` and `50-52` — catalog shows studio context, SKU grid, filters, price, trust context; each card is visible SKU the studio can sell.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_товара/Страница_товара.md:15-27` — product page: live mockup/fallback, customizer, surface, quantity, executor, trust signals, timeline/pickup orientation, price, `Проверить заявку`.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Корзина/Корзина.md:14-38` — cart/request draft shows final request composition, price, contact, pickup, acceptance; checkbox is required before `Отправить заявку`.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_заказа/Страница_заказа.md:23-49` — request page shows number/link, status, summary, next studio step, status actions, and explicitly does not accept payment.

**Warrant:** these are falsifiable constraints: a design that hides studio context, adds MAVO checkout, lets a cart cross studios, skips acceptance, or removes stable request status would violate the documented mechanism.

**Qualifier:** page docs are behavioral prose, not code/API specs. They are good enough for product behavior handoff, not implementation detail.

**Rebuttal:** some trust/payment details are named at business level but not fully specified as page requirements; see gap section.

**Local verdict:** green/yellow. Mechanism is mostly concrete and falsifiable.

### 4. Trust / Risk Around Payment, File Readiness, Production, Pickup, Returns

**Claim:** the corpus names the payment/trust boundary and deliberately keeps production, pickup, returns, and physical quality under the studio-as-seller boundary.

**Data / anchor:**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:47-68` — buyer trust fears B3-B7: unknown studio, direct payment, losing control after submit, unfamiliar invoice/payment channel, unclear status.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:98-104` — buyer wants lower financial risk; trust depends on visible studio, order ID, invoice/receipt, cancellation-before-print and remake-on-defect policy; MAVO is not cashier/guarantor.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Доверие_покупателя_к_студии.md:20-28` — buyer sees studio trust chain before send, after send, after accepted; if a step disappears, direct payment looks like gray transfer.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Доверие_покупателя_к_студии.md:36-40` — explicit hypothesis/risk: trust may not transfer; direct payment remains the weakest part.
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:22-30` — buyer acceptance: request goes to studio, payment to studio, quality/time/pickup/return are studio zone, preview is orientation, MAVO records request/accept/snapshot/file-open/paid event.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:47-64` — stable link, next studio step, seller/payment context; no production tracker, delivery, MAVO refund, or physical guarantee.
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:55-58` — after accept, studio invoices in external channel; MAVO shows status/contact/link; `Оплачено` is external.
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Споры_исключения_и_кто_отвечает.md:44-49` — support takes platform/file/line/access issues, not quality/color/material/refund/delay/delivery.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_товара/Фото_реальных_изделий.md:22-35` — real product photos are trust signal, not guarantee of exact result.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Корзина/Корзина.md:27-38` — acceptance before sending tells buyer request goes to studio, payment direct to studio, quality/timing are studio obligations, preview is not exact guarantee.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_заказа/Страница_заказа.md:57-67` — request page may leave contact orientation and link, but not promise MAVO becomes seller/delivery/quality court or tracker.

**Warrant:** because the corpus refuses to make MAVO cashier/guarantor, it must compensate with visible seller identity, stable link/order context, explicit acceptance, external payment handoff, and limited support boundary.

**Qualifier:** trust is a hypothesis, not a proven solution. Direct payment is the known weak link.

**Rebuttal:** the business layer mentions order ID, invoice/receipt, cancellation-before-print, and remake-on-defect policy, but page docs currently materialize only a general next-step/payment context. That is a traceability gap from buyer fear to concrete UX requirements.

**Local verdict:** yellow. The boundary is honest and mostly traceable, but not strong enough for green.

### 5. Why Buyer Does Not Simply Use Old Offline / Chat Flow

**Claim:** MAVO competes with the old direct chat flow by replacing idea explanation, mockup waiting, and manual prepress with a ready SKU, preview, safe fields, and structured request.

**Data / anchor:**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:11-24` — old path is WhatsApp/Instagram chat, explanation, mockup wait, edits, payment agreement; some buyers drop before ordering.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:27-34` — buyer already has catalog-shopping habit; the gap is that personal goods throw them back into chat; trust does not fully transfer.
- `Данные_снаружи/Проблемы_prepress_в_полиграфии.md:29-33` — manual chat order creates unpaid prepress work before money; MAVO should reduce friction, not promise no designer needed.
- `Данные_снаружи/Проблемы_prepress_в_полиграфии.md:47-51` — MVP question: can the studio accept structured request faster and with less prepress friction than manual chat order?
- `Бизнес_Анализ/Проверка_пилота.md:104-110` — pilot observes whether structured request closes typical clarifications and whether process escapes back to WhatsApp/manual prepress.
- `Бизнес_Анализ/Проверка_пилота.md:114-118` — main pilot competitor is buyer habit to write directly to studio; pilot measures transfer to catalog path and breaks at direct payment.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:61-68` — analytics track requests where the studio returned to WhatsApp/manual prepress, file rework, typical clarifications closed, insufficient sample.

**Warrant:** old chat is not just another channel; it is the pain MAVO claims to reduce. The corpus makes the alternative measurable by tracking WhatsApp fallback and manual prepress after structured requests.

**Qualifier:** this is not proven by docs; it is a pilot comparison.

**Rebuttal:** if the studio still asks the buyer to describe everything again or manually rebuilds files, the MAVO request did not beat the old flow. The corpus explicitly keeps that as a pilot failure signal.

**Local verdict:** yellow/green. The alternative is addressed well, but proof remains future pilot.

### 6. Reality Check / Validation After Launch

**Claim:** the corpus has a clear reality oracle: demand proof only appears through actual storefront exposure, submitted requests, accepted requests, paid unlocks, downstream paid conversion, and enough sample.

**Data / anchor:**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:70-77` — model is proven by published vitrine, configured capability, real sharing, structured requests, accepted requests, and paid event on `Принять`.
- `Бизнес_Анализ/Проверка_пилота.md:16-25` — what to prove first: buyer submits, studio accepts/rejects, money works, studio channel produces traffic, trust enough, linked layer works, hypotheses update with facts.
- `Бизнес_Анализ/Проверка_пилота.md:45-58` — decision window and minimum sample: 30 active days, 3-5 vitrines, 2+ shared links, measurable path, 20+ submitted or 3+ accepted in one studio/category; else `insufficient sample`.
- `Бизнес_Анализ/Проверка_пилота.md:87-99` — demand proof requires whole short path, not just `Отправить заявку`.
- `Бизнес_Анализ/Проверка_пилота.md:100-125` — unresolved pilot questions and signals: repeated paid `Принять`, 80% typical clarifications, WhatsApp/prepress fallback, breakeven, living studio channel.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:32-68` — definitions of demand, request, money, friction/manual-work metrics.
- `Бизнес_Анализ/Ставка_MAVO.md:46-49` — critical links are hypotheses: catalog habit, studio traffic, paid `Принять`, direct-payment trust.
- `Бизнес_Анализ/Ставка_MAVO.md:56-63` — kill criteria: studios don't pay after trial under live demand, negative contribution, direct-payment breaks not fixed by mitigations.
- `Бизнес_Анализ/Ставка_MAVO.md:80-82` — dated verdict: idea alive, not proven.

**Warrant:** the corpus does not hide reality behind prose; it defines falsifiable launch signals and separates `insufficient sample` from no-go.

**Qualifier:** no live pilot data in current corpus. It is a validation plan, not validation result.

**Rebuttal:** docs cannot answer whether buyers actually submit/pay. The corpus correctly says that only pilot can.

**Local verdict:** green as a validation plan; yellow as proof of market truth.

## Missing / Weak Links

1. **Buyer-to-paid-`Принять` wording mismatch.**  
   Corpus says buyer reaches `Отправить заявку`; studio reaches `Принять`; MAVO paid event occurs then. This is correct, but the test phrase "buyer would ... reach the paid `Принять` boundary" should be read as a chain across actors, not a buyer action.

2. **Direct payment mitigation is named more strongly than it is surfaced.**  
   `Психология_покупателя.md:98-100` says trust needs visible studio, order ID, invoice/receipt, cancellation-before-print and remake-on-defect policy. The page layer has stable link, next step, acceptance, direct payment note, but I did not find equally concrete page requirements for invoice/receipt, cancellation-before-print, or remake-on-defect policy.

3. **Returns / defect policy remains mostly boundary, not buyer reassurance.**  
   The corpus says quality/refunds stay with the studio and MAVO is not the court. That is coherent, but for CUSTOMER-01 the buyer trust chain may need a visible "what happens if defect/return" answer from the studio, not only "MAVO does not handle this".

4. **Price premium / old-flow bypass is acknowledged but underdeveloped.**  
   `Психология_покупателя.md:73-75` says buyer may compare price with direct studio order and leave; MAVO sells reduced effort and clarity, not cheapest price. This is plausible but not tied to a concrete pilot threshold beyond general conversion/drop-off metrics.

5. **Trust depends on studio-sourced traffic.**  
   The corpus leans on "buyer came from the studio already" (`Доверие_покупателя_к_студии.md:14-18`). This is coherent for current white-label scope, but weak if real buyers enter through forwarded links without prior studio trust.

## Old-Flow Alternative Gaps

- The old-flow comparison is good enough for pilot: chat/prepress pain is clear and measured.
- It is not enough for a launch claim like "buyers will prefer MAVO." The corpus must wait for pilot evidence: open -> personalization -> submitted, WhatsApp fallback rate, accepted request rate, downstream paid conversion.
- A strong failure mode is already named: studio receives a structured request but still asks the buyer to restart in WhatsApp or manually rebuilds the file.

## Payment / Trust Boundary Gaps

- Direct payment is the central yellow risk. The corpus is honest: it says direct payment is the weak link and may conflict with the core "MAVO is not cashier" model.
- Current docs protect MAVO's boundary better than they reassure the buyer. That is acceptable for canon integrity, but not enough for green CUSTOMER-01.
- To become green, the chain needs the page layer to carry the stronger business trust details: seller identity, request/order number, invoice/payment instruction, local payment channel, cancellation-before-print, defect/remake path, and exactly who handles each case.

## Reality Gap

- There is no evidence that buyers have actually submitted requests, paid studios, or that studios repeatedly press paid `Принять`.
- The corpus handles this correctly by marking the relevant links as `гипотеза` and defining pilot thresholds.
- Current business verdict from `Ставка_MAVO.md:80-82`: idea alive, not proven.

## Evidence Index

- Startup/scope: `README.md`, `AGENTS.md`, `_ops/GOAL.md`.
- Harness: `README.md`, `corpus.md`, `suite/customer-demand-chain.test.md`.
- Main business answer: `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8`, `22-27`, `38-46`, `60-68`, `70-77`.
- Buyer pain/JTBD: `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:11-34`; `Психология_покупателя.md:18-33`, `35-104`, `112-141`.
- Path/order canon: `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:12-17`, `31-40`, `42-63`, `65-71`, `73-103`, `105-122`.
- Contract/trust/legal/money: `Контракт_сторон.md:14-20`, `38-45`, `47-64`, `66-71`; `Доверие_покупателя_к_студии.md:14-40`; `Юридическая_рамка.md:22-30`, `49-54`; `Споры_исключения_и_кто_отвечает.md:23-49`; `Сервисный_сбор.md:32-39`, `55-58`.
- Web mechanism: `02_Веб_приложение/Реестр_возможностей/Покупатель.md:20-24`, `26-69`, `70-89`; `Страницы/Карта_страниц_и_пути/10_Путь_покупателя.md:15-62`; `Главная.md:18-38`, `46-54`; `Каталог.md:18-24`, `37-48`, `50-73`; `Страница_товара.md:15-31`, `47-61`; `Корзина.md:14-38`, `48-65`; `Страница_заказа.md:15-49`, `57-67`; `Фото_реальных_изделий.md:22-35`.
- Old-flow / prepress: `Данные_снаружи/Проблемы_prepress_в_полиграфии.md:10-14`, `29-33`, `47-58`; `Бизнес_Анализ/Суть_рынка.md:8-14`, `33-38`.
- Reality/pilot: `Бизнес_Анализ/Проверка_пилота.md:16-31`, `45-58`, `87-99`, `100-125`; `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:32-68`; `Бизнес_Анализ/Ставка_MAVO.md:46-63`, `64-82`.

## Auditor Opinion

I would pass the corpus for a **pilot-readiness** chain, not for a **market-proven demand** chain. The documentation is unusually honest about what is hypothesized, what belongs to the studio, and where `Принять` creates money. The main weakness is not a contradiction; it is an under-materialized trust handoff. The buyer-side UI needs to carry the direct-payment mitigation with the same specificity as the business layer, or the chain can break exactly where the corpus already predicts it will: "I liked the product, but I do not want to pay this studio outside MAVO."
