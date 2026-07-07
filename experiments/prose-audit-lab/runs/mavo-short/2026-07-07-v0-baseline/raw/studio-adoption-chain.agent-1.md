# STUDIO-01 raw chain audit — agent-1

Target: `/Users/triton/Documents/mavo-short/`
Harness: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/`
Test: `suite/studio-adoption-chain.test.md`
Role: independent Chain Auditor
Date: 2026-07-07

## Verdict

`yellow`

The current corpus contains a traceable studio adoption chain from pain -> value -> self-serve onboarding -> first accepted orders -> risk boundary -> pilot validation plan. It is not green because the chain is explicitly still hypothesis-heavy at the retention and reality layers: month-three/after-first-orders continuation is a measurement plan and a workflow-retention hypothesis, not a validated mechanism; paid `Принять`, studio willingness to pay after free openings, economics, legal/IP gates, and answer to strong/free substitutes remain current named gaps.

This is not red: the corpus is unusually honest about its qualifiers and does not silently promote future marketplace mechanics. The weak links are visible and mostly owned.

## Tool coverage

- `md ping --json`: worked, `md-tools 0.7.0`.
- `md status /Users/triton/Documents/mavo-short --json`: `FRESH`, index exists, no pending/stale sections, path scope excludes `_workspace`, `_ops/plans`, `_ops/handoffs`, `_ops/interviews`, `_ops/findings`, CLAUDE files, etc.
- `md search-read`: one broad studio query succeeded; several parallel/nearby queries returned `index_busy`. Later scoped retention search succeeded. I treated `index_busy` as a tool gap, not as semantic evidence.
- `rg`/`nl`/`sed`: used for exact line evidence. A first broad `rg` surfaced `_ops/findings` noise; those hits were not promoted into the current verdict.
- Future-only `04_Доп_проекты/Будущее/**`, archived plans, `_workspace/**`, handoffs/interviews/findings were not promoted into current verdict. `04_Доп_проекты/**` was used only as secondary/context-only where explicitly labelled that way by `corpus.md`.

## Scope boundary used

`corpus.md` says primary current corpus is:

- `README.md`
- `AGENTS.md`
- `_ops/GOAL.md`
- `_context-base/*.md`
- `Данные_снаружи/*.md`
- `01_Описание_бизнеса/**/*.md`
- `02_Веб_приложение/**/*.md`
- `03_Создание_загрузка_дизайнов/**/*.md`
- `Бизнес_Анализ/**/*.md`

Secondary/context-only:

- `04_Доп_проекты/**/*.md`, except future-only material must not be promoted into current canon without explicit current-owner anchor.

This matters for STUDIO-01 because `04_Доп_проекты/Самые_первые_студии/**` can support the external pitch, but cannot by itself make the adoption chain green.

## Chain links

### 1. Studio pain or business job

Claim:

Small/micro print studios have a real job: make money on small custom orders while reducing unpaid prepress, chat chaos, design/manager load, and uneven equipment utilization.

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория.md:34-40` — studio core: micro/small digital-printing studios, pay MAVO, want money from piece orders, acceleration, even equipment load; fear platform, MIS burden, opaque money/sanctions, insufficient orders.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:15-17` — current small studio work is WhatsApp/Instagram conversation, versions, approval, money only late; bottleneck often desire -> technically usable file.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:21-40` — unpaid prepress, messenger chaos, design load, buyer leakage, idle equipment, market shift to many small orders, raw lead insufficiency, order thresholds.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:69-83` — stable demand and money are core desires; why studio pays is expected saving of manual chat/prepress/admin work on accepted request.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:108-136` — JTBD: reduce designer work, reduce manager work, bring hot buyers with packaged request.
- `/Users/triton/Documents/mavo-short/Данные_снаружи/Проблемы_prepress_в_полиграфии.md:10-14`, `29-39`, `47-58` — external evidence: prepress friction, unpaid setup work, staffing burden; qualifiers that universal payoff is not proven.
- `/Users/triton/Documents/mavo-short/Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:16-24`, `26-35`, `53-69`, `144-169` — external hot-order evidence: value is accepted production/order packet, not abstract lead.

Warrant:

If a small studio loses margin in prepayment chat/prepress/design/manager work, a structured accepted-order packet can create value before any marketplace demand exists.

Qualifier:

The corpus explicitly limits this to a target segment. Universality is not proven:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:45-52`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:146-177`

Rebuttal:

Studios with existing templates, strict file intake, mature W2P/order tools, manual production without digital file input, or corporate buyers with brand books may not feel this pain enough to adopt.

Status: strong / traceable.

### 2. MAVO value against that pain

Claim:

MAVO offers the studio a branded storefront, MAVO-owned catalog/SKU, structured request, paid `Принять`, and open package only when the studio accepts the request. The value is not "we send you leads"; it is "your storefront, your customer, your money, less chaos per accepted request."

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:52-68` — for studios: storefront without development, ready SKU, less manual prepress, easier-to-process requests; model components include capability model, storefront, structured request, accepted request, thin post-accept contour.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:22-35` — studio gets own channel/brand storefront, MAVO catalog, compatible SKU, managed request, buyer relationship/payment/communication, print-ready packages after `Принять`; promise: "your storefront, your client, your money".
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:38-45` — MAVO promise by moment: give buyer managed choice, give studio data before `Принять`, open packages at `Принять`, keep link/status/file/financial traces without quality arbitration.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Обработка_заявок.md:12-29` — studio sees decision-ready package; `Принять` opens files and paid lines; after `Принять` order moves into studio contour.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Привлечение_студий.md:20-29` — channel hooks: store without code, catalog not drawn by studio, structured request, own brand/client/money, free entry and payment only for opened package.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Выгода_студии_в_цифрах.md:15-23` — working estimate: messenger order around 2,050 KZT vs MAVO request around 1,400 KZT; all numbers are pre-pilot working guides.

Warrant:

The value maps directly to the pain: it reduces setup/chat/design/manager overhead while preserving the studio's channel and money, so the studio has a reason to try MAVO without first accepting marketplace control.

Qualifier:

Demand volume is not promised and remains a pilot hypothesis:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:56-64`
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Посадочная_страница/Посадочная_страница.md:25-31`, `48-55`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Каналы_привлечения/Каналы_привлечения.md:20-36`

Rebuttal:

If MAVO does not produce a felt saving, if catalog quality is weak, if the structured request still becomes WhatsApp/manual prepress, or if substitutes are easier/cheaper, the value does not survive first use.

Status: strong, but monetization/willingness is still hypothesis.

### 3. Current alternative and why worse or insufficient

Claim:

The corpus names alternatives: direct WhatsApp/Instagram to studio, W2P/MIS/order OS, studio storefront SaaS, design tools/catalogs, Canva/freelancers, mass-market, POD/marketplace models. It argues MAVO's wedge is the combined layer: studio-owned storefront + MAVO catalog/SKU + structured request + paid `Принять`, without heavy MIS or marketplace control.

Data / anchors:

- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:13-33` — seven neighbor groups and summary map.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:60-73` — design catalogs, storefront SaaS and local-maker networks prove components but not the MAVO assembly; catalog alone is not barrier.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:77-85` — W2P/MIS/order OS already solve order thresholds, but usually require the studio to configure products, prices, templates, workflow and implementation; MAVO takes lightweight order certainty rather than heavy MIS.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:87-93` — direct studio habit is the process competitor; MAVO must be faster/clearer than messenger.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:95-109` — freelancer/Canva and mass-market are effort/desire competitors.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/00_Анализ_рынка/Рыночные_паттерны_заказа.md:17-30`, `34-47`, `70-81` — market lesson: use responsibility thresholds, not heavy MIS.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:114-121` — pilot compares against the habitual direct-message channel.

Warrant:

MAVO can win only if it preserves the studio's own channel while reducing the effort and ambiguity of direct chat, and if it avoids the adoption burden of heavier W2P/MIS while adding catalog/SKU value that plain SaaS storefronts do not.

Qualifier:

The comparison is current but incomplete against some concrete substitutes. The corpus itself says the answer to Kaspi/free substitutes is missing:

- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:64-79`
- especially `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:75`

Rebuttal:

Mature studios can buy W2P/order OS; studios with existing demand and digital stack can use storefront SaaS; buyers may use Canva/freelancer/mass-market; local commerce/payment ecosystems like Kaspi may be a stronger free/subsidized path.

Status: partial. Alternative map exists; concrete current substitute answer is not green.

### 4. Switching cost / onboarding friction and product reduction

Claim:

Onboarding is intentionally self-serve and lightweight: registration, contact, card/budget, storefront profile, physical capability, commercial availability, prices/terms, rules, payment contours, first active link. It avoids manual approval, offline verification, heavy integrations, paper contracts, and technical onboarding per studio.

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Регистрация_студии.md:11-24` — anyone can connect; registration/contact, card/min budget, storefront setup, catalog rules; founder-touch first 3-5 studios is motivation, not technical onboarding; manual tech onboarding would turn MAVO into consulting.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_студии.md:41-55` — connection, card/budget, storefront settings, capability, prices, request fields.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Путь_студии.md:37-51` — lifecycle from first touch to active storefront; first touch removes fear; onboarding completes mandatory minimum; weak trust signal does not block activation.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/Подключение_студии.md:12-31` — seven onboarding steps and explicit non-goals: no manual interview, no paper contract, no offline capability check, no complex software/integrations.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/UIUX_Разработка/Экранный_бриф.md:15-39`, `41-79`, `80-98` — onboarding screen task, hierarchy, next-step button, critical blocks, demo path, and MVP exclusions.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/UIUX_Разработка/Состояния_и_переходы.md:16-29`, `31-58`, `72-90`, `101-106` — wizard states, saved progress, blockers, activation, forbidden transitions.

Warrant:

Reducing switching friction lets a skeptical studio try the storefront without adopting an ERP/MIS, waiting for manual approval, or doing heavy integration first.

Qualifier:

The "safe" part is safe relative to current model, not safe as marketplace vetting. MAVO intentionally does not check real-world studio quality before the first link:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Регистрация_студии.md:30-35`
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/Подключение_студии.md:23-31`

Legal form remains a jurisdictional assumption:

- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/Подключение_студии.md:48-50`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:17-20`

Rebuttal:

If every next studio still needs founder-led persuasion/manual setup, the model becomes consulting:

- `/Users/triton/Documents/mavo-short/04_Доп_проекты/Самые_первые_студии/Подключение_первых_студий.md:53-66` secondary/context-only.

Status: good onboarding chain, with legal/trust/access caveats.

### 5. First order fulfillment path

Claim:

The corpus describes how a studio receives and executes first orders: structured request arrives; studio sees enough to accept/reject; `Принять` opens files and creates paid lines; after that the studio handles invoice, payment, production and handoff outside MAVO.

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_студии.md:56-66` — when storefront is live, structured requests arrive; studio accepts/rejects; after `Принять` physical order is in studio contour; studio pays MAVO for opened print-ready package by accepted position.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Обработка_заявок.md:12-29` — request as work unit; accept/reject; paid action and file opening; after accept order leaves to studio contour.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:73-103` — what studio sees before/on/after `Принять`, snapshot, money at boundary.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Платформа_обработки_заказов/Платформа_обработки_заказов.md:14-24`, `33-40`, `44-59`, `61-84` — working zone, main screen, employee-visible data, non-goals.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Платформа_обработки_заказов/Список_заказов.md:47-73`, `82-115` — request card, actions, files after accept, payment/production external, empty/anxious states.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Статусы_и_события_заказа.md:22-38` — usable request contents, external studio events, `Оплачено` not MAVO boundary, risk of weak operational discipline.

Warrant:

The first-order path gives the studio a bounded, decision-ready package and avoids turning MAVO into a production tracker. This is consistent with the model: MAVO monetizes accepted packages, not full fulfillment.

Qualifier:

After `Принять`, production/payment/returns are external studio operations. The corpus does not promise to guarantee physical fulfillment.

Rebuttal:

If the studio ignores statuses, returns to WhatsApp, asks the buyer to restate everything, or rebuilds the file manually, the order path does not deliver adoption value. This is explicitly a pilot question:

- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:100-112`
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:61-68`

Status: mechanically traceable, pilot-dependent in practice.

### 6. Retention mechanism after first orders / month three

Claim:

Current retention mechanism is not lock-in. It is a hypothesis: studios keep using MAVO if repeated `Принять` events remain faster/easier/more profitable than returning to WhatsApp/manual prepress, and if their own storefront/share-link produces repeat submitted/accepted requests and paid unlocks after the free opening corridor.

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:172-177` — retention is workflow advantage hypothesis, not structural lock; risk if manual path is easier.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:17-30` — supply funnel includes repeat paid `Принять`, retention of paying studios after first openings, and studios that stop returning to publication/requests/paid accept.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:44-59` — repeated `Принять` and paid MAVO lines signal studio willingness to pay; money events recorded.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:45-58` — 30 active days after publication of 3-5 storefronts; minimum sample and economic sample.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:60-69` — go requires repeated submitted/accepted requests and willingness to pay service fee after trial openings.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:70-85` — post-go growth checks, 90-day/100 submitted/30 downstream paid orders review trigger.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:87-99` — main hypotheses: studio traffic, 3 accepted requests in 30 days, downstream paid conversion, willingness to pay after trial openings, whole short path required.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:33-48` — monthly revenue scenarios per studio; first month depressed by free openings.

Warrant:

If accepted packages repeatedly save enough time/prepress and generate paid unlocks from the studio's own traffic, the studio has a reason to continue past first use.

Qualifier:

This is the weakest current link. The corpus names metrics and hypotheses; it does not yet show actual retention. The 90-day mark is a review trigger, not evidence that the studio will continue after month three.

Secondary/context-only support exists but is not current proof:

- `/Users/triton/Documents/mavo-short/04_Доп_проекты/ИИ_поддержка.md:19-21`, `53-65`, `87` calls AI support a retention tool, but it is a separate project, not core current product.
- `/Users/triton/Documents/mavo-short/04_Доп_проекты/Привлечение_покупателей.md:39-43` says future help page appears after first live studios.

Rebuttal:

If repeat paid `Принять` does not happen after trial openings, if studio stops sharing, if requests are low quality, or if economics are negative, the current wedge pivots or stops:

- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:60-69`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:56-63`

Status: partial / yellow. Mechanism is plausible and measurable; not proven and not enough for green.

### 7. Risk handling: quality remains with studio, buyer pays studio, MAVO does not police production like a marketplace

Claim:

The current model consistently keeps production, quality, payment from buyer, returns and buyer relationship with the studio. MAVO keeps storefront, catalog, request structure, snapshot, file opening and financial trace. It does not act as marketplace arbiter or production police.

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:38-46` — buyer pays studio; studio is seller/executor; MAVO is infrastructure, not cashier/seller.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:56-70` — physical result and execution with studio; `Оплачено` external; after `Принят`, no transfer to another studio.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:15-41` — buyer -> studio money, studio -> MAVO for package opening; MAVO not cashier, not price setter, no buyer money.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:15-38` — three "no": not shop, not cashier, not quality arbiter; responsibility matrix.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:15-30`, `49-52` — buyer sees studio as seller; quality/timing/delivery/returns are studio zone; legal risk remains assumption until country check.
- `/Users/triton/Documents/mavo-short/_context-base/CTX-026_Без_надзора_за_студией.md:18-38` — MAVO does not check, observe, judge print quality or hunt fraud in studio-buyer relation; only money balance or court order affect access.
- `/Users/triton/Documents/mavo-short/_context-base/CTX-014_Качество_остаётся_у_студии.md:20-40` — quality stays with studio; no current sanctions/trial periods/quality metrics.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Споры_исключения_и_кто_отвечает.md:44-47` — support handles platform/file/line/access issues; does not handle product quality/material/refund/delay/delivery.

Warrant:

These boundaries keep current MAVO from accidentally becoming a marketplace, cashier, arbitration layer, or production OS, which would contradict the studio-owned storefront model.

Qualifier:

Legal/IP and country launch checks are not complete:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:19-20`
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:76`

Rebuttal:

No-policing is coherent for current scope but shifts trust burden to studio signals and buyer understanding. If buyers expect MAVO to guarantee quality, or if studios abuse the channel, current model has intentionally deferred sanctions/marketplace mechanics. Future sanctions/rating files must not be used to green current STUDIO-01.

Status: strong current boundary, with legal/IP risk.

### 8. Reality check: interviews, pilot, usage signal

Claim:

The corpus has interview and external evidence plus a concrete pilot measurement plan. It does not yet have actual usage/adoption proof.

Data / anchors:

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:58-61`, `77-83`, `89-95`, `101-104`, `112-136` — interview-derived claims about studio fear, money, speed, equipment load, designer/manager/hot-packaged-buyer JTBD.
- `/Users/triton/Documents/mavo-short/04_Доп_проекты/Самые_первые_студии/Презентация.md:130-153` secondary/context-only — external presentation cites studio-owner quote and proposes 5-10 submitted/accepted requests, 15-20 min connection, no subscription, service fee after trial openings, but some items are assumptions.
- `/Users/triton/Documents/mavo-short/04_Доп_проекты/Самые_первые_студии/Нарратив_презентации.md:105-112` secondary/context-only — explicitly says phase-1 presentation has no customer stories; evidence is external structure and hot-order evidence.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-52` — first accepted paid request criteria, steps to pilot, and what pilot validates.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:16-30`, `45-58`, `70-85`, `100-125` — what to prove first, pilot go/no-go, after-go growth checks, unresolved pilot questions, metrics owner.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:46-54`, `64-82` — adoption chain links are mostly hypothesis/dopushchenie; due-diligence verdict: idea alive, not proven; named evidence holes.

Warrant:

The audit can trace what would validate adoption, but cannot treat planned pilot metrics as actual adoption.

Qualifier:

Actual live adoption evidence is absent in current corpus. The strongest current reality evidence is interview/external research, not observed use.

Rebuttal:

If pilot data contradicts the hypotheses, the docs already define pivot/no-go paths rather than papering over failure.

Status: yellow. Plan is good; proof is not there.

## Missing or weak links

1. Retention after month three is not proven.
   - Current owner has metrics and review triggers, not evidence.
   - Key lines: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:70-85`, `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:17-30`, `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:172-177`.

2. Willingness to pay after free openings is the central unresolved adoption proof.
   - Key lines: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:48`, `56-63`, `68-73`; `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:60-69`, `87-99`, `104-112`.

3. Concrete answer to free/strong substitutes is not done.
   - The alternative map exists, but `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:75` explicitly says "why not Kaspi" is not written.

4. Economics is not green.
   - Unit contribution and break-even are skeletal, with V/A/B not quantified.
   - Key lines: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Расчёт_прибыли.md:50-56`, `65-96`; `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:72-74`.

5. Legal/IP risk remains assumption.
   - Key lines: `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:19-20`; `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:76`.

6. Separate owner-vs-employee access model is explicitly a founder gap.
   - It does not break STUDIO-01 by itself, but it weakens "safe onboarding/execution" if the first product needs employee workflows.
   - Key lines: `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Путь_студии.md:14-16`; `/Users/triton/Documents/mavo-short/02_Веб_приложение/Реестр_возможностей/Сотрудник_студии.md:14-18`, `62-70`.

7. No current marketplace-quality safety net.
   - This is not a contradiction; it is current scope. But it means buyer/studio trust must be validated without future sanctions, ratings, or platform policing.
   - Key lines: `/Users/triton/Documents/mavo-short/_context-base/CTX-026_Без_надзора_за_студией.md:18-35`; `/Users/triton/Documents/mavo-short/_context-base/CTX-014_Качество_остаётся_у_студии.md:20-40`.

## Current alternative gaps

- Direct WhatsApp/studio habit is acknowledged as the process competitor, but actual measured superiority over chat is only a pilot question.
  Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:87-93`; `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:114-118`.

- W2P/MIS/order OS are acknowledged, but mature studios may choose them instead.
  Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:77-85`.

- Studio storefront SaaS can solve storefront/form workflow without MAVO if catalog/design pipeline is not valuable enough.
  Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:60-69`.

- Canva/freelancers/mass-market remain credible effort/desire substitutes.
  Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Соседние_модели_рынка.md:95-109`.

- Kaspi/free-substitute positioning is explicitly missing.
  Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:75`.

## Onboarding / retention / risk gaps

Onboarding gaps:

- Self-serve path is well described, but safety depends on honest capability/availability entry, not physical verification.
  Evidence: `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/Подключение_студии.md:23-31`; `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Настройка_поверхностей.md:13-19`, `44-51`.

- Legal onboarding form remains a launch-country assumption.
  Evidence: `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Онбординг_студий/Подключение_студии.md:48-50`; `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:19-20`.

Retention gaps:

- No validated retention loop yet; the loop is "repeat paid `Принять` because workflow is better", and it is labelled hypothesis.
  Evidence: `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:172-177`; `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:70-85`.

- AI support is a secondary add-on, not current core retention proof.
  Evidence: `/Users/triton/Documents/mavo-short/04_Доп_проекты/ИИ_поддержка.md:19-21`, `40-59`.

Risk gaps:

- Current model intentionally avoids quality sanctions and marketplace policing. Coherent, but trust must be earned via studio signals and pilot evidence.
  Evidence: `/Users/triton/Documents/mavo-short/_context-base/CTX-014_Качество_остаётся_у_студии.md:20-40`; `/Users/triton/Documents/mavo-short/_context-base/CTX-026_Без_надзора_за_студией.md:18-35`.

- Copyright/IP/file-quality gate is not yet proven by first studio tests.
  Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:68-77`.

## Reality gap

Current corpus does not yet prove adoption. It proves that:

- the pain hypothesis has external and interview grounding;
- the product path is traceable and scoped;
- the pilot can measure whether adoption happens;
- the docs do not pretend registration equals adoption.

It does not prove:

- 3-5 studios will publish and share storefronts;
- studios will get repeated submitted/accepted requests;
- studios will pay after trial openings;
- they will still use MAVO after month three;
- direct payment, legal/IP, and quality boundaries will survive first real disputes;
- MAVO beats Kaspi/free substitutes in practice.

The corpus itself says the honest business verdict:

- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:80-82` — idea alive, not proven.

## Final assessment

STUDIO-01 is `yellow`.

Passable parts:

- Studio pain/job: strong.
- MAVO value against pain: strong as a hypothesis and offer.
- Alternative map: present, but with named gaps.
- Onboarding path: strong, product-level.
- First order path: strong mechanically.
- Risk boundary: strong and current-scope coherent.

Not green:

- Retention after month three is not a demonstrated chain, only a measurable hypothesis.
- Actual adoption evidence is absent; current evidence is interviews, external analysis, and pilot plan.
- Paid `Принять`, economics, legal/IP, print-ready first-studio contract, and Kaspi/free substitutes remain live holes.

