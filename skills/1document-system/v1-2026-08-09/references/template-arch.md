# ARCH — Architecture Description

**Purpose:** describe stable current boundaries, components, interactions,
quality mechanisms and operating topology. **Default authority:** `canon`.
Near-miss: one change design → EDD; one trade-off → DEC; interface contract →
API; recovery steps → PROC.

**Ban:** ARCH owns the current stable shape, not proposed changes, not decision
rationale, not interface or procedure detail. An EDD must never become the
hidden current architecture.

**Non-obvious contracts:** Drivers and Constraints, Data Architecture Mapping,
Security and Privacy Mapping = LOCAL — owner links → architecture-driving
consequence only. Architecture Decisions = REFERENCE: accepted DEC/ADR links,
rationale never repeated. Evolution Constraints and Risks owns seams and unsafe
change paths.

**Conditional modules:** C4 views; threat model; multi-region/tenancy;
capacity/cost; disaster recovery; integration landscape.

**Completion check:** every quality claim maps to a named mechanism and to
verification evidence.
