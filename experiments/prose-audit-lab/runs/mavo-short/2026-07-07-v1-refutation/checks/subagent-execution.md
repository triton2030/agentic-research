---
description: "Subagent execution evidence for the MAVO v1 prose-audit run."
depends-on:
  - ../role-manifest.tsv
---

# Subagent Execution Evidence

This file records the native subagents used in the run. It is an execution
ledger, not a substitute for raw outputs.

| Role | Agent ID | Status | Raw File |
| --- | --- | --- | --- |
| `md-scout` | `019f3c1d-6e13-7670-ba1a-bcba8d806bd1` | completed | `raw/md-scout.md` |
| `business-critic` | `019f3c1d-7a69-7802-847e-01efa879170e` | completed | `raw/business-critic.md` |
| `architecture-critic` | `019f3c1d-8625-7831-b406-50c0bc784e26` | completed | `raw/architecture-critic.md` |
| `auditor` | `019f3c26-c1ac-73e0-8fe8-28c8c9502825` | completed | `raw/auditor.md` |

Main-thread synthesis is recorded in `report.md` and is not independent.

The auditor initially failed the run because this execution evidence and final
metadata synchronization were missing. Those fixes are tracked in
`checks/auditor-resolution.md`.
