# CUSTOMER-01 raw audit — agent-2

verdict: yellow
auditor: independent Chain Auditor
target corpus: /Users/triton/Documents/mavo-short/
audit harness: /Users/triton/Documents/GitHub/agentic-research/experiments/prose-audit-mavo-short/
test: suite/customer-demand-chain.test.md
raw output: runs/2026-07-07/raw/customer-demand-chain.agent-2.md
date: 2026-07-07

## Scope and tooling

Primary current corpus was taken from `corpus.md`: `README.md`, `AGENTS.md`,
`_ops/GOAL.md`, `_context-base/**`, `Данные_снаружи/**`,
`01_Описание_бизнеса/**`, `02_Веб_приложение/**`,
`03_Создание_загрузка_дизайнов/**`, `Бизнес_Анализ/**`.
Future-only material and `_workspace/**` were not promoted into the current
verdict.

Tool status:

- `md status /Users/triton/Documents/mavo-short --json`: index state `FRESH`,
  no active lock.
- `md search-read`: one buyer/pain query returned usable hits; two parallel
  semantic queries hit `index_busy` on `.md-navigator/index.lock`.
- Fallback: exact evidence gathered with direct `rg` / `nl` reads.
- Target corpus was not edited. The only write is this raw audit file.

## Verdict

Yellow.

The corpus does hold a coherent and traceable designed chain from buyer pain to
structured request and paid `Принять`. The chain is not vague: it is grounded in
business owners, page-route owners, finance/legal owners, launch metrics, and
external-risk notes. A designer or developer can violate it concretely by adding
MAVO checkout, mandatory buyer registration, production tracking, a generic
marketplace gallery, missing stable link, missing acceptance disclosure, file
access before `Принять`, or by treating `Оплачено` as the MAVO file/payment
boundary.

It is not green because the causal claim "buyer will reach request and then the
studio will press paid `Принять`" remains explicitly unproven. The corpus marks
the decisive links as hypotheses: transfer of catalog habit to custom studio
orders, buyer trust under direct studio payment, studio traffic/share behavior,
studio willingness to pay for accepted kits, and downstream paid conversion.

It is not red because I found no current-owner contradiction. The model is
consistent about the studio being seller/executor, buyer payment staying outside
MAVO, `Принять` opening the print-ready package and creating the MAVO paid event,
and future-only marketplace/payment/quality-control expansions staying outside
the current verdict.

## Chain links

### 1. Buyer pain / JTBD

claim:
Buyer wants a personal/non-mass-market item but the current studio path is too
chat-heavy, unclear, and risky before payment.

data-anchor:

- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Проблемы_покупателей.md:13-25`
  says the current flow is WhatsApp/Instagram, idea explanation, waiting for a
  mockup, unclear price/timing, fear of misunderstanding, and that some buyers
  do not order because the chat barrier comes before payment.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Психология_покупателя.md:22-25`
  frames the primary demand as wanting a unique/non-mass-market product and the
  secondary demand as wanting a familiar catalog-like path.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория.md:25-30`
  names the buyer desire and fear: unique thing, short path, unknown studio,
  direct payment, and loss of control.
- `Бизнес_Анализ/Суть_рынка.md:8-14` defines the market gap as personal-product
  desire colliding with small-studio manual chaos.

warrant:
The pain is not "no catalog exists"; it is that a custom-print desire currently
becomes a risky conversation before the buyer has enough shape, price, preview,
or confidence.

qualifier:
The buyer psychology file says the catalog-path transfer is a hypothesis until
pilot evidence (`Психология_покупателя.md:22-25`), and anti-segments should not
be fixed before conversion/return data (`Психология_покупателя.md:134-141`).

rebuttal:
The corpus names serious substitutes: direct studio/WhatsApp, Canva/freelancer,
and mass-market goods. If MAVO does not reduce time/risk or provide a more
interesting personal result, it can lose to all three
(`Бизнес_Анализ/Соседние_модели_рынка.md:87-109`).

### 2. MAVO promise to buyer

claim:
MAVO promises a short, understandable path from a concrete studio vitrine to a
structured request for a personal product. It does not promise platform checkout,
production guarantee, delivery, refund, or arbitration.

data-anchor:

- `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:8-20`
  defines MAVO as Web-to-Print SaaS / white-label vitrine where the buyer
  chooses/configures/sends a request to the studio; studio remains seller and
  executor; MAVO opens print-ready kits on `Принять`.
- `Что_такое_MAVO.md:22-40` says the promise is "as easy/simple as possible",
  structured request instead of chaotic chat, visible preview/valid parameters,
  no mandatory registration, and payment outside MAVO.
- `Что_такое_MAVO.md:52-68` says the buyer needs a short path to a personal
  product without torturous chat, through catalog/SKU, capability, studio
  vitrine, structured request, and accepted request.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:14-20`
  states what the buyer gets before/after submit and after `Принять`.
