---
name: screenshot-design
description: >
  Runs an evidence-backed artistic critique of UI screenshots: landing pages,
  dashboards, flows, competitor screens, and before/after comparisons.
  MANDATORY only when the screenshot is a UI artifact and the task is to
  judge visible design qualities such as layout, spacing, hierarchy,
  typography, color, density, composition, polish, or harmony. Do not
  trigger just because an attachment happens to be a screenshot. Use by
  default for requests like "analyze this UI", "audit this design", "check
  this screen layout", or "compare these product screens". Outputs only a
  compact visible protocol and concrete recommendations. Do NOT use for
  receipts, passports, IDs, invoices, scanned documents, chat logs, terminal
  captures, OCR/extraction, factual reading, proof/evidence review, code
  review, Figma editing, live-browser verification, or invisible states.
---

# Screenshot Design

Rigid, screenshot-first critique from the eye of an art director.
The skill must feel beauty, disharmony, rhythm, emptiness, and scene presence.
It earns that freedom by grounding the read in visible evidence first.
It is meant for cyclical reuse across iterations, not a one-shot opinion dump.

If the main evidence is a screenshot and the question is visual, do the full review. Do not jump straight from the image to a verdict.
Do not call a screen beautiful, harmonious, dead, flat, theatrical, or premium until the review has judged the whole frame, not just the local craft.
Do not dump the whole internal audit into chat. By default the printed answer is compact.
Do not trigger the skill for non-UI screenshots or for screenshots attached only as evidence, identity, paperwork, or factual context.

## When to use

- Static screenshot or multiple screenshots of a UI
- Screenshot-based design critique or visual verification
- Before/after screenshot comparison
- Competitor teardown from screenshots
- Repeated refinement passes on the same screen until visible mistakes are removed and the design feels clean, harmonious, and beautiful
- Requests about spacing, hierarchy, grouping, density, polish, readability, block logic, composition, balance, rhythm, beauty, or negative space on a screen

## When not to use

- Non-UI screenshots or document-like captures such as receipts, passports, IDs, invoices, forms, scans, chat logs, or terminal output
- Screenshots attached only for OCR, transcription, factual reading, compliance, identity, or evidence review
- Pure code or DOM/CSS review
- Figma editing or design-system authoring
- Live-browser verification
- Claims about hover, focus, animation, responsiveness, or other states not visible in the image
- Text-only requests with no screenshot attached

## Required input

- At least one UI screenshot
- Optional: product goal, audience, intended primary action, brand constraints
- If there are multiple screenshots, label them `Screen A`, `Screen B`, etc., and keep every ledger bullet tagged to the right screen

## Workflow

Load only the support files you need:
- before the ledger or critique: [references/output-contract.md](references/output-contract.md), [references/perception-limits.md](references/perception-limits.md)
- before sending the final answer: [references/failure-modes.md](references/failure-modes.md)
- comparison rules live inside `output-contract`; use them only when there are multiple screenshots

## Iteration model

This skill is for iterative design tightening.

Run it, fix the strongest visible problems, then run it again on the updated screenshot.
The goal is not to produce one clever critique.
The goal is to keep cycling until obvious visual mistakes are gone and the screen feels resolved, harmonious, and aesthetically convincing.

## What gets printed vs. what stays internal

Print:
- `Protocol Trace` — one compact visible line proving the skill was applied and showing step status
- `Protocol` — compact visible proof that the skill steps were actually executed
- `Recommendations` — only the strongest concrete changes

Stay internal and do not print unless the user explicitly asks:
- internal evidence ledger
- review progress checklist
- scene read notes
- axis-by-axis critique notes
- re-attention pass
- fresh-eye sweep
- uncertainty notes
- emotional freeform close
- scratch checks used to decide whether the printed answer is grounded

### 1. Evidence gate

Confirm the screenshot is legible enough to judge. Stop and ask for a better image if it is cropped, blurred, tiny, partial, or noisy. If code is also attached, ignore it until the visual pass is done — do not smuggle code assumptions into a visual review.

The printed answer must begin with `Protocol Trace`.

### 2. Internal audit

Internally inspect:
- scene — visual mass, empty space, eye path, felt balance;
- structure — grouping, hierarchy, rhythm;
- surface — typography, contrast, readability;
- color harmony — visible clashes, muddy combinations, inert palettes, or contradictions in temperature / accent logic.

Build the internal evidence ledger exactly to spec from [references/output-contract.md](references/output-contract.md).

### 3. Internal checks

Run the review progress checklist, re-attention pass, and fresh-eye sweep internally.

Do not print them in the answer unless the user explicitly asks to see the checking process.

### 4. Printed answer

Print only:
- `Protocol Trace`
- `Protocol`
- `Recommendations`

`Protocol` must visibly prove that the skill actually inspected:
- evidence gate;
- current state of the screen as a whole: broken | mixed | close | resolved;
- scene;
- structure;
- surface;
- color harmony;
- internal checks;
- comparison, if relevant;
- uncertainty, only if it materially limits the verdict.

Keep `Protocol` compact. It is proof, not an essay.
Lead with the dominant truth of the frame, not with checkbox energy.

`Recommendations` must include only the strongest 1-4 changes. If the colors are visibly ugly, disharmonious, or contradictory in their relationships, that must appear either as a protocol finding or as one of the recommendations, and as a recommendation when it materially hurts the screen.

## Done when

- The answer visibly begins with `Protocol Trace`, proving `screenshot-design` was applied in this chat
- `Protocol Trace` reports the state of evidence gate, audit, internal checks, comparison, and uncertainty as `ok`, `n/a`, `none`, or a compact count
- The printed answer contains only `Protocol Trace`, `Protocol`, and `Recommendations` unless the user explicitly asked for the internal working
- The internal evidence ledger meets the minimum composition even though it is not printed
- Every protocol item and recommendation traces to internal ledger bullets
- `Protocol` includes a compact whole-screen state signal: `broken`, `mixed`, `close`, or `resolved`
- The skill is usable in repeated cycles on the same design without changing format or lowering discipline
- Comparison mode is used when multiple screenshots are present
- Internal checks happened, but were not printed unless the user asked
- Visible ugliness / disharmony / color conflict is always checked, and surfaces in recommendations when it materially harms the design
- The final answer passes [references/failure-modes.md](references/failure-modes.md)

## References

- [references/output-contract.md](references/output-contract.md) — ledger format, minimum composition, recommendations, comparison mode, measurement policy, final report template
- [references/failure-modes.md](references/failure-modes.md) — red flags, forbidden shortcuts, and final self-check
- [references/perception-limits.md](references/perception-limits.md) — fragile reads and confidence rules for screenshot perception
