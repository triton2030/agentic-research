---
description: "Case definition for auditing the MAVO short corpus through the prose-audit lab."
depends-on:
  - "[[experiments/prose-audit-lab/docs/METHOD|Method]]"
  - "[[experiments/prose-audit-lab/docs/RUN-CONTRACT|Run Contract]]"
---

# Case: mavo-short

## Target

`/Users/triton/Documents/mavo-short/`

## Why This Case Is Useful

MAVO is a good stress test for `prose-audit` because it has:

- a large owner-authored corpus;
- current/future boundaries;
- business claims that cannot be unit-tested into truth;
- measurable but not-yet-observed reality gates;
- high risk of self-referential coherence.

## Inputs

- [intent.draft.md](inputs/intent.draft.md)
- [criteria.draft.md](inputs/criteria.draft.md)
- [corpus.md](inputs/corpus.md)

These are still draft inputs. A run may proceed as a method test, but decision
closure must carry `needs-owner-approval` until the owner approves or replaces
them.

## Suites

| Suite | Status | Purpose |
| --- | --- | --- |
| `v0-baseline` | archived | first failed/simple traceability audit |
| `v1-general` | active | corrected two-axis audit with validity/refutation/source-strength gates |

## Runs

| Run | Status |
| --- | --- |
| `runs/mavo-short/2026-07-07-v0-baseline` | archived negative control |
| `runs/mavo-short/2026-07-07-v1-refutation` | corrected rerun completed with warnings |