- `Контракт_сторон.md:47-55` explicitly denies production statuses, delivery,
  guarantee, refund from MAVO, chat, and tracker as part of the buyer promise.

warrant:
Ready SKU + limited personalization + preview + structured request can remove
the blank-canvas/chat problem without turning MAVO into a marketplace, checkout,
or production supervisor.

qualifier:
The promise is deliberately narrow. The buyer pays studio directly, and MAVO's
obligation is its own contour: submit/accept/snapshot/files/paid event.

rebuttal:
This narrowness creates the main weak point: if the direct-payment handoff feels
like a gray transfer, the easy-front promise may collapse at the payment/trust
boundary.

### 3. Product surface mechanism

claim:
The web corpus gives a falsifiable mechanism for how the buyer reaches a request:
studio vitrine -> product -> personalization -> cart/request assembly -> sent
request -> stable order link/status -> studio-side payment next step.

data-anchor:

- `02_Веб_приложение/Реестр_возможностей/Покупатель.md:16-24`
  says the buyer enters a concrete studio vitrine, chooses product, sends
  request, returns by stable link, and pays the studio directly.
- `02_Веб_приложение/Реестр_возможностей/Покупатель.md:72-85`
  lists screens and excludes general studio choice, checkout, and full account.
- `02_Веб_приложение/Страницы/Карта_страниц_и_пути/10_Путь_покупателя.md:15-27`
  maps the route from studio vitrine through product/personalization/request to
  stable link, status, and direct payment.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Путь_пользователя.md:37-44`
  gives concrete steps: main/catalog/product/cart/request page, with no MAVO
  payment.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_товара/Страница_товара.md:17-28`
  specifies preview, customizer, surface, quantity, studio, trust signals,
  term/pickup, price, and `Проверить заявку`.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Корзина/Корзина.md:10-38`
  defines the final request assembly, mandatory contact, acceptance disclosure,
  and `Отправить заявку`, while excluding MAVO payment.
- `02_Веб_приложение/Страницы/Страницы_для_юзеров/Страница_заказа/Страница_заказа.md:15-49`
  defines receipt/stable link/status and next step to pay the studio after
  `Принят`.

warrant:
The mechanism is operational, not slogan-level. A page owner can test whether a
screen has the necessary transition, disclosure, stable link, status, and
boundary.

qualifier:
The page corpus is a projection layer. `02_Веб_приложение/AGENTS.md:17-24`
keeps business rules, money, and obligations in `01_Описание_бизнеса`.

rebuttal:
Some conversion assumptions are still unresolved. For example, homepage manual
curation is not solved (`Главная.md:40-44`). More importantly, correct screens
do not prove buyer trust or studio acceptance.

### 4. Paid `Принять` boundary

claim:
The paid MAVO boundary is studio `Принять`, not buyer submit and not external
`Оплачено`. On `Принять`, MAVO freezes the snapshot, opens print-ready packages,
and creates paid service lines.

data-anchor:

- `_ops/GOAL.md:34-42` defines the current core: `Принять` is the paid boundary;
  buyer pays studio directly; MAVO is not cashier/seller; studio owns production,
  payment, pickup, and returns.
- `01_Описание_бизнеса/03_Как_это_работает/_Путь_покупателя.md:31-40`
  shows the transition table: sent request, studio evaluation, `Принять`, files,
  paid lines, then studio-side invoice/payment/production/pickup.
- `_Путь_покупателя.md:94-103` states buyer pays studio, studio pays MAVO, and
  no valid `Принять` means no file and no paid line.
- `_context-base/CTX-013_Принять_открывает_файл.md:15-30` says the file opens
  when the studio presses `Принять`, while `Оплачено` is an external studio-side
  event.
- `01_Описание_бизнеса/03_Как_это_работает/Путь_покупателя/Снимок_что_замораживается_на_Принять.md:14-40`
  lists snapshot fields and says the snapshot proves file/paid line/opening and
  version, not physical quality.
- `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:32-39`
  says the service fee is charged on `Принять`, not when balance is missing, no
  accept happens, or MAVO has an error.

warrant:
The studio pays for a valuable accepted-request packet: configured request,
frozen version, and print-ready file. File-gating protects catalog value and
prevents MAVO from charging before the studio takes responsibility.

qualifier:
The model assumes the studio sees enough pre-accept data and that the preview /
file gate discourages bypass. That assumption is explicitly named in
`_context-base/CTX-013_Принять_открывает_файл.md:39-41`.

rebuttal:
`Принять` is a studio willingness-to-pay action, not a buyer-only conversion.
The corpus has a designed route to it, but not proof that studios will press it
often enough after real buyer submissions.

### 5. Payment, trust, production, pickup, returns

claim:
The corpus has a consistent studio-as-seller boundary and several trust
mitigations, but this is the weakest current link and stays yellow.

data-anchor:

- `01_Описание_бизнеса/01_Что_такое_МАВО/Контракт_сторон.md:56-64`
  says demand is not promised, direct payment requires handoff, and physical
  result remains with the studio.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Аудитория/Покупатели_студий/Доверие_покупателя_к_студии.md:22-28`
  names the required trust chain: studio identity, city/photos/terms/price/rating,
  request number, stable link, summary, who received it, and next payment step.
