---
test_id: PROFIT-01
agent: agent-2
role: independent Chain Auditor
target_corpus: /Users/triton/Documents/mavo-short/
verdict: green
confidence: medium-high
---

# PROFIT-01 raw audit

## Verdict

**Green for traceability.** The current corpus does contain a traceable chain for how MAVO earns money in the current SaaS-vitrine model, without relying on future marketplace / commission logic.

This is **not** a green verdict on the business being proven. The corpus itself marks the model as alive but not proven: the dangerous numbers are still hypotheses / assumptions / unmeasured gaps. That is acceptable for PROFIT-01 because the gaps are explicit, routed to owners, and tied to reality checks.

## Scope and tool state

- Primary current corpus used the harness scope: `README.md`, `AGENTS.md`, `_ops/GOAL.md`, `_context-base/*.md`, `Данные_снаружи/*.md`, `01_Описание_бизнеса/**/*.md`, `02_Веб_приложение/**/*.md`, `03_Создание_загрузка_дизайнов/**/*.md`, `Бизнес_Анализ/**/*.md` (`corpus.md:5-15`).
- `04_Доп_проекты/**/*.md` treated as secondary/context-only; future-only material was not promoted into the current verdict (`corpus.md:17-20`).
- `_workspace/`, `.ignore/`, runtime folders, etc. excluded from semantic verdicts (`corpus.md:22-32`).
- `md status /Users/triton/Documents/mavo-short --json`: `FRESH`, no pending chunks, `_workspace/*` excluded by path scope.
- Tool gap: one semantic query for future-boundary hit `index_busy` during parallel semantic work; after `md status` showed `FRESH` and no lock, the same query was repeated successfully. This did not affect final evidence because exact `rg` / direct reads covered the same boundary.

## Chain links

### 1. Current revenue source

- **Claim:** Current MAVO revenue is paid by the studio, not the buyer: the studio pays MAVO for opened print-ready kits on accepted positions at `Принять`.
- **Data / anchor:** `Что_такое_MAVO.md:38-50`; `_Фин_модель.md:10-23`; `_Путь_студии.md:10-15,64-66`.
- **Warrant:** The first business answer, money owner, and studio path all state the same flow: buyer pays studio for the physical product; studio pays MAVO for accepted positions / opened kits.
- **Qualifier:** Current canon / decision.
- **Rebuttal / defeater:** If studios do not pay after free openings despite real demand, the current wedge is dead (`Ставка_MAVO.md:56-62`). If the model needs MAVO to collect buyer money or commission to work, that conflicts with current canon (`_ops/GOAL.md:34-42`).

### 2. Amount / pricing corridor

- **Claim:** Current mechanism is a per-opened-design service fee, not subscription and not marketplace commission: `300 / 700 / 1500 ₸` by design complexity, charged per accepted position / opened kit.
- **Data / anchor:** `Сервисный_сбор.md:15-27,32-40,41-49`; `Экономика_заказа.md:9-21`; `CTX-022_Плата_по_позициям.md:20-38`.
- **Warrant:** The fee grid, trigger, multiplier rules, and per-position logic are all owned in the money owner and CTX compression. The docs explicitly distinguish item count, personalized positions, and repeated openings.
- **Qualifier:** Fee levels are canon; free openings / minimum top-up are working corridor or hypothesis (`Экономика_заказа.md:16-19`).
- **Rebuttal / defeater:** If fee levels do not cover VarOps + catalog amortization + disputes, volume accelerates losses (`Расчёт_прибыли.md:65-89`; `Ставка_MAVO.md:56-62`). If studios cannot understand or accept fixed fee levels, CTX-028 says the frame must be revisited (`CTX-028_Сбор_предоплата_цены_студии.md:35-42`).

### 3. Cost structure

- **Claim:** The corpus names the relevant cost buckets for one accepted position, one SKU, and one studio/channel: VarOps, catalog amortization, bad debt/disputes, fixed tooling/hosting, founder time, onboarding/support/CAC.
- **Data / anchor:** `Расчёт_прибыли.md:50-63`; `Расчёт_прибыли.md:91-98`; `Экономика_каналов.md:12-24,35-45`; `Сбор_аналитики.md:57-68`.
- **Warrant:** Profit owner decomposes direct contribution into V/A/B and monthly fixed costs; channel owner adds onboarding/support/acquisition and payback positions; analytics owner defines the product events needed to compute them.
- **Qualifier:** Mostly hypothesis / unmeasured. V, A, B are explicitly not quantified yet.
- **Rebuttal / defeater:** If hidden manual founder work, support, SKU production, or disputes eat the service fee, the apparent SaaS margin is false (`Расчёт_прибыли.md:74-89`; `Экономика_каналов.md:21-24`).

