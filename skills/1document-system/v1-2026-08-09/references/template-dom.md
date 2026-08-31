# DOM — Semantic Domain Model and Data Dictionary

**Purpose:** own meaning, relationships, identifiers and field semantics without
fixing physical database design. **Default authority:** `canon`. Alias: DATA.
Near-miss: DDL/storage schema → EDD; wire contract → API; lifecycle → SEM;
vocabulary-only work → `1domain-modeling`.

**Ban:** DOM owns meaning, not storage, payloads, business rules or state
transitions. No DDL, no physical schema, no state machine.

**Non-obvious contracts:** Terminology = REFERENCE — canonical vocabulary and
forbidden synonyms. Lifecycle Mapping and Sensitivity/Retention = LOCAL: owner
links → domain-specific consequence only. Interface and Integration Owners =
REFERENCE. Integrity Constraints hold data invariants; policy conditions stay as
BRC links. Physical-model Boundary names explicitly what remains
engineering-owned.

**Conditional modules:** context map; event payload dictionary; localization;
units/currency; temporal data; audit/version fields; external identifiers.

**Completion check:** every entity and field has one meaning and one source of
record.
