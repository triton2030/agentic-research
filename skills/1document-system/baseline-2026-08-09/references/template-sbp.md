# SBP — Service Blueprint

**Purpose:** показать один end-to-end service scenario через actor actions,
frontstage, backstage, support и recovery. **Default authority:** `canon`.
Near-miss: customer-emotion view → projection; one operation → PROC; screen flow
→ PRD UX module; global responsibilities → OPM.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Scenario, Actor, and Outcome | OWNER | One bounded scenario and completion condition |
| Trigger and Entry Context | OWNER | Initiating event, channel, starting state |
| Preconditions | OWNER | Scenario-entry actor, data, permissions, readiness |
| Phases | OWNER | Ordered stages with entry/exit criteria |
| Primary-actor Actions | OWNER | Observable actions per phase |
| Secondary-actor Actions | OWNER | Actions and obligations per phase |
| Frontstage | OWNER | Visible people/product behavior and evidence |
| Backstage | OWNER | Hidden coordination behind the promise |
| Support Systems and Processes | LOCAL | System/process owner links → phase-specific use |
| Data and Produced Artifacts | LOCAL | DOM/API owner links → scenario-phase reads/writes/evidence |
| Money and State Events | LOCAL | BRC/SEM/economics owner links → scenario-phase mapping |
| Responsibility Handoffs | LOCAL | OPM owner links → phase-specific sender, receiver, deliverable |
| Failure Modes and Recovery | OWNER | Detection, visible response, compensation/escalation |
| Phase Metrics and Service Outcome | OWNER | Scenario-specific quality, latency, completion signals |
| Post-service Boundary | OWNER | What continues elsewhere |

## Conditional Modules

Timing/SLA lane; physical evidence; channel variants; customer emotions;
capacity constraints; regulatory checkpoints.

## Completion Check

Каждая phase содержит actions, front/backstage, systems, data и responsibility;
money/state/procedure owners linked; happy path и material failures завершаются
явным outcome либо escalation.

