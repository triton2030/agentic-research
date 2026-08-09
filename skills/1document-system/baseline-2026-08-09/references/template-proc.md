# PROC — Operational Procedure

**Purpose:** сделать одну repeatable operation безопасно исполнимой и
проверяемой. **Default authority:** `canon`. Aliases: SOP, Runbook. Near-miss:
multi-actor service → SBP; normative policy → BRC; system design → EDD;
one-off task → `1planning`.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Purpose and Scope | OWNER | Operation, outcome, exclusions |
| Trigger | OWNER | Event/request/schedule that starts it |
| Preconditions | OWNER | Required state, approvals, readiness |
| Roles and Escalation Owner | REFERENCE | OPM roles and local accountable operator |
| Inputs and Tools | LOCAL | Artifact/system/access owner links → procedure-specific use |
| Safety and Access Constraints | LOCAL | Security/permission/rule owner links → procedure-specific hard gates |
| Procedure | OWNER | Numbered steps and expected observables |
| Decision Points | LOCAL | BRC/DEC owner links → procedure-local branch condition and next step |
| Quality Gates | OWNER | Checks, pass criteria, retained evidence |
| Stop and Escalation Conditions | OWNER | When not to continue and safe state |
| Exceptions and Recovery | OWNER | Known failures and recovery boundary |
| Outputs and Retained Records | OWNER | Deliverables, logs, storage/retention |
| Rollback, Restart, or Handoff | OWNER | Reversibility and ownership transfer |
| Operational Metrics and Review | OWNER | Quality/time/error signals and trigger |
| Change Control | OWNER | Procedure owner, validation, supersession |
| Dependencies | REFERENCE | Systems, rules, models, adjacent procedures |

## Conditional Modules

Runbook: signals, diagnostics, commands, rollback, incident comms. SOP: training,
approval, safety. Also maintenance window, automation fallback, dual approval.

## Completion Check

Actor can execute without guessing order/branch/pass criteria; stop, recovery,
outputs and evidence explicit; shared rules linked; one-off project management
not embedded.

