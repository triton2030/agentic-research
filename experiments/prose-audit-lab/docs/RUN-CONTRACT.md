---
description: "Contract every prose-audit run must satisfy."
depends-on:
  - "[[experiments/prose-audit-lab/schemas/artifact-anchor|Artifact Anchor]]"
  - "[[experiments/prose-audit-lab/schemas/source-strength|Source Strength]]"
  - "[[experiments/prose-audit-lab/schemas/verdicts|Verdicts]]"
---

# Run Contract

Every run lives at:

```text
runs/<case-id>/<YYYY-MM-DD>-<slug>/
```

## Required Files

```text
run.md                  # what was run and why
suite/                  # copied test cards used for this run
raw/                    # unedited agent/tool outputs
evidence-ledger.tsv     # claim-to-source ledger
role-manifest.tsv       # which roles/tools actually ran
report.md               # synthesis, not raw transcript
checks/                 # deterministic check outputs
```

## Required Gates

| Gate | Fails As | Meaning |
| --- | --- | --- |
| owner/input approval absent | `needs-owner-approval` | run may proceed as draft, but cannot claim closure |
| test question contradicts corpus | `invalid-test` | no color verdict; repair suite first |
| local anchor missing | `missing-anchor` | deterministic failure |
| source strength absent | `bad-ledger` | cannot compare evidence |
| no challenger for important decision | `refutation-gap` | traceability only, not decision audit |
| no primary/reality evidence | `reality-open` | cannot claim market/viewer/user truth |

## Role Manifest

`role-manifest.tsv` records what actually ran:

```text
role_id	raw_file	status	independence_label	notes
trace-auditor	raw/md-scout.md	completed	role-heterogeneous	Markdown evidence scout
challenger	raw/business-critic.md	completed	role-heterogeneous	Business refutation
judge	report.md	completed	main-synthesis	Synthesis owner
```

Suite cards may declare `required_roles`. Deterministic checks must compare the
suite declarations with the manifest. A role written in a prompt but absent from
the manifest did not run.

## Aggregation Rule

Do not average verdicts.

Synthesis keeps:

- all raw verdicts;
- minority findings;
- disagreements;
- source strength by claim;
- residual risk.

If one agent finds an `invalid-test`, `missing-anchor`, or strong defeater, the
synthesis must discuss it even if all other agents converge.

## Independence Rule

Label evaluator independence explicitly:

| Label | Meaning |
| --- | --- |
| `same-model-sample` | repeated LLM runs with same model family |
| `role-heterogeneous` | different roles/tools, same model family |
| `model-heterogeneous` | different model families |
| `human-domain-review` | named human/domain expert |
| `primary-reality` | observed behavior or measured field data |

Same-model convergence may support stability. It cannot support independence.
