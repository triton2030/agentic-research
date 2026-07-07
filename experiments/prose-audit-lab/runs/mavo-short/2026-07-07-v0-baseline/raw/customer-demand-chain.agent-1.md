# CUSTOMER-01 Chain Audit - agent-1

Verdict: **yellow**

Target corpus: `/Users/triton/Documents/mavo-short/`
Test file: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/suite/customer-demand-chain.test.md`
Raw output: `/Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/runs/2026-07-07/raw/customer-demand-chain.agent-1.md`

## Scope and Tool Notes

- Scope followed `corpus.md`: primary current corpus only. Future-only and `_workspace` were not promoted into the verdict.
- Root context read first: `README.md`, `AGENTS.md`, `_ops/GOAL.md`.
- Relevant local `AGENTS.md` files read before owner evidence:
  - `01_Описание_бизнеса/AGENTS.md`
  - `01_Описание_бизнеса/01_Что_такое_МАВО/AGENTS.md`
  - `01_Описание_бизнеса/03_Как_это_работает/AGENTS.md`
  - `01_Описание_бизнеса/00_Анализ_рынка/AGENTS.md`
  - `01_Описание_бизнеса/04_Как_запускаем/AGENTS.md`
  - `02_Веб_приложение/AGENTS.md`
  - `02_Веб_приложение/Реестр_возможностей/AGENTS.md`
  - `02_Веб_приложение/Страницы/AGENTS.md`
  - `Бизнес_Анализ/AGENTS.md`
  - `Данные_снаружи/AGENTS.md`
- `md status` returned a fresh corpus, with no `NO_INDEX`.
- `md search-read` was useful for discovery but unstable: one query succeeded, while another concurrent semantic query returned `index_busy`. Exact verdict evidence below is from direct `rg` / `nl` / `sed` reads.

## Short Verdict

The corpus **does hold a traceable chain** from buyer pain to studio storefront request and paid `Принять`: buyer wants a personal product without chat anxiety; MAVO promises a white-label studio storefront with SKU-based controlled personalization; the web surface walks the buyer through product, personalization, request, stable link and status; the studio then decides and pays MAVO on `Принять`, which opens the print package.

It is **not green** because the corpus itself treats the decisive commercial chain as unproven: direct payment to the studio, trust transfer from studio link to structured request, buyer conversion after acceptance, and studio willingness to pay are launch hypotheses. The chain is coherent and falsifiable, but current proof is a pilot plan plus external research, not observed demand.

## Chain Links

### L1. Buyer Pain / JTBD

**Claim**

The buyer has a real job: get a personal, gift-like or small custom printed product quickly, without a painful chat/design process, while still understanding result, price, timing and who is responsible.

**Data anchor**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:11-20` says the current path is WhatsApp/Instagram, idea explanation, waiting for mockup, edits/payment agreement; it is slow and uncertain.
- `.../Проблемы_покупателей.md:22-34` says some buyers drop before ordering; the external evidence warns that no-chat storefronts do not close purchase if direct payment lacks order ID, check, rework/refund policy or status.
- `.../Психология_покупателя.md:18-25` frames the desired behavior as familiar online purchase plus personal object, not blank canvas or chat.
- `.../Психология_покупателя.md:77-105` lists buyer desires: special product, fast path without chat, confidence in date/result/payment/next step.
- `01_Описание_бизнеса/00_Анализ_рынка/Сценарии_спроса.md:11-16` states the demand is a social task: fast personal thing, no-chat possible only if result/date/payment risk are handled.
- `Бизнес_Анализ/Суть_рынка.md:8-15` summarizes the market gap: buyer wants to see a variant, personalize a template, understand the studio and submit a request.

**Warrant**

If the buyer already wants a personal object but the old path forces chat, uncertainty and manual coordination, a structured storefront can reduce friction enough to create a request.

**Qualifier**

The buyer is not asking for a complex editor. The intended shape is a ready SKU plus 0-3 safe fields and preview, not full custom design.

**Rebuttal / risk**

