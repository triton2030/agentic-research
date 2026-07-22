---
description: "Classify expert findings by source support while preserving disagreement and alternatives."
---

# Synthesis And Evidence

Read after agents return when findings disagree, need verification or change
the owner decision.

## Classification

- **accepted** — direct/source-supported evidence proves the claim; a critic
  also supplies an alternative. The finding changes the decision.
- **rejected** — evidence is wrong, outside scope or contradicted by source.
- **deferred** — plausible and useful, but not needed for the current decision.
- **needs verification** — material claim lacks an address, source support or
  required coverage.
- **incomplete** — critic finding has no alternative. Ask the same expert for a
  better path/smaller probe/missing input, or retain it only as awareness.
- **invalid-test** — the brief/question asks about the wrong actor, status,
  claim or owner. Repair the test before trusting its verdict.

`incomplete` does not apply to `auditor` or `md-scout`, whose native contracts
are evidence-shaped.

## Evidence Bar

A path or citation is not support by itself. Verify that it says what the
finding claims. Distinguish:

- `direct_evidence` / `source_supported` — normally eligible for acceptance;
- `inference` / `suspicion` — verification needed when the decision depends on
  it;
- `unknown` / `tool_failure` / `self_report_only` — gap, not proof.

For `md-scout`, require addressable snippets, actual scope/exclusions, tool
coverage and explicit gaps. Retrieval rank and broad shell counts do not become
IA/canon verdicts.

## Steering Trace

When input was corrected, preserve initial verdict, intervention, revised or
unchanged verdict, supporting evidence and the main-context label (`steered
pass`, `repaired pass`, `retained consultation`). One stream does not become
several independent votes.

## Synthesis Rules

- Do not vote or average verdicts. Decide from evidence and the user's outcome.
- Preserve each native verdict and material disagreement. Divergence may expose
  an ambiguous brief, rubric or owner boundary.
- Do not silently filter or move raw agent output into canon.
- Group findings by source, verdict and severity; retain uncertainty labels.
- Aggregate alternatives into the decision set, but keep `md-scout` evidence
  separate from critic judgments.
- An honestly `satisfied` / `architecture_ok` result is complete; do not rerun
  the same lens without a new material reason.

## Handoff

- accepted current-scope finding → main owner applies and validates;
- acceptance gap → task owner / `1planning`;
- instruction or owner-shape gap → `1instruction-layer` / `1ia-audit`;
- graph obligations → `1md-graph`;
- genuine collateral problem → `1findings`;
- project goal/scope change → `1goal` after caller decision.