### 4. Unit or period economics

- **Claim:** The corpus provides a period-economics skeleton: revenue per studio = paid positions/month × weighted average fee; contribution subtracts V/A/B; break-even depends on contribution per studio.
- **Data / anchor:** `Расчёт_прибыли.md:33-48`; `Расчёт_прибыли.md:65-89`.
- **Warrant:** The file computes pessimism/base/optimism scenarios and a break-even illustration at an explicit `V+A+B <= 40%` assumption.
- **Qualifier:** Model / scenario, not proven forecast. Mix, paid positions/month, V/A/B share, and wedge size remain assumptions.
- **Rebuttal / defeater:** If `V+A+B <= 40%` is false, or if the real paid-position volume is much lower than scenario inputs, break-even collapses. The file names this as the survival test, not a solved fact (`Расчёт_прибыли.md:83-98`).

### 5. Sensitivity / kill conditions

- **Claim:** The corpus has explicit kill conditions: studios not paying after free openings, negative contribution, insufficient sample not being mistaken for market failure, and pessimistic unit table failing.
- **Data / anchor:** `Ставка_MAVO.md:56-63`; `Проверка_пилота.md:45-69`; `Проверка_пилота.md:87-112`.
- **Warrant:** `Ставка_MAVO` gives due-diligence kill criteria; `Проверка_пилота` separates go, pivot channel, pivot request quality, pivot economics, no-go current wedge, and insufficient sample.
- **Qualifier:** Current audit / hypothesis thresholds.
- **Rebuttal / defeater:** If sample is too small, the right verdict is `insufficient sample`, not no-go; if accepted requests exist but costs eat the fee, the model pivots economics rather than scaling.

### 6. Reality check

- **Claim:** Cheapest next validation is not a full marketplace or broad build; it is a pre-pilot / pilot evidence path: manual factory run, print-ready test with first studio, pessimistic unit table, then 20-30 accepted requests / paid `Принять` evidence.
- **Data / anchor:** `Ставка_MAVO.md:64-82`; `Расчёт_прибыли.md:91-98`; `Пилот.md:15-30,32-50`; `Бизнес_Анализ/Проверка_пилота.md:45-58,100-112`.
- **Warrant:** The proposed checks directly hit the weakest assumptions: cost per opening, cost per SKU, paid willingness after free openings, accepted/submitted conversion, and contribution.
- **Qualifier:** Recommended next proof / working corridor.
- **Rebuttal / defeater:** A pilot with only registrations or free openings is insufficient; it must include paid `Принять` after free openings or it does not validate monetization (`Ставка_MAVO.md:68-74`; `Пилот.md:17-30`).

## Future-smuggling / conflicts

No material future-commission smuggling found in the current profit chain.

- Current root boundary says the current model is SaaS-vitrine with paid `Принять`; general gallery, buyer choice of studios, marketplace/channel mechanics, and demand commission live in future, not current canon (`_ops/GOAL.md:14`).
- `01_Описание_бизнеса/AGENTS.md` routes "общий выбор студий, общий спрос и комиссия за приведённый спрос" to `04_Доп_проекты/Будущее/` (`01_Описание_бизнеса/AGENTS.md:26-34`).
- `03_Как_это_работает/AGENTS.md` forbids treating marketplace / platform channel / commission for demand as current mechanics (`01_Описание_бизнеса/03_Как_это_работает/AGENTS.md:31-36`).
- Future owner confirms `04_Доп_проекты/Будущее/` is future-only parking, not current canon or roadmap (`04_Доп_проекты/Будущее/AGENTS.md:13-24,39-47`).
- Post-MVP commission files explicitly say current vitrine money is studio-paid `Принять`; platform commission appears only if MAVO later brings demand through a future common gallery (`Деньги_и_комиссия.md:8-35`; `Post-MVP_общая_галерея.md:9-29,50-60`).
- Current UI files contain marketplace language only as boundary / UX appearance, not revenue logic: no marketplace, no common gallery, no studio comparison in first web slice (`Поведение_веб_продукта_L6.md:19-22,74-84`; `Главная.md:20-27,46-54`).