- `Доверие_покупателя_к_студии.md:38-40` marks trust transfer and direct payment
  fear as hypotheses/risks.
- `Психология_покупателя.md:51-68` says direct payment cannot be an opaque
  transfer, and stable link / next-action clarity reduce loss of control.
- `01_Описание_бизнеса/03_Как_это_работает/_Юр_детали.md:21-38` assigns buyer
  attraction, trust, refund, quality, timing, pickup, and delivery to the studio,
  while MAVO owns technical/file/snapshot/financial/catalog contour.
- `_context-base/CTX-014_Качество_остаётся_у_студии.md:22-30` says MAVO does not
  guarantee physical fulfillment and has no current sanctions or quality metrics.
- `_context-base/CTX-026_Без_надзора_за_студией.md:20-35` says MAVO does not
  inspect studios, supervise buyers, judge quality/fraud, or provide current
  quality sanctions.
- `Данные_снаружи/Parallel-ai/Как_продавать_кастомную_печать_без_переписки.md:76-106`
  identifies direct payment as the weakest part and says invoice/check/order ID
  and clear policy strengthen the handoff.

warrant:
Visible studio identity, order number, stable link, summary, next payment step,
and local payment context can reduce the feeling that the buyer is being thrown
into an unsafe private transfer.

qualifier:
MAVO does not currently solve this with checkout, escrow, guarantees, tracker,
studio vetting, sanctions, or quality arbitration.

rebuttal:
If buyers still refuse direct studio payment after these mitigations, this is
not a small UX copy bug. `Бизнес_Анализ/Ставка_MAVO.md:56-63` treats direct
payment breakage after mitigations as a core-model conflict.

### 6. Old-flow alternative gaps

claim:
The corpus explains why the old flow is painful and what MAVO must beat, but it
does not yet prove that buyers and studios will stop falling back to the old
flow.

data-anchor:

- `Проблемы_покупателей.md:13-25` describes the chat-first current flow and why
  some buyers drop before payment.
- `01_Описание_бизнеса/01_Что_такое_МАВО/Продукт/Преимущества/Без_разговоров.md:12-22`
  says MAVO reduces re-explaining and chaos; it does not promise zero contact.
- `Бизнес_Анализ/Соседние_модели_рынка.md:87-101` says local studios already use
  WhatsApp/Instagram/direct payment, and MAVO must be faster/clearer than
  messenger; it can also lose to freelancer/Canva if it does not reduce time and
  risk.
- `Бизнес_Анализ/Соседние_модели_рынка.md:103-109` says mass-market is the
  competitor by desire: if the catalog is not more interesting, the short path
  alone loses.
