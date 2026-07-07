---
description: "Domain-neutral lab for auditing prose when there is no single red/green oracle."
depends-on: []
---

# Prose Audit Lab

`prose-audit` checks prose-driven decisions when normal tests cannot say
"correct" or "incorrect": films, decks, landing pages, design concepts,
business models, specs, narratives, grant texts, investor memos, prompts.

The output is not "truth". The output is a traceable decision audit:

- what claim is being tested;
- which artifact says it;
- what kind of evidence supports it;
- what would refute it;
- where the current text is coherent but still unproven.

## Why This Exists

Some artifacts have no stable expected output. A landing page may be internally
clear but still fail to sell. A film pitch may be coherent but emotionally dead.
A product strategy may be well written but grounded only in its own assumptions.

So this lab separates four things that are easy to blur:

| Layer | Question | Output |
| --- | --- | --- |
| `validity` | Is the audit question valid for this corpus? | `valid`, `invalid-test`, `needs-owner-approval` |
| `trace` | Can the claim be traced to concrete text, numbers, design elements, or sources? | anchor map and source ledger |
| `argument` | Does the traced material warrant the conclusion and survive refutation? | claim / warrant / rebuttal / defeater |
| `reality` | What outside observation would make the claim stronger or false? | next evidence, not simulated certainty |

## Folder Shape

```text
experiments/prose-audit-lab/
  docs/                 # method, research grounding, run contract
  schemas/              # verdicts, source-strength labels, ledger format
  templates/            # reusable case/run/report templates
  scripts/              # deterministic layer-1 checks
  cases/<case-id>/      # stable inputs for one project/artifact
  runs/<case-id>/<run>/ # every audit run is isolated and reproducible
```

`cases/` describes what is being audited. `runs/` records what happened in one
audit attempt. Never overwrite a run; create a new folder.

## Current Cases

| Case | Artifact | Status |
| --- | --- | --- |
| `mavo-short` | `/Users/triton/Documents/mavo-short/` | active case; v0 baseline archived; v1 refutation completed with warnings |

## Core Rule

Same-model agreement is not independence. A panel of five similar LLM runs may
be useful for stability, but it is not a reality oracle and not a heterogeneous
panel. Strong claims need either a different oracle type, a different model
family, primary evidence, or an explicit reality-debt label.

Start here:

- [Method](docs/METHOD.md)
- [Research Grounding](docs/RESEARCH.md)
- [Run Contract](docs/RUN-CONTRACT.md)
- [Artifact Anchor](schemas/artifact-anchor.md)
- [Case Contract](schemas/case-contract.md)
- [Source Strength](schemas/source-strength.md)
- [Verdicts](schemas/verdicts.md)
