---
description: "Archived baseline MAVO prose-audit run that exposed flaws in the first harness."
depends-on: []
---

# Archived Baseline: 2026-07-07-v0

This folder preserves the first MAVO run. It is useful as a negative control.

Do not treat its report as the current method. Known defects:

- the lab folder used to be MAVO-specific;
- suite used `runs: 3`, not the stronger `×5` baseline once discussed;
- no deterministic source-strength ledger;
- no separate challenger/judge;
- `CUSTOMER-01` used a bad actor boundary around paid `Принять`;
- `PROFIT-01` failed to promote Kaspi/substitute pressure into the synthesis;
- a single color hid two axes: chain completeness and evidence strength.

The raw outputs are intentionally preserved. Some paths inside the old report
refer to the previous folder name, `prose-audit-mavo-short`.
