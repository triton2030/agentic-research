# STUDIO-01 raw chain audit - agent 3

Verdict: **yellow**.

Short reason: current corpus contains a traceable, owner-anchored chain for why a studio might connect, onboard, accept first requests, and use MAVO as a thin storefront/request workflow. It is not green because the hardest links - current alternatives, retention after month three, and real pilot proof - remain explicitly hypothetical or marked as evidence gaps by the business-analysis owners.

## Scope and tooling

- Target corpus: `/Users/triton/Documents/mavo-short/`.
- Harness read:
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/corpus.md:3` sets target root.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/corpus.md:5-15` defines primary current corpus.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/corpus.md:17-20` allows secondary/context only, without promoting future-only material.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/corpus.md:22-32` excludes `.ignore`, `_workspace`, tool dirs, and similar non-current zones.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/suite/studio-adoption-chain.test.md:1-7` identifies STUDIO-01 as a chain/coherence oracle.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/suite/studio-adoption-chain.test.md:13-14` asks the core studio adoption chain question.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/suite/studio-adoption-chain.test.md:20-27` requires pain, MAVO value, alternatives, switching/onboarding, retention, risk, and reality check.
  - `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/suite/studio-adoption-chain.test.md:31-33` requires claim/data-anchor/warrant/qualifier/rebuttal and warns not to promote future marketplace material.
- `md ping --json` worked. `md status /Users/triton/Documents/mavo-short --json` reported a fresh semantic index (`state: FRESH`, no pending chunks) and excluded `_workspace`, `_ops/plans`, `_ops/findings`, `_ops/handoffs`, tool dirs, and other non-current zones.
- Tool gap: I initially ran several `md search-read` calls in parallel; only one succeeded and the others returned `index_busy`. I treated this as a tooling/concurrency gap, not as a corpus finding, and continued with targeted `rg` / `sed` / `nl` reads. A later `md status` remained fresh.
- Target corpus was not edited. The only write is this raw audit file.

## Corpus boundary

The current product frame is explicitly a studio storefront/request SaaS, not a marketplace:

- `/Users/triton/Documents/mavo-short/README.md:8-12` frames the repo as current business/product truth, not code/Figma/infra.
- `/Users/triton/Documents/mavo-short/README.md:18-25` maps owners: business, web surfaces, catalog/design operations, business analysis, support/future folders.
- `/Users/triton/Documents/mavo-short/README.md:45` says the current frame is a studio storefront; future marketplace/platform layer lives under `04_Доп_проекты/Будущее`.
- `/Users/triton/Documents/mavo-short/AGENTS.md:24-31` requires live evidence and separates structural green from semantic closure.
- `/Users/triton/Documents/mavo-short/AGENTS.md:48` says future-only ideas are not current canon.
- `/Users/triton/Documents/mavo-short/_ops/GOAL.md:12-15` defines the current model: SaaS storefront with MAVO catalog, structured request, and paid `Принять`; future layers stay in `04_Доп_проекты/Будущее`.
- `/Users/triton/Documents/mavo-short/_ops/GOAL.md:34-41` fixes the current money/product core: `Принять` is the paid gate, buyer pays studio directly, MAVO sells catalog/SKU/request/file-opening infrastructure, studio stays seller/executor.
- `/Users/triton/Documents/mavo-short/_ops/GOAL.md:63-68` requires traceability between layers and explicit separation of facts and hypotheses.

I did not promote `04_Доп_проекты/Самые_первые_студии/*` or future marketplace material into the current verdict. That material can support launch-context hypotheses, but not current product truth.

## Chain links

### 1. Studio pain / business job

**Claim:** The target studio has a real operational pain: small/custom orders arrive through chat/social channels, require manual clarification and prepress before money, and create load on designers/managers while equipment can remain idle.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:15-24` describes WhatsApp/Instagram order chaos, versions, approvals, and prepress before payment.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:25-40` adds design load, buyer disappearing, idle equipment, and why a raw lead is not enough.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория.md:34-38` summarizes studio motives and fears: money, acceleration, equipment loading, reducing designer/manager work, buyer loss, sanctions, and weak order volume.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:69-83` anchors the money/workflow motive.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:97-104` anchors idle equipment / regular load as a studio motive.

**Warrant:** If the studio's cost is not just "getting a lead" but turning a fuzzy chat into a usable order packet, then a structured request and file gate can plausibly remove work before payment.

**Qualifier:** `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:45-49` explicitly says the prepress pain is confirmed enough to use as a hypothesis, but its universality is not proved.

**Rebuttal:** The link does not hold for every studio. `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Подходящие_студии.md:14-24` narrows fit by size, technical readiness, capability, operational maturity, and order mix. Studios with mature W2P/MIS or no suitable custom order mix may not feel this pain enough.

### 2. MAVO value proposition to the studio

**Claim:** MAVO's current value is not marketplace demand. It is a white-label storefront plus MAVO catalog/SKU/request logic that lets the studio receive a more complete request and open production files only after `Принять`.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8` defines MAVO as Web-to-Print SaaS for studios, where the studio stays seller/executor, buyer pays studio, and MAVO opens print-ready packages on `Принять`.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:24-27` states the product replaces chaotic request-making with a structured request containing product, design, valid parameters, preview, and contact.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:54-58` lists what studios get: storefront without development, ready SKU, less prepress, and more processable requests.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:62-68` defines the model components: catalog/SKU, capability, storefront, structured request, accepted request opens files.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:18-25` answers the "another platform" fear: own storefront, channel preserved, money tied to accepted request, not traffic sale.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:126-137` identifies the strongest JTBD as hot buyers with a packed request, but keeps it as a one-studio structured request, not platform demand.

**Warrant:** The value proposition matches the pain only if "structured request + catalog + file gate" is materially better than chat and does not steal the studio's buyer/channel.

**Qualifier:** `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:54-62` says the "easy/self-serve/useful" answer is only partially proven until cases exist.

**Rebuttal:** If the studio expects MAVO to provide buyer traffic, this value proposition weakens. The corpus correctly avoids that promise: `/Users/triton/Documents/mavo-short/04_Как_запускаем/Каналы_привлечения.md:20-36` makes the main bet studio storefront / studio-owned traffic, not a buyer marketplace.

### 3. Current alternative comparison

**Claim:** The main current alternative in the corpus is direct chat/social/manual prepress. MAVO wins only if it turns that path into a cleaner, cheaper, decision-ready request.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:15-24` gives the direct chat workflow problem.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:33-40` says a raw lead does not solve the studio's order problem; the order needs rubrics and gates.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Выгода_студии_в_цифрах.md:9-19` offers a working estimate: chat order around 2050 KZT vs MAVO request around 1400 KZT, about 650 KZT saved in an upper scenario.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:114-119` explicitly says the pilot should compare MAVO against habitual direct chat.

**Warrant:** A studio keeps using MAVO only if the reduction in clarification/prepress/admin cost exceeds the MAVO fee and switching friction.

**Qualifier:** `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Выгода_студии_в_цифрах.md:9-19` is framed as working orientation, not measured reality.

**Rebuttal:** This is one of the weak links. `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:64-79` lists evidence gaps including economics, fee pass-through, why not Kaspi, legal/IP, compatible studio, and measured wedge. `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:80-82` says the idea is alive but not proven, and paid accept is pressured by free substitutes like Kaspi.

### 4. Switching and onboarding safety

**Claim:** The current onboarding story is coherent: a studio can self-connect, configure basic commercial/capability data, publish a storefront link, and activate without manual approval or platform quality vetting.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Путь_студии/Регистрация_студии.md:13-24` defines registration inputs and self-serve rationale.
- `/Users/triton/Documents/mavo-short/03_Как_это_работает/Онбординг_студий/Подключение_студии.md:14-31` maps registration, card, setup, storefront publication, and says no manual interview/offline checks/complex software.
- `/Users/triton/Documents/mavo-short/03_Как_это_работает/Онбординг_студий/UIUX_Разработка/Состояния_и_переходы.md:16-29` defines onboarding states.
- `/Users/triton/Documents/mavo-short/03_Как_это_работает/Онбординг_студий/UIUX_Разработка/Состояния_и_переходы.md:44-58` defines progress saving and blocking only on missing required minimum.
- `/Users/triton/Documents/mavo-short/03_Как_это_работает/Онбординг_студий/UIUX_Разработка/Состояния_и_переходы.md:86-99` defines activation results.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Кредитная_система.md:23-25` gives first openings free, reducing initial payment friction.

**Warrant:** A self-serve path with no manual gate keeps adoption cheap and avoids turning MAVO into consulting.

**Qualifier:** `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/CTX-028_Сбор_предоплата_цены_студии.md:35-42` says the prepayment decision should be revisited if it blocks onboarding, while preserving the non-cashier/non-seller boundary.

**Rebuttal:** Onboarding is not fully safe for operational adoption yet. `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Путь_студии.md:16-17` marks employee access as a founder-gap, and `/Users/triton/Documents/mavo-short/02_Веб_приложение/Реестр_возможностей/Сотрудник_студии.md:18-25` keeps employee behavior scoped but not fully closed. No observed completion/conversion data exists in current corpus.

### 5. First orders and fulfillment path

**Claim:** The first-order path is traceable: buyer submits a structured request to a specific studio; studio sees request data; studio accepts or declines; `Принять` opens files, records paid lines, and hands execution back to the studio.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/02_Пользовательский_путь/_Путь_покупателя.md:31-37` maps submitted request, transfer to studio, `Принять`, and after-accept state.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/02_Пользовательский_путь/_Путь_покупателя.md:73-82` shows what the studio sees before/after accept.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/02_Пользовательский_путь/_Путь_покупателя.md:94-103` defines money/file gate: no valid accept means no file and no paid line.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/02_Пользовательский_путь/Путь_студии/Обработка_заявок.md:12-29` defines request contents, accept/decline, snapshot, print-ready files, paid action, and studio-side invoicing/payment/printing.
- `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Платформа_обработки_заказов.md:44-60` defines what the employee sees before and after accept.

**Warrant:** Because files are withheld before accept and opened only after a paid studio action, MAVO can charge for concrete workflow value rather than a vague lead.

**Qualifier:** `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:64-70` still lists the "print-ready contract" and first factory/production proof as evidence gaps.

**Rebuttal:** Fulfillment itself is intentionally outside MAVO. `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Платформа_обработки_заказов.md:61-76` excludes buyer payment, production tracker, quality disputes, delivery, and balance details from the request platform. This keeps scope clean but means "safe first order" depends on studio execution, not on MAVO guarantee.

### 6. Retention after first orders / month three

**Claim:** The corpus has a plausible retention hypothesis: studios continue if repeated accepted requests reduce manual work and make the fee feel cheaper than chat/prepress/admin pain.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:138-144` says the current test is own storefront, structured requests, and share-link, while the studio wants stable flow/control/margin.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:172-177` says retention rests on workflow advantage, not structural lock, until pilot evidence exists.
- `/Users/triton/Documents/mavo-short/04_Как_запускаем/Сбор_аналитики.md:17-30` includes studio funnel metrics: registration, setup, share, repeat paid accept, churn, adoption bottleneck, qualitative feedback.
- `/Users/triton/Documents/mavo-short/04_Как_запускаем/Сбор_аналитики.md:44-55` includes request funnel metrics: submitted to accepted/declined, repeat accepts/paid lines, downstream conversion, spam/invalid, time to decision, source.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:70-85` defines post-go growth checks and says larger thresholds remain hypotheses until 100+ submitted, 30 paid, 10 active, and 90 days.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:87-113` lists core hypotheses and unresolved questions around repeated paid accepts, clarification closure, adoption bottleneck, return to WhatsApp/prepress, and whether live studio channels create enough traffic.

**Warrant:** Retention is expected if repeated `Принять` events prove that MAVO removes more work/risk than it adds cost/friction.

**Qualifier:** This link is the clearest reason for yellow. The corpus itself says retention is a hypothesis and not structural lock. It has instrumentation and thresholds, not proof.

**Rebuttal:** If manual chat remains easier, if paid accept compresses studio margin, if the studio cannot drive demand through its own channel, or if free alternatives are "good enough," the retention chain breaks. These are not peripheral risks; they are current owner-level open questions.

### 7. Risk handling and safety boundary

**Claim:** The risk boundary is internally coherent: MAVO is not a store, cashier, quality arbiter, or production controller; studio owns buyer relationship, money, quality, deadlines, delivery, and claims.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10-12` says buyer pays studio, studio pays MAVO upfront, MAVO is not cashier/store.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:23-31` defines the paid unit and what MAVO does not do.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:15-20` says MAVO is not store/cashier/quality arbiter.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:31-38` maps responsibility boundaries.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/CTX-014_Качество_остаётся_у_студии.md:20-30` says quality/returns/deadlines stay with the studio and there are no current sanctions/quality metrics.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/CTX-026_Без_надзора_за_студией.md:18-38` says no entry check, no watching, no judging print quality/fraud; quality controls are future, not current.
- `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Споры_исключения_и_кто_отвечает.md:44-48` limits support to technical/money/file/balance/access problems, not buyer quality/refund/delay/delivery.

**Warrant:** A thin platform boundary makes onboarding legally and operationally lighter, and keeps MAVO from becoming a marketplace/operator before the model is proven.

**Qualifier:** `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юридическая_рамка.md:17-20` says the legal-risk position is still an assumption until country-specific check.

**Rebuttal:** The same boundary can weaken buyer/studio trust. If studios or buyers expect platform guarantees, the current "not our contour" answer may feel unsafe. The corpus names this tradeoff but has not validated whether it is commercially acceptable.

### 8. Reality check / pilot proof

**Claim:** The corpus has a clear proof route, but not proof. It knows what must be observed: active storefronts, first accepted requests, paid positions, repeat accepts, channel source, and friction against WhatsApp/prepress.

**Data-anchor:**

- `/Users/triton/Documents/mavo-short/04_Как_запускаем/Пилот.md:11-13` says the roadmap is to first real accepted request / paid event.
- `/Users/triton/Documents/mavo-short/04_Как_запускаем/Пилот.md:15-30` defines criteria for the first accepted request with paid position.
- `/Users/triton/Documents/mavo-short/04_Как_запускаем/Пилот.md:32-45` defines the minimal path: one city, 3-5 studios, catalog, storefronts, share, first request, order cycle.
- `/Users/triton/Documents/mavo-short/04_Как_запускаем/Пилот.md:46-52` says the pilot validates order ability, studio accept, buyer reach through studio, and whether the paid unit makes sense; no sample means insufficient sample.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:16-26` lists first proof points.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:45-58` defines 30 active days after 3-5 storefronts and accepted requests as go/no-go evidence.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:46-54` marks major links as hypotheses/deductions with proof planned.
- `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:80-82` gives the current verdict: idea alive, not proven.

**Warrant:** This is enough for a traceable pilot chain because the corpus knows what would falsify/confirm it.

**Qualifier:** This is not enough for a green adoption verdict because STUDIO-01 asks whether the corpus holds the chain through onboarding, first orders, and continued usage. For continued usage, the corpus mostly holds tests and hypotheses, not empirical anchors.

**Rebuttal:** If future-only first-studio materials or launch scripts are treated as current proof, the verdict would be artificially inflated. I did not treat them that way.

## Missing or weak links

1. **Retention after month three is not proven.** The chain has metrics and hypotheses, but no current evidence that studios repeatedly pay after free openings or after 90 days. Main anchors: `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:172-177`, `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:70-85`, `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:87-113`.
2. **Current alternatives are under-answered beyond direct chat.** Direct chat is compared, but Kaspi/free substitutes, existing sites, simple forms, W2P/MIS, and marketplace-like expectations are not yet beaten with measured wedge. Main anchor: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:64-82`.
3. **First production proof is missing.** The accepted-request/file-gate model is internally coherent, but print-ready package acceptance by a real studio remains a proof gap. Main anchor: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:64-70`.
4. **Prepayment/onboarding friction is acknowledged but not measured.** Free first openings help, but card/min budget/prepay may still block adoption. Main anchors: `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Кредитная_система.md:23-25`, `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/CTX-028_Сбор_предоплата_цены_студии.md:35-42`.
5. **Employee/owner operational model has a founder-gap.** The web layer has a route for owner and employee, but not a fully closed access model. Main anchors: `/Users/triton/Documents/mavo-short/02_Веб_приложение/Страницы/Страницы_для_студий/Путь_студии.md:16-17`, `/Users/triton/Documents/mavo-short/02_Веб_приложение/Реестр_возможностей/Сотрудник_студии.md:18-25`.
6. **Legal/IP/country risk is not closed.** Boundary is coherent, but jurisdictional validation is explicitly pending. Main anchor: `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/03_Как_это_работает/Юридическая_рамка.md:17-20`.

## Current alternative gaps

- **Direct chat / WhatsApp / Instagram:** well-covered as the main alternative. Evidence: `/Users/triton/Documents/mavo-short/01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:15-24`, `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Проверка_пилота.md:114-119`.
- **Free or familiar tools:** under-covered. `Ставка_MAVO` explicitly flags pressure from free substitutes and asks why not Kaspi. Evidence: `/Users/triton/Documents/mavo-short/Бизнес_Анализ/Ставка_MAVO.md:73-82`.
- **Existing W2P/MIS:** treated as heavy/not the first wedge, but not deeply compared in current owner docs. This is acceptable for early pilot scope but not for green adoption proof.
- **Own website / simple form / manual designer:** not falsified with measured data. The corpus has cost hypotheses, not observed switching evidence.

## Onboarding gaps

- The self-serve path is coherent and grounded: registration, setup, activation states, storefront publication, and required minimums are present.
- What is missing is observed completion: how many studios complete setup, where they drop, whether card/prepay/min budget blocks them, and whether founder-touch first 3-5 studios masks true self-serve friction.
- `Путь_студии/Регистрация_студии.md:20-24` argues manual onboarding would turn the product into consulting. That is a strong product stance, but it also raises the evidence bar: the corpus must eventually show self-serve completion without founder rescue.

## Retention gaps

- The retention theory is good: keep using MAVO if structured requests and opened packages reduce manual work enough to justify the fee.
- The current corpus does not yet show month-three behavior, repeat paid accepts after free trials, churn reasons, or return-to-WhatsApp rates.
- The right retained-use owner already exists in metrics/pilot docs, but currently it is instrumentation, not evidence.

## Risk gaps

- The risk boundary is one of the stronger current chains: no marketplace, no cashier, no quality arbiter, no production owner.
- Commercial trust is the unresolved risk: a thin boundary reduces liability, but may also make MAVO feel less safe if buyers/studios expect guarantees.
- Legal-country validation remains pending; current legal frame should not be treated as closed.

## Reality gap

The corpus is honest about reality status: the model is alive, coherent, and testable, but not proven. The strongest reality anchors are pilot design and go/no-go metrics, not observed studio retention. Therefore:

- **Traceability:** yellow-green. Most links have current owner anchors and explicit caveats.
- **Empirical proof:** yellow-red. Pilot proof, month-three retention, alternative defeat, and first real production package are not present.
- **Overall STUDIO-01 verdict:** **yellow**.

I would not mark this red because the chain is not hand-wavy: it has clear current owners, a precise money/file gate, a self-serve onboarding model, a first-order path, and explicit falsification criteria. I would not mark it green because the corpus itself says the adoption economics and retention proof remain hypotheses.
