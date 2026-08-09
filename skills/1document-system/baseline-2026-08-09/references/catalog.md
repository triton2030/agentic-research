# Core Artifact Catalog

Используй catalog как selector, затем читай ровно один linked template. Local
registry и его codes выигрывают до отдельной принятой задачи смены. Если проект
имеет локальный section contract, catalog и templates не применяются к его
типам — читай entry типа в локальном контракте.

| Code | Standard type | Authority | Default home | Use for | Template |
| --- | --- | --- | --- | --- | --- |
| `DEC` | Decision Record | `decision` | `_ops/decisions/` | Одна принятая или рассматриваемая развилка | [DEC](template-dec.md) |
| `MRD` | Market Requirements Document | `canon` | `canon/<domain>/` | Стабильный market/ICP/problem synthesis | [MRD](template-mrd.md) |
| `OPM` | Operating Model and Responsibility Matrix | `canon` | `canon/<domain>/` | Actors, rights, promises, money/data flow | [OPM](template-opm.md) |
| `SBP` | Service Blueprint | `canon` | `canon/<domain>/` | Один сквозной service scenario | [SBP](template-sbp.md) |
| `PRD` | Product Requirements Document | `canon` | `canon/<domain>/` | What/why/outcomes/requirements продукта | [PRD](template-prd.md) |
| `BRC` | Business Rules Catalog | `canon` | `canon/<domain>/` | Точные reusable business rules | [BRC](template-brc.md) |
| `SEM` | State and Event Model | `canon` | `canon/<domain>/` | States, events, transitions, guards | [SEM](template-sem.md) |
| `DOM` | Semantic Domain Model and Data Dictionary | `canon` | `canon/<domain>/` | Смысл concepts/entities/fields | [DOM](template-dom.md) |
| `ARCH` | Architecture Description | `canon` | `canon/<domain>/` | Current software structure и quality properties | [ARCH](template-arch.md) |
| `EDD` | Engineering Design Document | `decision` | `_ops/design/` | Proposed implementation of material change | [EDD](template-edd.md) |
| `API` | API Specification | `canon` | `canon/<domain>/` | Machine-facing interaction contract | [API](template-api.md) |
| `RSP` | Research Protocol | `ops` | `_ops/research/` | Вопрос, method и quality gates до исследования | [RSP](template-rsp.md) |
| `RPT` | Research and Evidence Report | `evidence` | `canon/evidence/` | Evidence-backed answer без product decision | [RPT](template-rpt.md) |
| `EXP` | Experiment Record | `ops` / `evidence` | `_ops/experiments/` → `canon/evidence/` | Pre-registered test и learning | [EXP](template-exp.md) |
| `PROC` | Operational Procedure | `canon` | `canon/<domain>/` | Повторяемая operation, SOP или Runbook | [PROC](template-proc.md) |

## Reader, Multiplicity, Lifecycle Defaults

При отсутствии live local section contract core sections в template
обязательны; selected conditional modules становятся обязательными на текущем
scope. Локальный контракт целиком владеет обязательностью, modes и closure
rules. Общий file lifecycle: `draft` → `active` → `superseded` или `archived`.
Type-specific workflow хранится отдельно.

| Code | Primary reader | Multiplicity / scope default |
| --- | --- | --- |
| `DEC` | decider, implementer | один record на material decision |
| `MRD` | product/business strategy | один active synthesis на market scope |
| `OPM` | domain and operating owners | один active model на operating scope |
| `SBP` | service/product/ops owners | один blueprint на bounded scenario |
| `PRD` | product, delivery, QA | один active owner на capability scope |
| `BRC` | domain, engineering, QA | один active catalog на ruleset scope |
| `SEM` | product, engineering, data | один active model на lifecycle subject |
| `DOM` | domain, data, engineering | один active model на domain scope |
| `ARCH` | engineering, operations, security | один active description на system scope |
| `EDD` | reviewers, implementers, operators | один design на material change |
| `API` | consumers, implementers, QA | один active contract на interface/version |
| `RSP` | researcher and reviewer | один protocol на study instance |
| `RPT` | evidence consumer and researcher | один report на question/evidence window |
| `EXP` | experiment and decision owners | один record на experiment instance |
| `PROC` | operator and procedure owner | один active procedure на operation scope |

## Alias Routing

- `ADR`, `BDR` → `DEC` с architecture/business module. BDR profile —
  самодостаточная append-only история выбора: без Markdown/wikilinks, URL/path
  references и graph dependencies; отношения выражаются plain stable IDs.
- `RFC` → `EDD` в review-state; отдельные принятые rationale могут стать `DEC`.
- `OM` → `OPM`; `BR` → `BRC`; `STATE` → `SEM`; `DATA` → `DOM`.
- `EVD`, Evidence Report → `RPT`.
- `SOP`, Runbook → `PROC` с соответствующим module.
- UX Specification → PRD UX module, пока нет независимого design lifecycle.
- Task → `1planning`; Finding → `1findings`; Rule/Instruction →
  `1instruction-shaping`.

Reserved system type: filename code `DOCS` → metadata
`docs-system-map`. Он принадлежит `_ops/documentation/`, а не
domain catalog.

Home — default, не global taxonomy. Для `canon/<domain>/` domain выводится из
current owner/cohesion, а не из type. Unified `EXP` меняет authority/home после
conclusion; split profile оставляет Brief в ops, а Report — в evidence.

В filename нового проекта используй standard code/type. В существующем проекте
следуй local registry; не создавай рядом второй vocabulary. Его смена —
отдельный System Refactor.

## Out-Of-Catalog Gate

Допусти project-local type, только если он владеет самостоятельным изменяемым
ответом и имеет независимый lifecycle, reader, validation или owner. Различие
scope само по себе недостаточно. Иначе добавь conditional module к ближайшему
type либо создай свободную projection.
Не изменяй global catalog без отдельной просьбы пользователя.