- `Бизнес_Анализ/Проверка_пилота.md:114-119` explicitly says the pilot must test
  whether the catalog path beats chat and does not break on direct payment.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:57-68` includes return
  to WhatsApp/prepress and typical clarifications closed as measurement points.

warrant:
MAVO's advantage over the old flow is speed, clarity, configured request, and
file readiness, not total absence of studio communication.

qualifier:
This remains a pilot question.

rebuttal:
The strongest unresolved alternative gap is not "does the corpus mention the
old flow"; it does. The gap is whether existing trust in a known studio plus
Kaspi/direct transfer/free substitutes beats MAVO's structured route.
`Бизнес_Анализ/Ставка_MAVO.md:72-76` explicitly lists Kaspi/free-substitute
pressure as not written/proven enough.

### 7. Reality check after launch

claim:
The corpus has a concrete reality-check plan for whether the chain actually
works after launch.

data-anchor:

- `Бизнес_Анализ/Проверка_пилота.md:16-25` says the first proof is buyer submit,
  lack of fear around outside payment, studio accept/decline without manual
  rescue, money, studio traffic, trust, and linking layer.
- `Проверка_пилота.md:45-58` gives go/no-go sample conditions: 30 active days,
  3-5 vitrines, 2+ studios sharing, measurable funnel, 20+ submitted or 3+
  accepted, and economics sample.
- `Проверка_пилота.md:87-99` says demand proof appears only when the whole path
  is visible: open vitrine, setup, submitted request, studio decision, paid
  `Принять`, and downstream payment signal.
- `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-30` defines the first
  accepted request with paid position and separates service-fee boundary from
  downstream `Оплачено`.
- `01_Описание_бизнеса/04_Как_запускаем/Стратегия_запуска.md:17-45` orders the
  first build around vitrine -> structured request -> `Принять` -> kits ->
  service fee, without checkout/ERP.
- `01_Описание_бизнеса/04_Как_запускаем/Сбор_аналитики.md:32-68` defines demand,
  request, money, product, and manual-friction metrics.

warrant:
The corpus knows which observable events would validate or break the chain:
exposure, product view, personalization, submit, accept/decline, file opening,
paid MAVO line, downstream studio payment, return to WhatsApp, and manual
prepress.

qualifier:
`Сбор_аналитики.md:74-76` and `Бизнес_Анализ/Экономика_каналов.md:27-45` keep
thresholds as hypotheses until enough sample exists.

rebuttal:
The current corpus contains a test plan, not observed demand data.

## Missing links and weak joints

1. Buyer payment trust is specified as a boundary and mitigation set, not proven.
   The corpus names order ID, stable link, visible studio, payment context, and
   policy language, but does not yet contain live evidence that buyers will pay
   the studio directly after submitting through MAVO.

2. The bridge from buyer submit to paid `Принять` depends on studio behavior.
   The buyer can reach a request; paid `Принять` requires the studio to believe
   the packet is valuable enough to accept and pay for. This is designed in the
   mechanics but explicitly a pilot hypothesis.

3. The current model intentionally excludes the most obvious trust hardeners:
   MAVO checkout, escrow, production tracker, quality arbitration, studio vetting,
   sanctions, and fraud supervision. That keeps scope coherent but leaves a real
   buyer-confidence gap.

4. Invoice/check/reprint/refund policy is mentioned as trust support, especially
   in buyer psychology and external notes, but it is not yet a fully owned
   current product/legal spec. The legal owners keep responsibility with the
   studio.

5. Old-flow displacement remains unproven. The corpus defines why WhatsApp is
   painful and what to measure, but it does not prove studios will avoid asking
   the buyer to re-explain in WhatsApp or that buyers will prefer MAVO over a
   familiar direct chat with an already trusted studio.

6. The appeal of the catalog itself is still an assumption. If SKU/design taste
   is weak, the short path will not overcome mass-market alternatives or Canva.

## Payment / trust boundary gaps

- Direct payment is the core yellow gap. Owner files consistently say buyer
  pays studio and MAVO is not cashier, but buyer-facing trust depends on studio
  identity, stable request link, order number, payment instructions, and policy
  clarity.
- `Оплачено` is deliberately not a MAVO file gate. This is internally coherent,
  but it means the buyer's strongest payment concern is outside MAVO's direct
  control.
- Studio-as-seller boundaries are clear, but buyer-facing copy and UI must avoid
  accidentally implying MAVO warranty, delivery, refund, or quality guarantee.
- If direct payment breaks after mitigations, the corpus itself says this
  threatens the model rather than requiring only local UX polish.

## Old-flow alternative gaps

- WhatsApp/direct studio flow: pain is clear; displacement is unproven.
- Kaspi/free substitutes: listed as pressure in `Ставка_MAVO.md:72-76`; not
  resolved.
- Canva/freelancer: MAVO must be faster/less risky; not proven.
- Mass-market: MAVO must offer a more interesting personal result; not proven.
- Studio bypass: after file opening the studio can continue outside MAVO; this
  is an accepted risk in `_context-base/CTX-013_Принять_открывает_файл.md:39-41`.

## Reality gap

Current reality is a designed chain plus measurement plan, not validated demand.
The strongest owner evidence for this is:

- `Бизнес_Анализ/Ставка_MAVO.md:46-54`: core chain links are hypotheses.
- `Ставка_MAVO.md:64-82`: no funnel run, no print-ready proof, no taste signal,
  no pipeline, no pilot proof, Kaspi/free substitutes pressure; 2026-07-02
  verdict says the idea is live but not proven.
- `Бизнес_Анализ/Проверка_пилота.md:87-112`: full proof requires visible path
  through submitted request, studio decision, paid `Принять`, downstream payment
  signal, and unresolved questions about paid kit value and return to WhatsApp.
- `Бизнес_Анализ/Экономика_каналов.md:27-45`: thresholds are hypotheses until
  submitted/accepted/willingness-to-pay/downstream data exists.

## Final judgment

CUSTOMER-01 should pass as yellow.

The corpus is strong enough to audit and implement against: it has owner-backed
claims, falsifiable mechanisms, route boundaries, payment/file invariants,
status distinctions, and pilot metrics. It is not strong enough to claim that
customer demand is proven. The correct current reading is: "the designed chain
is traceable and internally consistent; the buyer-to-paid-`Принять` causal proof
is intentionally deferred to pilot data."
