# SEM — State and Event Model

**Purpose:** single semantic owner of one entity/process lifecycle: states,
events, transitions, invalid moves. **Default authority:** `canon`. Alias:
STATE. Near-miss: UI display state → PRD UX module; tracking event → local
tracking plan; business condition → BRC; procedure workflow → PROC.

**Ban:** SEM owns lifecycle facts, not business rules, not UI, not procedures
and not the full technical event vocabulary with payloads. Derived flags and
aggregates are computed values, never competing states.

**Non-obvious contracts:** Guard Mapping = state-intrinsic predicates plus BRC
Rule IDs — no copied business rules. Side-effect Mapping, UI Presentation
Consequences, Analytics Mapping = LOCAL: downstream owner links →
transition-specific delta, no copied procedures or labels. Transition rows
carry guard ID and side-effect ID, not inline logic.

**Conditional modules:** parallel/substates; timeouts; retry/re-entry;
compensation; eventual consistency; manual override.

**Completion check:** every nonterminal state has an exit or wait reason;
transitions deterministic; rules, UI and analytics remain with their owners.
