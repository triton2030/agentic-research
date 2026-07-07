---
description: "Resolution of auditor blockers for the MAVO v1 prose-audit run."
depends-on:
  - ../raw/auditor.md
  - subagent-execution.md
---

# Auditor Resolution

## RUN-VALIDATOR-FAIL

Resolution:

- `raw/auditor.md` was saved.
- `role-manifest.tsv` was updated to mark `auditor` as `completed`.
- `check_run.py` was rerun after metadata synchronization.

## RUN-STATE-STALE

Resolution:

- Root `README.md` and case `README.md` status were updated from in-progress to
  completed-with-warnings.
- `run.md` gates and raw-output list were synchronized with the actual report
  and raw files.

## SUBAGENT-EVIDENCE

Resolution:

- `checks/subagent-execution.md` records native subagent ids, roles, completion
  status, and raw files.

## Still Intentional Warnings

The deterministic checker still warns that some `decision_ground` rows use
`self_canon`. This is not a failure to fix; it is the central audit result:
MAVO's business decisions are traceable in canon but not supported by primary
reality evidence yet.
