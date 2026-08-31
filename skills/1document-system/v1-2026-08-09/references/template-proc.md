# PROC — Operational Procedure

**Purpose:** make one repeatable operation safely executable and verifiable.
**Default authority:** `canon`. Aliases: SOP, Runbook. Near-miss: multi-actor
service → SBP; normative policy → BRC; system design → EDD; one-off task →
`1planning`.

**Ban:** PROC owns the executable steps, not the policy behind them, not system
design, and not one-off project management.

**Non-obvious contracts:** Roles and Escalation Owner = REFERENCE — OPM roles
plus the local accountable operator. Inputs and Tools, Safety and Access
Constraints, Decision Points = LOCAL: owner links → procedure-local hard gate or
branch condition. Dependencies = REFERENCE. Stop and Escalation Conditions is
owned: when not to continue and what the safe state is.

**Conditional modules:** Runbook — signals, diagnostics, commands, rollback,
incident comms. SOP — training, approval, safety. Also maintenance window,
automation fallback, dual approval.

**Completion check:** the actor executes without guessing order, branch or pass
criteria.
