# Core Artifact Catalog

Use the catalog as a selector, then read exactly one linked template. A local
registry and its codes win until a separately accepted change; if the project
has a local section contract, catalog and templates do not apply to its types.

| Code | Standard type | Authority | Default home | Use for | Template |
| --- | --- | --- | --- | --- | --- |
| `DEC` | Decision Record | `decision` | `_ops/decisions/` | One accepted or considered fork | [DEC](template-dec.md) |
| `MRD` | Market Requirements Document | `canon` | `canon/<domain>/` | Stable market/ICP/problem synthesis | [MRD](template-mrd.md) |
| `OPM` | Operating Model and Responsibility Matrix | `canon` | `canon/<domain>/` | Actors, rights, promises, money/data flow | [OPM](template-opm.md) |
| `SBP` | Service Blueprint | `canon` | `canon/<domain>/` | One end-to-end service scenario | [SBP](template-sbp.md) |
| `PRD` | Product Requirements Document | `canon` | `canon/<domain>/` | What/why/outcomes/requirements | [PRD](template-prd.md) |
| `BRC` | Business Rules Catalog | `canon` | `canon/<domain>/` | Exact reusable business rules | [BRC](template-brc.md) |
| `SEM` | State and Event Model | `canon` | `canon/<domain>/` | States, events, transitions, guards | [SEM](template-sem.md) |
| `DOM` | Semantic Domain Model and Data Dictionary | `canon` | `canon/<domain>/` | Meaning of concepts/entities/fields | [DOM](template-dom.md) |
| `ARCH` | Architecture Description | `canon` | `canon/<domain>/` | Current software structure and qualities | [ARCH](template-arch.md) |
| `EDD` | Engineering Design Document | `decision` | `_ops/design/` | Proposed implementation of a material change | [EDD](template-edd.md) |
| `API` | API Specification | `canon` | `canon/<domain>/` | Machine-facing interaction contract | [API](template-api.md) |
| `RSP` | Research Protocol | `ops` | `_ops/research/` | Question, method, quality gates before research | [RSP](template-rsp.md) |
| `RPT` | Research and Evidence Report | `evidence` | `canon/evidence/` | Evidence-backed answer without a product decision | [RPT](template-rpt.md) |
| `EXP` | Experiment Record | `ops`/`evidence` | `_ops/experiments/` → `canon/evidence/` | Pre-registered test and learning | [EXP](template-exp.md) |
| `PROC` | Operational Procedure | `canon` | `canon/<domain>/` | Repeatable operation, SOP or Runbook | [PROC](template-proc.md) |

Defaults: one active artifact per type + scope; file lifecycle `draft` →
`active` → `superseded`/`archived`; readers are the professional defaults of
each genre. Home is a default, not a taxonomy: `<domain>` comes from the
current owner, not from the type. In a new project use standard codes in
filenames; in an existing project follow the local registry — never grow a
second vocabulary beside it.

## Alias routing

- `ADR`, `BDR` → `DEC` with the matching module; the BDR profile is a
  self-contained append-only history — no Markdown/wikilinks, URLs, paths or
  graph dependencies; relations only as plain stable IDs.
- `RFC` → `EDD` in review state; accepted rationale may become `DEC`.
- `OM` → `OPM` · `BR` → `BRC` · `STATE` → `SEM` · `DATA` → `DOM` · `EVD` →
  `RPT` · `SOP`, Runbook → `PROC` · UX Specification → PRD UX module.
- Task → `1planning` · Finding → `1findings` · Rule/Instruction →
  `1instruction-shaping`.
- Reserved system type: filename code `DOCS` → `docs-system-map`, lives in
  `_ops/documentation/`, not in the domain catalog.

## Out-of-catalog gate

Admit a project-local type only when it owns an independent mutable answer and
has an independent seam: lifecycle, reader, validation or owner — scope alone
is not enough. Otherwise use a conditional module of an existing type or a
free projection. Never change the global catalog without an explicit user
request.
