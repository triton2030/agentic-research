---
description: "Single-run preservation and transfer evidence for the compact 1skill-architect rewrite."
---

# Evaluation — 2026-08-08

## Contract

Old baseline: `three-reference-2026-08-07/`. New candidate: shared portable
owner. Each cell used one isolated default Codex subagent and a bare task after
the package path; routing cells received only the task. Resolved model/settings
were not exposed to the parent: `unknown`. Therefore these runs show possible
behavior/preservation, not probability uplift or full target-set coverage.

## Observations

| Stream | Runs | Observed output | Status |
|---|---:|---|---|
| `baseline_cognitive` / `new_cognitive` | 1+1 | Both replaced “думай системно” with owner/change-path/probe gates; new also tested admission and three evidence lanes. | preserved |
| `baseline_migration` / `new_migration` | 1+1 | Both chose ordered backup/restore-proof/dry-run gates and deterministic script/CI enforcement. | preserved |
| `baseline_handbook` / `new_handbook` | 1+1 | Both kept the handbook external and required task-local veto evidence; baseline named the applicability-index gap more sharply. | preserved, gap noted |
| `routing_should` | 1 | Refused a duplicate skill because the live instruction already owned outcome-vs-lint; returned the cheaper owner rule. | should-trigger passed |
| `routing_near_miss` | 1 | Returned only the requested spelling correction; no meta-design ceremony. | near-miss passed |
| `transfer_tone` | 1 | Produced a narrow outcome-controller, observable send gate and comparator without copying the architecture example. | transfer possible |
| `transfer_design_system` | 1 | Produced a knowledge/tool hybrid, kept docs as owner and routed prop checks to a validator. | transfer possible |

## Verdict

No observed branch regressed after compression or the repaired thought
demonstration. This is not matched resampling: uplift for GPT-5.6, Opus 5 and
Fable 5 remains `unknown`. Reopen with repeated same-task runs on resolved
models/settings before claiming a probability shift.
