---
description: "Case-level taxonomy for prose-audit so MAVO does not define the shape for every domain."
depends-on:
  - "[[experiments/prose-audit-lab/schemas/artifact-anchor|Artifact Anchor]]"
---

# Case Contract

Every case should name the audit shape before the first run.

## Required Case Fields

| Field | Meaning |
| --- | --- |
| `artifact_type` | What is being audited: `markdown_corpus`, `landing_page`, `film_pitch`, `deck`, `design`, `mixed`. |
| `decision_type` | What decision the audit informs: buy, fund, watch, trust, understand, adopt, continue, approve. |
| `artifact_anchor_adapter` | Which anchor types are valid for this case. |
| `oracle_types` | Deterministic, trace, challenger, reader, visual, primary reality, etc. |
| `owner_status` | `approved`, `draft`, `unknown`, or `external`. |
| `reality_test_type` | What real-world observation could close the claim. |

## Why This Exists

Without a case contract, every future audit will copy the MAVO pattern:
Markdown corpus, owner docs, line refs, business due diligence. That would make
the lab appear general while its real surface remains one-project-specific.
