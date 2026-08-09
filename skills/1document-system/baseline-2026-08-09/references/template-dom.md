# DOM — Semantic Domain Model and Data Dictionary

**Purpose:** владеть meaning, relationships, identifiers и field semantics без
фиксации physical database design. **Default authority:** `canon`. Alias: DATA.
Near-miss: DDL/storage schema → EDD; wire contract → API; lifecycle → SEM;
vocabulary-only work → `1domain-modeling`.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Domain Boundary | OWNER | Included subdomain, exclusions, integration edges |
| Terminology | REFERENCE | Canonical vocabulary and forbidden synonyms |
| Entity Map | OWNER | Entities/value objects and responsibility |
| Entity Definitions | OWNER | Identity, existence criteria, meaning |
| Relationships | OWNER | Direction, cardinality, ownership, temporality |
| Identifiers | OWNER | Keys, uniqueness scope, external/internal distinction |
| Field Dictionary | OWNER | Meaning, semantic type, requiredness, source, mutability, examples |
| Integrity Constraints | OWNER | Data invariants; BRC links for policy conditions |
| Lifecycle Mapping | LOCAL | SEM owner links → entity/field effects |
| Source of Record and Stewardship | OWNER | Creator, updater, correction path |
| Sensitivity and Retention | LOCAL | Policy/legal owner links → domain-specific sensitivity/retention consequence |
| Canonical Examples | OWNER | Valid, boundary, invalid examples |
| Physical-model Boundary | OWNER | What remains engineering-owned |
| Interface and Integration Owners | REFERENCE | API/event/imported schema links |

## Conditional Modules

Context map; event payload dictionary; localization; units/currency; temporal
data; audit/version fields; external identifiers.

## Completion Check

Entities/fields have one meaning and source; relationships state
direction/cardinality; storage, payloads, rules и transitions не дублируются.

