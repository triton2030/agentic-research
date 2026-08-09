# ARCH — Architecture Description

**Purpose:** описать stable current boundaries, components, interactions,
quality mechanisms и operating topology. **Default authority:** `canon`.
Near-miss: one change design → EDD; one trade-off → DEC; interface contract →
API; recovery steps → PROC.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Scope and Concerns | OWNER | System/version, stakeholders, answered questions |
| Drivers and Constraints | LOCAL | Product/business/regulatory owner links → architecture-driving constraints |
| System Context | OWNER | Users, external systems, exchanges, assumptions |
| Boundaries and Trust Zones | OWNER | Ownership, process/network/data boundaries |
| Components and Responsibilities | OWNER | Capability and exclusions per component |
| Interactions and Data Flows | OWNER | Direction, protocol/pattern, sync/async |
| Runtime and Deployment Topology | OWNER | Units, environments, dependencies, placement |
| Data Architecture Mapping | LOCAL | DOM/source-of-record owner links → store/stream placement and access |
| Quality Mechanisms | OWNER | Performance, availability, consistency, scale mechanisms |
| Failure and Resilience Model | OWNER | Failure domains, isolation, recovery guarantees |
| Security and Privacy Mapping | LOCAL | Security/privacy owner links → trust-zone and control placement |
| Operations and Observability | OWNER | Health signals and operator boundaries |
| Architecture Decisions | REFERENCE | Accepted DEC/ADR links, no repeated rationale |
| Evolution Constraints and Risks | OWNER | Limits, seams, unsafe change paths |
| Architecture Verification | OWNER | Tests/reviews/evidence for claims |

## Conditional Modules

C4 views; threat model; multi-region/tenancy; capacity/cost; disaster recovery;
integration landscape.

## Completion Check

Components have distinct responsibilities; critical interactions have direction
and owner; quality claims map to mechanisms/verification; EDDs не становятся
скрытым current architecture.

