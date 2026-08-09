# EDD — Engineering Design Document

**Purpose:** описать how для bounded material change: implementation,
migration, verification и operation. **Default authority:** `decision`; RFC —
review module. Near-miss: product what/why → PRD; stable topology → ARCH;
enduring trade-off → DEC; public contract → API.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Requirements and Acceptance Basis | REFERENCE | PRD IDs, rules, constraints |
| Design Goals | OWNER | Properties the design must achieve |
| Non-goals | OWNER | Plausible technical work excluded |
| Assumptions and Constraints | OWNER | Design-local facts and owner links |
| Proposed Design | OWNER | Coherent mechanism and major choices |
| Component Change Map | OWNER | Create/modify/remove responsibility changes owned by this design |
| Control and Data Flows | OWNER | Runtime order, concurrency, transactions |
| Interface Changes | LOCAL | API/event/schema owner links → proposed design-local delta |
| Data and State Changes | LOCAL | DOM/SEM owner links → proposed migration/state delta |
| Failure and Error Handling | OWNER | Faults, propagation, retries, idempotency, recovery |
| Security and Privacy Impact | LOCAL | Security/privacy owner links → design-local threat/data/control delta |
| Migration and Compatibility | OWNER | Coexistence, backfill, cutover, reversibility |
| Rollout and Rollback | OWNER | Stages, gates, flags, stop conditions |
| Observability | OWNER | Signals proving health and correctness |
| Verification Strategy | OWNER | Tests mapped to requirements/failures |
| Alternatives and Trade-offs | OWNER | Credible options and DEC candidates |
| Open Questions | OWNER | Blocker, owner, evidence needed |
| Permanent Owner Updates | LOCAL | ARCH/API/DOM/SEM/PROC owner links → exact post-implementation update |

## Conditional Modules

Capacity/cost; schema migration; cache/concurrency proof; RFC review/dissent;
deprecation plan.

## Completion Check

Requirements/failures map to design and tests; migration/rollback/observability
исполняемы; stable decisions/interfaces вынесены своим owners.