The same files name the weak point: trust does not automatically transfer from online catalog habit to an unknown direct studio payment. The pain is plausible, but demand is not proven by current MAVO traffic.

**Audit status**

Holds as a current hypothesis with strong internal traceability and external-support anchors.

### L2. MAVO Promise to Buyer

**Claim**

MAVO promises the buyer a short, simple path to a personal studio-made product through a concrete studio storefront: choose SKU, personalize safely, submit structured request, then follow a stable request link.

**Data anchor**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8` defines MAVO as a white-label storefront for print studios with catalog, SKU, controlled personalization and structured request; the studio remains seller/executor.
- `.../Что_такое_MAVO.md:22-27` states the star goal: make ordering from a small studio максимально легко и просто by replacing chaotic request with structured request.
- `.../Что_такое_MAVO.md:32-37` promises no mandatory registration, payment outside MAVO, mobile-first path, minimum chats, ready variants plus settings.
- `.../Что_такое_MAVO.md:52-56` says buyers get a short path to a personal product without painful chat.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:14-20` says the buyer receives choice before send, then number/stable link/summary/visible studio, and after `Принять` status and next step.
- `.../Контракт_сторон.md:47-55` specifies the buyer-facing promise around order number, stable link, request summary, next payment step and clear external payment context.

**Warrant**

The promise matches the pain: remove blank-canvas uncertainty and chat dependence while keeping studio identity and request traceability visible.

**Qualifier**

MAVO does not promise production, delivery, physical quality, warranty or refund handling. Those remain in the studio-buyer contour.

**Rebuttal / risk**

The promise may be weaker than marketplace expectations because MAVO intentionally does not provide cashier/payment protection, delivery guarantee or quality arbitration.

**Audit status**

Holds, but it is a bounded promise. The corpus is clear that this is a storefront/request promise, not a marketplace guarantee.

### L3. Concrete Product Mechanism

**Claim**

The mechanism is concrete enough for design/dev to violate: studio storefront -> product/SKU -> limited personalization -> cart/request -> stable request page -> studio queue -> `Принять` opens snapshot/files/paid row.

**Data anchor**

- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:12-18` names the short path from studio storefront to structured request and paid `Принять`.
- `.../_Путь_покупателя.md:31-38` maps the business sequence: collected in storefront, sent, transferred, `Принять` creates snapshot/open packages/paid rows, then studio invoices, takes payment, prints and gives.
- `.../_Путь_покупателя.md:42-49` says buyer acts inside a concrete studio storefront, chooses design, fills fields and contacts, pays studio, no MAVO production/delivery/refund/quality promise, no registration.
- `.../_Путь_покупателя.md:73-81` says before `Принять` the studio sees enough request data and preview, but no source/print-ready files; on `Принять` it receives full package and snapshot.
- `.../Путь_покупателя/Карта_рубежей.md:15-21` defines visible product link, request sent, `Принять`, `Оплачено`, pause/dispute as rubicons.
- `.../Путь_покупателя/Снимок_что_замораживается_на_Принять.md:14-32` defines immutable snapshot contents and says changed base requires cancel/refund/new request, not silent edit.
- `01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Обработка_заявок.md:16-25` defines `Принять` / `Отклонить`; `Принять` creates snapshot, opens print files and paid rows.
- `01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10-23` says buyer pays studio; studio pays MAVO for accepted position; paid unit is opening package on `Принять`, not sending request or buyer `Оплачено`.
- `_context-base/CTX-013_Принять_открывает_файл.md:19-30` repeats the invariant: `Принять` fixes snapshot, debits balance and opens print-ready package; `Оплачено` is external.
- `02_Веб_приложение/Подготовка_к_разработке/Поведение_веб_продукта_L6.md:19-37` defines the first web slice and stored facts.
- `.../Поведение_веб_продукта_L6.md:74-84` forbids opening a package before accept, giving buyer print-ready files, making MAVO cashier, silently changing snapshot, requiring registration or turning the surface into marketplace/gallery.

**Warrant**

The flow converts a vague buyer intent into a decision-ready packet for the studio, while `Принять` is the economic and file-access boundary that makes the studio pay only for accepted work.

**Qualifier**

The buyer does not directly trigger MAVO payment. Paid `Принять` is a studio action after receiving a structured buyer request.

**Rebuttal / risk**

This proves product mechanics, not buyer demand. It also protects MAVO/file economics more directly than it protects the buyer from studio execution risk.

**Audit status**

Strong. This is the best-supported chain segment.

### L4. Trust, Payment, File Readiness, Production, Pickup, Returns

**Claim**

The corpus intentionally places payment, production, pickup, quality and returns in the studio-as-seller boundary, while MAVO provides request traceability, snapshot, stable link, file gate and internal paid-event trace.

**Data anchor**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:56-65` says direct payment requires a clean handoff: seller, order number, contact and next payment step; quality/refunds remain with the studio.
- `.../Контракт_сторон.md:66-71` says on `Принят` MAVO guarantees snapshot/files/paid event, while `Оплачено` is external and not a file gate.
- `01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:10-19` says MAVO is platform/infrastructure, not shop, cashier or quality arbiter.
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:22-31` says buyer accepts the request goes to studio; payment is between buyer and studio; quality/deadline/pickup/return are studio responsibility; MAVO records events/files/paid event.
- `_context-base/CTX-014_Качество_остаётся_у_студии.md:20-30` says MAVO does not guarantee physical execution; studio owns deadlines, pickup, returns, conversations and quality; there are no current quality sanctions.
- `_context-base/CTX-020_Storefront_без_трекинга.md:18-30` says stage 1 is a thin storefront with accepted status, stable link, order number, next step and snapshot, not a live production tracker.
- `_context-base/CTX-026_Без_надзора_за_студией.md:18-35` says MAVO does not monitor studios, quality or fraud; buyer pays studio directly; reputation/fraud tools are future.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Доверие_покупателя_к_студии.md:14-28` says buyer trust belongs to the studio link; MAVO must show studio identity, photos, deadline, price, order number/link/summary and post-accept next payment step.
- `.../Доверие_покупателя_к_студии.md:36-40` explicitly marks trust transfer and direct payment as a pilot risk.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Корзина/Корзина.md:27-38` requires buyer acknowledgement: request goes to studio, payment is direct to studio, quality/deadlines belong to studio, preview is visual orientation.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_заказа/Страница_заказа.md:57-67` says the request page is not a production, payment, delivery or refund tracker.

**Warrant**

The boundary is coherent: MAVO avoids becoming a marketplace/cashier and keeps its promise to data, files, event trace and structured handoff. This reduces legal/product scope and keeps the first slice buildable.

**Qualifier**

The boundary is not a full buyer-trust solution. It relies on studio identity, external payment context, stable link and buyer expectation-setting.

**Rebuttal / risk**

This is the main yellow risk. External evidence and corpus notes say direct payment to an executor is the highest-friction point unless formal invoice/order ID/check/refund/status/rework policy are credible. MAVO's current boundary may be too thin to make the buyer continue to payment after `Принять`.

**Audit status**

Holds as a boundary. Weak as proof of conversion.

### L5. Why Buyer Does Not Simply Use Old Offline / Chat Flow

**Claim**

MAVO's alternative to old flow is not "another chat"; it is a structured request from ready studio products with bounded personalization, preview, price/deadline, stable link and status.

