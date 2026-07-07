---
description: "Corrected MAVO prose-audit rerun with validity, source-strength, and refutation gates."
depends-on:
  - ../../../docs/RUN-CONTRACT.md
  - ../../../cases/mavo-short/README.md
---

# Run: mavo-short / 2026-07-07-v1-refutation

## Input

- Case: `mavo-short`
- Target artifact: `/Users/triton/Documents/mavo-short/`
- Owner intent: `cases/mavo-short/inputs/intent.draft.md`
- Criteria: `cases/mavo-short/inputs/criteria.draft.md`
- Corpus: `cases/mavo-short/inputs/corpus.md`
- Suite version: copied from `cases/mavo-short/suites/v1-general/`

## Purpose

Rerun the MAVO audit after the v0 baseline exposed a method failure:
coherence/self-traceability was being treated as stronger evidence than it was.

This run tests the corrected architecture:

- validity gate before synthesis;
- source-strength ledger;
- explicit refutation;
- two-axis verdicts;
- no plain overall green/yellow/red;
- no silent repair of a bad test question.

## Independence Label

- Deterministic checks: `scripts/check_run.py` plus direct CLI verification.
- LLM roles: `md-scout`, `business-critic`, main-agent synthesis.
- Model-family heterogeneity: unavailable in this native run; label is
  `role-heterogeneous / same-family`.
- Human/domain review: none.
- Primary reality: none.

## Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| owner/input approval | `needs-owner-approval` | inputs are `.draft.md` |
| test validity | `pass-with-warning` | `MAVO-VALIDITY-00`; v1 corrected v0 actor-boundary error |
| anchors/source ledger | `pass-with-warnings` | `evidence-ledger.tsv`; weak decision-ground warnings are intentional |
| challenger present | `pass` | `raw/business-critic.md` |
| reality evidence | `reality-open` | no interviews, paid usage, or buyer/studio observations in this run |
| acceptance audit | `completed-after-fix` | `raw/auditor.md`; blockers resolved in `checks/auditor-resolution.md` |

## Raw Outputs

- `raw/md-scout.md`
- `raw/business-critic.md`
- `raw/architecture-critic.md`
- `raw/local-defender.md`
- `raw/auditor.md`

Subagent execution ids are recorded in `checks/subagent-execution.md`.

## Synthesis Rule

No voting. Any invalid-test, missing source-strength, minority defeater, or
decision-duel conflict is reported even if the traceability chain is coherent.