Minor wording risk: current docs use phrases like "маскировка под маркетплейс" for buyer-facing familiarity (`Главная.md:24-27`). In context this is not smuggling, because the same file and L6 behavior forbid common gallery / marketplace behavior. But phrase-level extraction could confuse a future agent if read without the boundary lines.

## Missing / weak links

These are not PROFIT-01 failures because they are named as unknowns, but they keep the business reality unproven:

1. **V/A/B not quantified:** one opening cost, cost per SKU, and dispute/bad-debt buffer are explicitly open (`Расчёт_прибыли.md:50-63,91-98`).
2. **Paid-position volume is assumed:** paid positions/month and mix levels are scenarios until pilot data (`Расчёт_прибыли.md:33-48`).
3. **Studio payback/support not quantified:** channel owner lists CAC, setup/support, and payback positions but does not yet provide numbers (`Экономика_каналов.md:35-45`).
4. **Studio margin pressure exists:** service fee may eat the studio margin, especially medium/expensive levels (`Выгода_студии_в_цифрах.md:21-23`; `Ставка_MAVO.md:72-75`).
5. **Cheapest experiment still requires manual work:** pre-pilot packet is cheap versus full web build, but not free: factory run, print-ready test, and pessimistic unit table must happen before confidence increases (`Ставка_MAVO.md:80-82`).

## Reality gap

The corpus is honest that MAVO's profit chain is **traceable but not validated**:

- The due-diligence verdict is "идея жива, не доказана" and identifies economics as an unmeasured weak area (`Ставка_MAVO.md:80-82`).
- Pilot proof requires willingness to pay after free openings, repeat `Принять`, contribution, cost per SKU, and support burden; registrations alone do not prove the model (`Проверка_пилота.md:45-58,100-112`; `Сбор_аналитики.md:17-30,44-60`).
- Therefore: documentation passes PROFIT-01 as a chain, but the actual business remains in hypothesis status until pre-pilot / pilot evidence exists.

## Exact evidence index

- Harness scope: `experiments/prose-audit-mavo-short/corpus.md:5-32`.
- Test standard: `experiments/prose-audit-mavo-short/suite/profit-chain.test.md:17-39`.
- Root current/future boundary: `README.md:14-28,43-47`; `_ops/GOAL.md:10-15,34-42,63-68,100-107`.
- Owner routing: `01_Описание_бизнеса/AGENTS.md:26-34,44-47`; `01_Описание_бизнеса/03_Как_это_работает/AGENTS.md:21-36`; `01_Описание_бизнеса/04_Как_запускаем/AGENTS.md:17-35`; `Бизнес_Анализ/AGENTS.md:13-35,37-54`.
- Revenue source: `01_Описание_бизнеса/01_Что_такое_МАВО/Что_такое_MAVO.md:38-50`; `01_Описание_бизнеса/03_Как_это_работает/_Фин_модель.md:10-23`; `01_Описание_бизнеса/03_Как_это_работает/_Путь_студии.md:10-15,64-66`.
- Pricing: `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Сервисный_сбор.md:15-61`; `01_Описание_бизнеса/03_Как_это_работает/Фин_модель/Экономика_заказа.md:9-27`; `_context-base/CTX-022_Плата_по_позициям.md:20-41`; `_context-base/CTX-028_Сбор_предоплата_цены_студии.md:22-42`.
- Costs/economics: `Бизнес_Анализ/Расчёт_прибыли.md:23-98`; `Бизнес_Анализ/Экономика_каналов.md:12-45`; `Бизнес_Анализ/Выгода_студии_в_цифрах.md:9-23`.
- Sensitivity/reality check: `Бизнес_Анализ/Ставка_MAVO.md:46-82`; `Бизнес_Анализ/Проверка_пилота.md:16-29,45-69,87-112`; `01_Описание_бизнеса/04_Как_запускаем/Пилот.md:15-50`.
- No future-smuggling evidence: `04_Доп_проекты/Будущее/AGENTS.md:13-47`; `04_Доп_проекты/Будущее/Этап-3/Post-MVP_общая_галерея/Деньги_и_комиссия.md:8-35`; `04_Доп_проекты/Будущее/Этап-3/Post-MVP_общая_галерея/Post-MVP_общая_галерея.md:9-29,50-60`; `02_Веб_приложение/Подготовка_к_разработке/Поведение_веб_продукта_L6.md:19-22,74-84`.