**Data anchor**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:11-20` describes old flow as chat, unclear result, unclear price/deadline and fear of being misunderstood.
- `01_Описание_бизнеса/00_Анализ_рынка/Рыночные_паттерны_заказа.md:19-30` says mature systems split quote/proof/payment/status and do not force everything into chat.
- `.../Рыночные_паттерны_заказа.md:49-68` says buyer needs a return point to a concrete order; a storefront is strong because it defines available goods, editable fields, safe quantities/materials/deadlines and approval.
- `01_Описание_бизнеса/00_Анализ_рынка/Соседние_модели_рынка.md:87-94` says local studios without a digital layer create chat chaos; MAVO must be faster and clearer than direct messenger.
- `.../Соседние_модели_рынка.md:95-101` says freelancers/Canva force the buyer to formulate style/design; if MAVO does not reduce time and error risk, it loses even against free paths.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_товара/Кастомизатор.md:12-21` limits customization to no edit or up to 3 fields with live preview, explicitly not prompt-to-design.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Корзина/Корзина.md:14-25` gathers final adequate request data: studio, positions, mockups, price, contacts, pickup, conditions and send button.
- `Данные_снаружи/Parallel-ai/Как_продавать_кастомную_печать_без_переписки.md:93-106` says habit transfers to design choice/form/order, but breaks on direct payment to an unknown executor; formal order artifacts make the hypothesis stronger.

**Warrant**

MAVO wins over chat if it makes the order feel already shaped: known SKU, bounded fields, visible preview, price/deadline and post-send trace. This removes the buyer's hardest cognitive work.

**Qualifier**

Contact with studio remains available as secondary support, and after acceptance the buyer-studio contour resumes.

**Rebuttal / risk**

The corpus does not prove the buyer will prefer the structured path once direct payment or trust gets difficult. It explicitly says return to WhatsApp/manual prepress is a pilot signal to watch.

**Audit status**

Holds as a product argument; not yet proven as behavior.

### L6. Reality Check After Launch

**Claim**

The corpus does not pretend the demand chain is already proven. It defines pilot metrics for whether buyer demand, studio acceptance and paid `Принять` actually happen.

**Data anchor**

- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:70-77` says the model is proven by actions: studio publishes a storefront, shares it, gets structured requests, accepts some, and the paid event happens on `Принять`.
- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-31` defines first accepted request with paid position as the first proof.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:32-55` defines demand/request funnel metrics: opened storefront/product, personalized/submitted request, accepted/rejected, repeat accept, paid rows, downstream paid conversion, invalid request, time to decision and source.
- `.../Сбор_аналитики.md:61-76` says manual chat/prepress return, file rework, typical questions and insufficient sample must be tracked; thresholds remain hypotheses until meaningful sample.
- `Бизнес_Анализ/Проверка_пилота.md:16-31` says the pilot must prove buyer submits, studio accepts/rejects, money works, studio brings traffic, trust is enough, and the binding layer works.
- `.../Проверка_пилота.md:45-58` defines a go/no-go sample: 30 days after 3-5 storefronts, 3+ active storefronts, 2+ shared storefronts, measurable open-to-submitted path, 20+ submitted or 3+ accepted; otherwise insufficient sample.
- `.../Проверка_пилота.md:87-119` says demand proof requires the full short path from open/configure/submit through studio decision, paid accept and downstream payment, and specifically compares against direct chat and direct payment breakage.
- `Бизнес_Анализ/Ставка_MAVO.md:46-54` lists what must be true: catalog habit, studio traffic, paid accept, payment trust, SKU factory, printability, economics, solo execution and defensibility.
- `.../Ставка_MAVO.md:64-82` says current proof holes remain and the idea is alive but not proven.

**Warrant**

The reality check is specific enough to falsify the chain. The corpus knows what would make the story fail: no traffic, no submitted requests, no accepts, payment drop-off, manual reversion or no studio willingness to pay.

**Qualifier**

This is a future/pilot validation plan, not current evidence that buyers already reach paid acceptance.

**Rebuttal / risk**

Until the pilot produces those numbers, the chain remains a designed hypothesis. The corpus cannot honestly claim validated customer demand.

**Audit status**

Strong as a test plan. Yellow as current proof.

## Missing or Weak Links

1. **Buyer-to-payment conversion is not currently evidenced.**
   The corpus has a funnel and hypotheses, but no launch data proving that buyers who submit a request continue through studio acceptance and external payment.

2. **Direct payment trust is the largest unresolved buyer-risk link.**
   Current mitigations are studio identity, photos, order number, stable link, summary, contacts and next payment step. The corpus also admits that external direct payment to an executor is a high-risk break point.

