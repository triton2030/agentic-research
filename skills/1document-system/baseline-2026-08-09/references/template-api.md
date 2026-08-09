# API — API Specification

**Purpose:** владеть consumer-visible testable interface contract across
implementations. **Default authority:** `canon`. OpenAPI/AsyncAPI/GraphQL
schema может быть normative для representable wire units или derived companion,
но не independently editable второй truth. Near-miss: domain meaning → DOM; internal change → EDD;
lifecycle/rules → SEM/BRC; tutorial → projection.

Machine spec доказывает только явно выраженный wire contract. Не выводи из HTTP
method, status codes или schemas purpose, committed effects, retry/idempotency,
compatibility или business behavior. Без owner evidence соответствующий
`OWNER` section получает `SECTION-STATUS`, а не conventional API semantics.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Consumers and Scope | OWNER | Intended callers, capability, excluded interfaces |
| Representation Authority | OWNER | Per interface/version and logical unit choose Markdown section or exact machine-spec component as normative; stable IDs, direction, drift gate |
| Protocol, Endpoint, and Version Model | OWNER | Transport, base address/topic, negotiation |
| Authentication and Authorization | LOCAL | Security/OPM owner links → interface-specific enforcement and credential boundary |
| Global Conventions | OWNER | Naming, time, IDs, encoding, correlation, nullability |
| Operations or Messages | OWNER | Stable ID and source-backed purpose/effects; method/topic lives only in selected normative representation, otherwise exact operation pointer |
| Request or Input Schemas | OWNER | Full wire shape only when Markdown is normative; otherwise explicit local mode override to REFERENCE + exact component links |
| Response or Output Schemas | OWNER | Full success wire shape only when Markdown is normative; otherwise explicit local mode override to REFERENCE + exact component links |
| Error Contract | OWNER | Source-backed semantic codes, conditions, retryability, safe behavior; wire status/schema follows Representation Authority |
| Idempotency and Concurrency | OWNER | Keys, duplicates, ordering, optimistic control |
| Collection Behavior | OWNER | Pagination, filtering, sorting, consistency |
| Limits and Quotas | OWNER | Sizes, rates, timeouts, enforcement signals |
| Security and Privacy Impact | LOCAL | Security/privacy owner links → exposed data/operations and interface-specific controls |
| Conformance Examples | OWNER | Nonnormative cases derived from confirmed operation/schema IDs; unsupported semantics stay unresolved |
| Compatibility and Deprecation | OWNER | Source-backed breaking-change rule and migration signal |
| Observability Contract | OWNER | Correlation/audit fields and diagnostics |
| Conformance and Companion Spec | REFERENCE | Exact normative/derived spec and version links plus validation route; no duplicate schema |
| Semantic Dependencies | REFERENCE | DOM, SEM, BRC, DEC, security owners |

## Conditional Modules

Webhooks/events; streaming; batch/file transfer; callbacks/signing; SDK;
multi-tenancy.

## Completion Check

Operations define auth, input, output, errors, effects и retry/idempotency; each
wire contract has one normative representation and explicit generation/
validation direction; semantic OWNER sections are source-backed or carry
`SECTION-STATUS`; examples are nonnormative; machine validation не доказывает
purpose/effects/retry/compatibility.

