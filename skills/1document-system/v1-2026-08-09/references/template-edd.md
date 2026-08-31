# EDD — Engineering Design Document

**Purpose:** describe the how for one bounded material change: implementation,
migration, verification, operation. **Default authority:** `decision`; RFC is a
review module. Near-miss: product what/why → PRD; stable topology → ARCH;
enduring trade-off → DEC; public contract → API.

**Ban:** EDD owns one change, not the standing truth. Stable decisions,
interfaces and topology leave for their owners; the EDD must not become the
de-facto current architecture.

**Non-obvious contracts:** Requirements and Acceptance Basis = REFERENCE (PRD
IDs, rules, constraints). Interface Changes, Data and State Changes, Security
and Privacy Impact = LOCAL: owner links → the proposed design-local delta only.
Permanent Owner Updates = LOCAL: ARCH/API/DOM/SEM/PROC owner links → the exact
post-implementation update. Component Change Map covers only responsibility
changes this design owns.

**Conditional modules:** capacity/cost; schema migration; cache/concurrency
proof; RFC review/dissent; deprecation plan.

**Completion check:** migration, rollback and observability are executable, not
aspirational.