3. **Returns/rework/refund expectations are under-specified from the buyer's perspective.**
   The boundary is clear that the studio owns them, but there is no current standardized buyer-protective policy inside MAVO. This is coherent legally, but weak commercially.

4. **Old-flow displacement is argued, not proven.**
   The corpus explains why chat is bad and how structured request is better. It does not yet show that buyers will not revert to WhatsApp once uncertainty, date, price or payment risk appears.

5. **Studio quality/reputation remains mostly external.**
   `CTX-026` explicitly says there is no current oversight of studio behavior. That preserves scope, but makes the buyer's reason to trust the post-acceptance path dependent on the individual studio.

6. **Country-specific legal/payment reality is not closed.**
   The legal frame is a working SaaS/storefront assumption and says country check is still needed before hard reliance.

## Old-Flow Alternative Gaps

The corpus names the alternatives well:

- direct WhatsApp/Instagram order;
- local studio messenger flow;
- Canva/freelancer/self-design paths;
- mass-market marketplace/catalog alternatives;
- studio contact as fallback.

The MAVO answer is also concrete:

- ready studio SKU, not blank design;
- limited personalization with preview;
- price/deadline/pickup shown before request;
- stable request link and status after send;
- structured packet for studio decision;
- paid `Принять` only after studio accepts production.

Gap: none of this yet proves behavioral substitution. If the buyer still needs to negotiate, verify trust, ask about price/deadline or solve payment fear in chat, the path collapses back into the old flow.

## Payment / Trust Boundary Gaps

The boundary is internally consistent:

- buyer pays studio directly;
- studio pays MAVO;
- MAVO is not cashier, marketplace, shop, production guarantor or refund arbiter;
- `Принять` opens files and creates the paid MAVO event;
- `Оплачено` is external and not a file gate.

The commercial gap is also explicit:

- direct payment to a studio may feel unsafe without strong invoice/check/order/rework/refund/status context;
- the stable link and snapshot support traceability, but do not replace payment protection;
- MAVO has no current quality sanctions or studio oversight;
- refund/return/rework policy is pushed to studio, which may be true legally but thin for buyer trust;
- the buyer never sees a MAVO-backed checkout, so marketplace trust habits do not fully transfer.

This is the main reason for **yellow** rather than green.

## Reality Gap

The corpus has a credible pilot measurement plan, but the test asks whether the corpus holds the chain all the way to application and paid `Принять`. It holds it as a **designed and measurable hypothesis**, not as observed reality.

Current reality evidence is not enough for green:

- no current funnel data in corpus;
- no measured submit-to-accept conversion;
- no measured accept-to-downstream-payment conversion;
- no measured proof that direct payment does not break trust;
- no measured proof that buyers prefer this path over chat;
- `Бизнес_Анализ/Ставка_MAVO.md:64-82` explicitly keeps major proof holes open and says the idea is alive, not proven.

## Exact Evidence Index

Core scope / invariants:

- `README.md`
- `AGENTS.md`
- `_ops/GOAL.md:16-18` current model: SaaS studio storefront with MAVO catalog, structured request and paid `Принять`; future gallery/marketplace outside current.
- `_ops/GOAL.md:34-39` core invariants: paid `Принять`, immutable snapshot, buyer pays studio directly, MAVO not cashier/seller, catalog/SKU belongs to MAVO, studio is seller/executor.
- `_ops/GOAL.md:77-78` traceability chain requirement.

Buyer demand / pain:

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:11-34`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:18-25`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:39-71`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:77-128`
- `01_Описание_бизнеса/00_Анализ_рынка/Сценарии_спроса.md:11-37`
- `Бизнес_Анализ/Суть_рынка.md:8-15`

MAVO promise:

- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:22-41`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:52-77`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:14-20`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:38-71`

Product mechanism / web surface:

- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:12-18`
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:31-49`
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:53-123`
- `01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Заказ_покупателя.md:10-16`
- `01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Карта_рубежей.md:15-30`
- `01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Снимок_что_замораживается_на_Принять.md:14-40`
- `01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Статусы_и_события_заказа.md:22-38`
- `01_Описание_бизнеса/03_Как_это_работает/Путь_студии/Обработка_заявок.md:12-29`
- `01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10-45`
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:15-17`
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:32-39`
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:55-57`
- `_context-base/CTX-013_Принять_открывает_файл.md:19-41`
- `02_Веб_приложение/Подготовка_к_разработке/Поведение_веб_продукта_L6.md:19-84`
- `02_Веб_приложение/Реестр_возможностей/Покупатель.md:20-85`
- `02_Веб_приложение/Страницы/Карта_страниц_и_пути/10_Путь_покупателя.md:15-62`
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Главная/Главная.md:18-54`
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Каталог/Каталог.md:18-73`
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_товара/Страница_товара.md:15-61`
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_товара/Кастомизатор.md:12-54`
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Корзина/Корзина.md:10-65`
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_заказа/Страница_заказа.md:15-67`

Trust / legal / responsibility:

- `01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:10-39`
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:15-31`
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Юридическая_рамка.md:49-54`
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Споры_исключения_и_кто_отвечает.md:13-26`
- `01_Описание_бизнеса/03_Как_это_работает/Юр_детали/Споры_исключения_и_кто_отвечает.md:44-49`
- `_context-base/CTX-014_Качество_остаётся_у_студии.md:20-30`
- `_context-base/CTX-020_Storefront_без_трекинга.md:18-30`
- `_context-base/CTX-026_Без_надзора_за_студией.md:18-35`
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Доверие_покупателя_к_студии.md:14-40`

Old-flow alternatives / market patterns:

- `01_Описание_бизнеса/00_Анализ_рынка/Рыночные_паттерны_заказа.md:19-81`
- `01_Описание_бизнеса/00_Анализ_рынка/Соседние_модели_рынка.md:87-109`
- `Данные_снаружи/Parallel-ai/Как_продавать_кастомную_печать_без_переписки.md:8`
- `Данные_снаружи/Parallel-ai/Как_продавать_кастомную_печать_без_переписки.md:78-80`
- `Данные_снаружи/Parallel-ai/Как_продавать_кастомную_печать_без_переписки.md:93-122`
- `Данные_снаружи/Parallel-ai/Как_продавать_кастомную_печать_без_переписки.md:128-140`
- `Данные_снаружи/Parallel-ai/Лёгкая_логика_заказов_у_печатной_студии.md:23-56`
- `Данные_снаружи/Parallel-ai/Лёгкая_логика_заказов_у_печатной_студии.md:82-119`
- `Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:24`
- `Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:99-104`
- `Данные_снаружи/Parallel-ai/Горячие_заказы_для_малых_студий_печати.md:144-169`

Reality check:

- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-50`
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:17-76`
- `01_Описание_бизнеса/04_Как_запускаем/Стратегия_запуска.md:11-24`
- `01_Описание_бизнеса/04_Как_запускаем/Стратегия_запуска.md:36-46`
- `01_Описание_бизнеса/04_Как_запускаем/Стратегия_запуска.md:63-75`
- `Бизнес_Анализ/Проверка_пилота.md:16-31`
- `Бизнес_Анализ/Проверка_пилота.md:45-69`
- `Бизнес_Анализ/Проверка_пилота.md:87-119`
- `Бизнес_Анализ/Ставка_MAVO.md:12-15`
- `Бизнес_Анализ/Ставка_MAVO.md:46-82`

## Final Rationale

**Why not green:** the current corpus does not prove buyer demand or paid-accept conversion. It states a coherent chain and a test plan, but the decisive links are still hypotheses: direct payment trust, studio-led traffic, buyer preference over chat, studio willingness to pay on `Принять`, and downstream buyer payment.

**Why not red:** the chain is not missing. It is explicit, traceable across business owner files, web behavior, legal/payment boundaries and pilot analytics. It includes concrete product mechanics and named rebuttals.

**Final verdict:** **yellow** - traceable and build-testable chain, but not validated enough to pass as current customer-demand proof.
