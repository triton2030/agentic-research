# STUDIO-01 raw chain audit — agent 2

Target corpus: `/Users/triton/Documents/mavo-short/`
Harness: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/`
Test: `suite/studio-adoption-chain.test.md`
Auditor: independent Chain Auditor, read-only target corpus
Date: 2026-07-07

## Verdict

**yellow**

The corpus holds a coherent and mostly traceable current-model chain for why a studio would try MAVO: small studios have real pain around unpaid prepress, chat chaos, uncertain leads and underused equipment; MAVO answers with a white-label studio storefront, MAVO-owned catalog/SKU, structured request, accept/reject decision, paid `Принять`, and bounded file opening. Safe onboarding and first-order fulfillment are described concretely enough for a pilot.

It is **not green** because the last part of STUDIO-01 is weaker: "continue after month three" is mostly expressed as hypotheses, metrics and post-go checks, not as a current retention mechanism. The corpus measures repeat paid `Принять`, share, active storefronts and return to paid openings, and it names workflow advantage as the retention thesis, but it does not yet prove or fully productize retention after first orders. Reality evidence is a pilot plan plus founder/interview-derived hypotheses and external category evidence, not observed studio usage.

It is **not red** because the chain is not missing or incoherent. The weak links are explicitly marked as hypotheses and tied to pilot signals.

## Scope and tooling

- Harness scope: primary current corpus is root docs, `_context-base`, `Данные_снаружи`, `01_Описание_бизнеса`, `02_Веб_приложение`, `03_Создание_загрузка_дизайнов`, `Бизнес_Анализ` (`corpus.md:5-15`).
- `04_Доп_проекты/**/*.md` was treated as secondary/context-only; future-only material was not promoted into current verdict (`corpus.md:17-20`).
- `_workspace`, `.codex`, `.claude`, `.ignore`, etc. excluded from semantic verdicts (`corpus.md:22-32`).
- `md status /Users/triton/Documents/mavo-short --json` returned `FRESH`, `pending_chunks=0`, `drift_count=0`.
- Tool gap: three concurrent `md search-read` queries returned `index_busy` even though status reported `FRESH`; I recorded this as a tool gap and continued with direct `nl`/`rg` reads. A later `md search-read` succeeded for retention and risk queries.
- Target corpus was not edited.
- Prior raw audit files under harness `runs/**` were not used as evidence.

## Chain Links

### 1. Studio pain or business job

**Claim:** MAVO targets small studios whose pain is not "need a website" but repeated unpaid setup work: chat intake, prepress, design/manager load, weak order boundaries, and the wish for more money/faster process.

**Data / anchor:**
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Проблемы_студий.md:15-17` — small studio work starts in WhatsApp/Instagram and bottleneck is desire-to-printable-file.
- `.../Проблемы_студий.md:21-29` — unpaid prepress, messenger chaos, design load, buyer disappearance, equipment idle.
- `.../Проблемы_студий.md:33-40` — raw lead does not solve SKU/quantity/deadline/file/proof/payment/order-boundary work.
- `.../Психология_студии.md:67-83` — studio wants demand/money and must feel savings in manual correspondence/prepress/admin work.
- `.../Психология_студии.md:106-140` — JTBD: reduce design function, reduce manager coordination, get a packed request rather than a raw lead.
- `Данные_снаружи/Проблемы_prepress_в_полиграфии.md:29-33` and `:47-51` — external packet frames unpaid setup/prepress as the narrow MAVO thesis.

**Warrant:** If the pain is manual uncertainty before payment, the product must reduce uncertainty before the studio commits.

**Qualifier:** The corpus itself limits confidence: universality is not proven; studios with templates, strict intake, or W2P tools may suffer less (`Проблемы_студий.md:45-48`).

**Rebuttal:** If a studio mainly does bespoke creative work, corporate brand-book work, or already has a disciplined order system, the pain link weakens.

### 2. MAVO value against that pain

**Claim:** MAVO's value proposition is traceable: a studio gets a white-label storefront, MAVO catalog/SKU, controlled personalization, structured request, and a paid accept boundary while keeping its brand, buyer relationship and money.

**Data / anchor:**
- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8-20` — top-level flow: buyer configures, studio accepts, MAVO opens kits, buyer pays studio.
- `Что_такое_MAVO.md:52-68` — studios get storefront, SKU, less manual prepress, accepted request, thin post-acceptance contour.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:22-35` — studio receives storefront, catalog, managed request and keeps customer/payment/communication.
- `Контракт_сторон.md:38-45` — MAVO gives data before accept, opens kits/snapshot/paid events on accept.
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_студии.md:10-15` — studio is paying side and seller; MAVO gives tool and does not enter its business.
- `_Путь_студии.md:48-58` — setup creates ready storefront; live storefront brings structured requests.
- `Путь_студии/Обработка_заявок.md:12-25` — each request is a decision packet; `Принять` opens files and creates paid rows.

**Warrant:** The value matches the named pain because it turns a vague chat request into a bounded decision and only charges when the studio accepts the work.

**Qualifier:** The value is explicitly not "MAVO brings platform demand"; the studio's own channel remains the first channel.

**Rebuttal:** If the structured request still requires the studio to re-ask everything or rebuild the file manually, MAVO becomes a prettier lead channel and the value collapses.

### 3. Current alternative and why worse / insufficient

**Claim:** The current alternative is direct chat/email/forms/spreadsheets plus manual prepress. It is cheap and flexible, but insufficient when repeated questions, version confusion, proof cycles and prepress work dominate.

**Data / anchor:**
- `Проблемы_студий.md:15-23` — current order comes through direct conversation and creates chain of manual work.
- `Данные_снаружи/Parallel-ai/Print-Shop_Platforms_Turn_Chaos_Into_Orders.md:38-48` — manual workflow uses WhatsApp/Instagram/email/forms, but creates unstructured work and repeated daily admin.
- `Print-Shop_Platforms_Turn_Chaos_Into_Orders.md:71-79` — manual tools can be enough for tiny/low-volume studios, but paid platform becomes rational when repetition, productized SKUs, costly mistakes and self-service expectations appear.
- `Print-Shop_Platforms_Turn_Chaos_Into_Orders.md:139-148` — comparison: manual chat is flexible but errors hide; W2P standardizes at the cost of less ambiguity.
- `Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:97-104` — cold lead has low willingness to pay; accepted order is recommended.

**Warrant:** MAVO wins only where it reduces the real operational cost of ambiguity, not where it merely adds a form or storefront.

**Qualifier:** The alternative is not always worse. For very small, bespoke, relationship-led or low-volume studios, chat may remain the right tool.

**Rebuttal:** If MAVO cannot beat the old workflow on speed/clarity, switching is irrational.

### 4. Switching cost / onboarding friction and mitigation

**Claim:** The corpus names onboarding friction and gives a current mitigation path: self-serve registration, no manual approval, card/budget upfront, simple storefront setup, capability/availability, pricing and request fields. Founder-touch is allowed only to motivate first studios, not as technical onboarding.

**Data / anchor:**
- `01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Регистрация_студии.md:7-18` — register, bind card, configure storefront, publish link.
- `Регистрация_студии.md:20-25` — why self-serve immediately; manual technical onboarding would turn MAVO into consulting.
- `Путь_студии/Настройка_поверхностей.md:11-19` — studio declares what it can and is willing to sell; both capability and availability are needed.
- `Путь_студии/Настройка_поверхностей.md:21-43` — studio sets print categories, conditions, price, deadlines, pickup/delivery.
- `Путь_студии/Настройка_полей_заявки.md:11-28` — studio controls required fields; MAVO does not judge the one right request shape.
- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:32-45` — minimal pilot path: choose city/segment, connect 3-5 studios, base catalog, launch storefronts, share, first request, accept cycle.
- `04_Доп_проекты/Самые_первые_студии/Подключение_первых_студий.md:38-55` — context-only bootstrap: founder-touch for motivation, target state is self-serve without technical onboarding.

**Warrant:** A studio is more likely to try MAVO if activation is closer to a site builder than an MIS/ERP implementation.

**Qualifier:** Early founder-touch is a secondary support artifact, not current core product. It can help first 3-5 studios but cannot be the scaling mechanism.

**Rebuttal:** If setup requires founder-led handholding for every studio, the corpus itself says this is consulting, not a platform (`Подключение_первых_студий.md:55-66`).

### 5. Retention mechanism after first orders

**Claim:** The corpus has a retention thesis, but not a green current mechanism. Retention is expected to come from workflow advantage, repeated paid `Принять`, catalog/SKU reuse, storefront sharing, and post-go measurement; support automation is secondary/context-only.

**Data / anchor:**
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Психология_студии.md:172-177` — explicit hypothesis: retention depends on workflow advantage, not structural lock.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:17-30` — supply funnel measures registration to live storefront and repeated paid `Принять`; tracks studios that stop returning.
- `Сбор_аналитики.md:44-55` — repeated `Принять` and paid rows are willingness-to-pay signal.
- `Бизнес_Анализ/Проверка_пилота.md:70-85` — post-go growth checks include storefronts, share, requests, paid openings, downstream conversion; thresholds remain hypotheses until real sample.
- `03_Создание_загрузка_дизайнов/Зачем_он_бизнесу.md:19-34` — catalog as reusable asset and repeatable SKU mechanism, but only in connection with request/open-file flow.
- `_context-base/CTX-015_Каталог_и_availability.md:20-40` — catalog accumulation is a hypothesis; if SKU do not create repeat use/conversion, the asset thesis weakens.
- `04_Доп_проекты/ИИ_поддержка.md:19-21` and `:53-65` — secondary/context-only retention support, explicitly not core site and not launch-day.

**Warrant:** A studio continues only if MAVO keeps beating WhatsApp/manual prepress after novelty and free openings. The corpus measures this through repeat paid accept and return-to-workflow signals.

**Qualifier:** This is the weakest required link. The current corpus does not yet give a concrete month-three retention loop beyond "workflow stays useful" plus metrics.

**Rebuttal:** If studios accept a few trial requests but stop sharing, stop paying, or return to WhatsApp/manual prepress, retention fails even if onboarding and first orders worked.

### 6. Risk handling: quality, direct payment, no marketplace policing

**Claim:** The corpus is strong and consistent on the risk boundary: quality, payment from buyer, production, pickup, returns and buyer relationship remain with the studio; MAVO is not a marketplace, cashier, seller, production operator or quality police.

**Data / anchor:**
- `_ops/GOAL.md:34-42` — immutable core: buyer pays studio directly; MAVO not cashier/seller; studio is seller and performer.
- `Что_такое_MAVO.md:38-47` — buyer pays studio, studio pays MAVO; roles and owned assets separated.
- `Контракт_сторон.md:47-65` — buyer gets number/link/summary/payment handoff; MAVO does not promise production, delivery, physical guarantee or refunds.
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:94-113` — two money flows; MAVO sees its own contour, not bank transfer, production or quality.
- `_context-base/CTX-014_Качество_остаётся_у_студии.md:20-40` — quality remains with studio; no current sanctions/quality metrics.
- `_context-base/CTX-026_Без_надзора_за_студией.md:18-38` — MAVO does not verify studio, observe buyers, judge print quality or hunt fraud; only money/legal access interventions.
- `01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:15-38` — three "not": not shop, not cashier, not quality arbiter.

**Warrant:** This protects current scope from accidentally importing marketplace duties that would make onboarding/risk heavier and contradict the model.

**Qualifier:** It handles model boundary, not market trust. Direct payment and lack of marketplace protection are still adoption risks.

**Rebuttal:** If buyers or studios require MAVO to guarantee production quality or process payment, the core model breaks rather than needing a UI tweak.

### 7. Reality check: interviews, pilot, or usage signal

**Claim:** The corpus has a clear validation plan and some founder/interview/category evidence, but no live usage proof. Reality check is therefore yellow: falsifiable, not validated.

**Data / anchor:**
- `Бизнес_Анализ/Проверка_пилота.md:16-25` — what to prove first: buyer submits, studio accepts/declines, money, storefront as first channel, trust, linked layer, hypotheses updated by facts.
- `Проверка_пилота.md:27-33` — starting contour explicitly includes adoption friction, first bottleneck, return to chat/manual prepress.
- `Проверка_пилота.md:45-58` — decision window, minimum sample, economic sample and insufficient-sample rule.
- `Проверка_пилота.md:60-69` — go/pivot/no-go verdict map.
- `Проверка_пилота.md:100-113` — unresolved pilot questions include willingness to pay, prepress reduction, first adoption bottleneck, WhatsApp/manual prepress fallback, breakeven and channel.
- `Бизнес_Анализ/Ставка_MAVO.md:46-54` — core success links marked as hypotheses and what would prove them.
- `Ставка_MAVO.md:56-63` — kill criteria: studios do not pay after trials, negative contribution, insufficient sample, direct payment breaks trust.
- `Ставка_MAVO.md:80-82` — dated verdict: idea alive, not proven.

**Warrant:** The chain is auditably testable because the corpus names observable signals and failure modes.

**Qualifier:** The test file asks whether the chain exists; it does not ask whether market truth is already proven. Harness also says the pilot tests traceability/internal coherence, not market truth (`README.md:14-15`).

**Rebuttal:** Until actual studios publish, share, accept, pay after trials and continue after month three, the corpus cannot claim adoption proof.

## Missing / weak links

1. **Month-three retention mechanism is underbuilt.**
   There are metrics and hypotheses (`Сбор_аналитики.md:17-30`, `Проверка_пилота.md:70-85`) and one explicit workflow-retention hypothesis (`Психология_студии.md:172-177`), but no current owner section that explains the concrete loop: what keeps a studio returning in month three after trial openings, first paid accepts and initial novelty.

2. **Support retention lives outside core.**
   `04_Доп_проекты/ИИ_поддержка.md:19-21` names a retention tool, but `:40-51` says it is not the core site and not a rules source; `:53-59` says not launch day. It cannot make STUDIO-01 green for current adoption.

3. **Willingness to pay after free openings is a hypothesis.**
   Strong anchors exist (`Проверка_пилота.md:89-98`, `Ставка_MAVO.md:46-49`), but no actual usage data.

4. **Current alternative is well described, but the "why this studio will not just use WhatsApp after first order" answer is still pilot-grade.**
   The corpus knows to measure WhatsApp/manual-prepress fallback (`Проверка_пилота.md:104-110`, `Сбор_аналитики.md:61-68`) but does not yet prove it.

5. **Founder/interview quotes are useful but not enough.**
   `Психология_студии.md:58-61`, `:77-83`, `:89-95`, `:112-124`, `:130-136` provide qualitative anchors, but they are not a live adoption signal from connected studios.

## Current alternative gaps

- Manual chat is not always worse (`Print-Shop_Platforms_Turn_Chaos_Into_Orders.md:71-75`). For low-volume/bespoke studios, MAVO may add friction.
- Generic W2P/MIS tools are stronger where repeated B2B portals and reorders exist (`Print-Shop_Platforms_Turn_Chaos_Into_Orders.md:79-80`, `:143-150`), but heavier to implement. MAVO's "lighter" position is plausible, not proven.
- Raw-lead framing is explicitly dangerous (`Горячие_заказы_для_малых_студий_печати.md:97-104`, `:142-156`). MAVO avoids it, but must actually deliver accepted order packet quality.
- Proof/preflight/IP/file-quality risk remains a make-or-break current alternative gap (`Горячие_заказы_для_малых_студий_печати.md:124-140`).

## Onboarding gaps

- Self-serve is a strong current design (`Регистрация_студии.md:20-25`), but the pilot still expects founder-touch for first studios as motivation (`Подключение_первых_студий.md:38-55`).
- Access model for employee vs owner remains a founder-gap (`02_Веб_приложение/Реестр_возможностей/Сотрудник_студии.md:62-70`; `Реестр_возможностей/README.md:56-63`).
- First-order anxiety is named (`Психология_студии.md:31-37`), and the web/product path addresses it, but I did not find a current owner checklist that fully closes first-order operator guidance.

## Retention gaps

- Retention is measured, not fully designed: repeated paid `Принять`, stopped returns, share and paid openings are metrics (`Сбор_аналитики.md:17-30`, `:44-55`), not a retention program.
- Catalog repetition is plausible but marked as hypothesis (`CTX-015:20-40`; `Жизненный_цикл_каталога.md:45-56`).
- Month-three timing appears as a test requirement, but current corpus uses pilot/post-go windows, 90-day or 100-submitted-request review points, not a studio month-three retention playbook (`Проверка_пилота.md:85`).

## Risk gaps

- The no-policing boundary is clear, but it may weaken buyer trust and therefore studio adoption. This is acknowledged as a hypothesis in `Ставка_MAVO.md:49` and kill criterion in `:62`.
- Quality remains with the studio, but bad files/IP/proof can still make MAVO look like the source of bad orders (`Горячие_заказы_для_малых_студий_печати.md:124-140`).
- The corpus correctly refuses marketplace controls, but that means fewer levers if a studio behaves badly; current answer is boundary, not mitigation.

## Reality gap

The corpus is honest that STUDIO-01 is still an adoption hypothesis:

- No live connected-studio usage data in the current corpus.
- No proof of repeated paid `Принять` after free openings.
- No proof that studios keep sharing storefronts after initial setup.
- No proof that request quality beats WhatsApp/manual prepress under real pressure.
- No month-three retained cohort.

The current strongest reality oracle is the pilot plan:

- 3-5 published storefronts, 2+ actually sharing, path to submitted and accepted requests, willingness to pay after trial openings, downstream paid conversion and enough sample (`Проверка_пилота.md:45-58`, `:60-69`, `:100-113`).

## Evidence index

- Harness: `experiments/prose-audit-mavo-short/suite/studio-adoption-chain.test.md:13-33`
- Scope: `experiments/prose-audit-mavo-short/corpus.md:5-32`
- Current model: `README.md:43-47`, `_ops/GOAL.md:12-15`, `_ops/GOAL.md:34-42`
- First answer: `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8-20`, `:38-47`, `:52-77`
- Audience/pain: `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория.md:32-40`, `Аудитория/Проблемы_студий.md:15-48`, `Аудитория/Психология_студии.md:16-177`, `Аудитория/Подходящие_студии.md:28-40`
- Studio path: `01_Описание_бизнеса/03_Как_это_работает/_Путь_студии.md:10-66`, `Путь_студии/Регистрация_студии.md:7-35`, `Путь_студии/Настройка_поверхностей.md:11-55`, `Путь_студии/Обработка_заявок.md:8-33`
- Money / accept: `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:12-40`, `:73-113`, `_Фин_модель.md:10-53`, `Фин_модель/Кредитная_система.md:9-41`, `Фин_модель/Сервисный_сбор.md:15-61`
- Risk boundary: `_context-base/CTX-014_Качество_остаётся_у_студии.md:20-40`, `_context-base/CTX-026_Без_надзора_за_студией.md:18-38`, `01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:10-38`
- Web/capability layer: `02_Веб_приложение/Реестр_возможностей/Студия_владелец.md:21-74`, `Сотрудник_студии.md:20-70`, `Подготовка_к_разработке/Как_приступаем.md:15-36`, `Поведение_веб_продукта_L6.md:19-84`
- Launch/pilot: `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-64`, `Сбор_аналитики.md:17-76`, `Каналы_привлечения/Каналы_привлечения.md:11-89`, `Стратегия_запуска.md:17-77`
- Business analysis: `Бизнес_Анализ/Привлечение_студий.md:14-68`, `Выгода_студии_в_цифрах.md:7-23`, `Проверка_пилота.md:16-132`, `Ставка_MAVO.md:12-82`, `Экономика_каналов.md:8-47`
- Catalog/repetition: `_context-base/CTX-015_Каталог_и_availability.md:20-40`, `03_Создание_загрузка_дизайнов/Зачем_он_бизнесу.md:19-56`, `Жизненный_цикл_каталога.md:45-71`
- External category evidence inside corpus: `Данные_снаружи/Проблемы_prepress_в_полиграфии.md:10-58`, `Данные_снаружи/Parallel-ai/Print-Shop_Platforms_Turn_Chaos_Into_Orders.md:38-80`, `:119-154`, `Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:89-169`, `Данные_снаружи/Parallel-ai/Лёгкая_логика_заказов_у_печатной_студии.md:20-32`, `:60-66`, `:142-149`

## Final answer

STUDIO-01 is **yellow**: traceable current adoption chain exists, but month-three retention and real willingness-to-pay remain hypotheses with pilot metrics, not proven or fully productized current truth.
