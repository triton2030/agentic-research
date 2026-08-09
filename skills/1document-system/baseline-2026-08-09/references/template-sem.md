# SEM — State and Event Model

**Purpose:** быть единым semantic owner одного entity/process lifecycle:
states, events, transitions и invalid moves. **Default authority:** `canon`.
Alias: STATE. Near-miss: UI display state → PRD UX module; tracking event →
local tracking plan; business condition → BRC; procedure workflow → PROC.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Subject and Boundary | OWNER | Entity/process, start/end, exclusions |
| State Definitions | OWNER | Key, meaning, entry truth, allowed duration |
| Event Definitions | OWNER | Key, trigger, actor/source, payload reference |
| Initial and Terminal States | OWNER | Creation, success/failure/cancel terminals |
| Transition Table | OWNER | From, event, guard ID, to, side-effect ID, invalid reason |
| Guard Mapping | OWNER | State-intrinsic predicates and BRC owner links/Rule IDs; no copied business rules |
| Side-effect Mapping | LOCAL | Downstream owner links → transition-specific effect; no copied procedures |
| Forbidden Transitions | OWNER | Plausible invalid moves and response |
| Derived Flags and Aggregates | OWNER | Computed values, never competing states |
| History and Audit | OWNER | Actor/time/reason retention obligations |
| UI Presentation Consequences | LOCAL | PRD/projection owner links → constraints imposed by stable state keys; no copied labels/grouping |
| Analytics Mapping | LOCAL | Metric owner links → lifecycle-event consumer mapping |
| Compatibility and Versioning | OWNER | Stored-value migration and consumers |
| Dependencies | REFERENCE | BRC, DOM, API, PRD owners |

## Conditional Modules

Parallel/substates; timeouts; retry/re-entry; compensation; eventual
consistency; manual override.

## Completion Check

States reachable or justified; every nonterminal state has exit/wait reason;
transitions deterministic; rules/UI/analytics remain with their owners.

