# PRD — Product Requirements Document

**Purpose:** define a bounded product capability, its users/outcomes,
requirements and acceptance without choosing implementation. **Default
authority:** `canon`. Near-miss: market need → MRD; technical design → EDD;
exact reusable rule → BRC; shared lifecycle → SEM.

**Ban:** PRD owns what and why, never how. Implementation is absent; shared
rules, states, permissions and data are referenced, never copied.

**Non-obvious contracts:** Context and Problem, Users and Jobs = REFERENCE, no
copied personas. Requirements carry stable IDs with the normative statement and
an observable pass/fail in the same row; priority column only when it
differentiates. Business Rules, Roles and Permissions, States and Events, Data
Obligations, Dependencies = LOCAL: owner links → capability-specific delta only,
no copied tables.

**Conditional modules:** use-case narrative only for an end-to-end flow that
requirement rows cannot express; UX flow/screens/states; content and
accessibility; analytics; rollout/experiment; migration; localization.

**Completion check:** each decision stated once in the file; failure and
permission states covered.
