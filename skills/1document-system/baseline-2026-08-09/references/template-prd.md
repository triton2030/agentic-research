# PRD — Product Requirements Document

**Purpose:** определить bounded product capability, users/outcomes,
requirements и acceptance без выбора implementation. **Default authority:**
`canon`. Near-miss: market need → MRD; technical design → EDD; exact reusable
rule → BRC; shared lifecycle → SEM.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Context and Problem | REFERENCE | Concise problem plus MRD/evidence/DEC links |
| Goal and Outcomes | OWNER | User/business change, not output volume |
| Users and Jobs | REFERENCE | Applicable actors/JTBD; no copied personas |
| Scope | OWNER | Included capability and surfaces |
| Non-goals | OWNER | Plausible adjacent work excluded |
| Requirements | OWNER | Stable IDs; normative statement plus observable pass/fail in the same row; priority column only when it differentiates |
| Business Rules | LOCAL | BRC owner links/Rule IDs → capability-specific applicability and effect; no copied tables |
| Roles and Permissions | LOCAL | OPM owner links → capability-specific access delta |
| States and Events | LOCAL | SEM owner links → capability-specific lifecycle effects |
| Data Obligations | LOCAL | DOM/API owner links → capability-local reads/writes |
| Quality Constraints | OWNER | User-visible performance, reliability, privacy, a11y |
| Success Metrics | OWNER | Metric, baseline/target or unresolved, decision use |
| Dependencies and Risks | LOCAL | Dependency/risk owner links → capability-local impact |
| Handoff and Open Questions | OWNER | UX/engineering handoff; unresolved blockers |

## Conditional Modules

Use-case narrative only for an end-to-end flow that requirement rows cannot
express; UX flow/screens/states; content and accessibility; analytics
instrumentation; rollout/experiment; migration; localization.

## Completion Check

Requirements testable, outcome-linked и in-scope; каждое решение сформулировано
в файле один раз; shared rules/states/data referenced; failure/permission
states covered; implementation absent.

