---
name: screenshot-design
description: >
  Critique visible UI screenshots with evidence-backed artistic judgment.
  Use only when the image is a UI artifact and the user asks to judge
  visible design qualities: layout, spacing, hierarchy, typography,
  color, density, composition, polish, harmony, balance, or beauty.
  Trigger when the user asks "analyze this UI", "audit this design",
  "check this screen layout", "compare these product screens", "что не
  так с экраном", "проверь визуал", or gives before/after UI screenshots.
  Output in delayed-judgment order: what is noticed first, what starts to
  break, verdict, then fix-next changes. Do not trigger merely because a
  screenshot is attached. Do not trigger for receipts, passports, IDs,
  invoices, scanned documents, chat logs, terminal captures, OCR,
  factual reading, proof/evidence review, code review, Figma editing,
  live-browser verification, or invisible states.
---

# Screenshot Design

Rigid, screenshot-first critique from the eye of an interface designer who cares deeply about harmony, composition, alignment, visual weight, and semantic balance.
It earns that freedom by grounding the read in visible evidence first.
It is meant for cyclical reuse across iterations, not a one-shot opinion dump.

If the main evidence is a screenshot and the question is visual, do the full review. Do not jump straight from the image to a verdict.
Do not call a screen beautiful, harmonious, dead, flat, theatrical, or premium until the review has judged the whole frame, not just the local craft.
Do not dump the whole internal audit into chat. By default the printed answer is compact.
Do not trigger the skill for non-UI screenshots or for screenshots attached only as evidence, identity, paperwork, or factual context.

## Governing lens

Think like an interface designer with a strong bias for:
- harmony of the frame as a whole;
- composition before component praise;
- alignment, rhythm, and containment;
- visual weight and the distribution of emphasis;
- semantic balance, so the important things feel important and the secondary things stay secondary.

Judge the screen first as one visual field:
- where the weight sits;
- where the eye goes first, second, and then stalls;
- whether empty space works as counterweight or is just leftover canvas;
- whether blocks align into one rhythm or drift apart;
- whether the distribution of meaning feels intentional.

Frame-level harmony outranks local neatness.
Composition outranks component polish.
Semantic weight distribution outranks stylistic cleverness.

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

## Action bias

This skill is a diagnostic step, not the end of the task.
End the critique with fix-next changes that can be acted on immediately.
If the surrounding task is to improve the current UI rather than only discuss it, continue from the fix list into the next edit pass unless the user explicitly asked for critique only.

## Iteration model

This skill is for iterative design tightening.

Run it, fix the strongest visible problems, then run it again on the updated screenshot.
The goal is not to produce one clever critique.
The goal is to keep cycling until obvious visual mistakes are gone and the screen feels resolved, harmonious, and aesthetically convincing.

## What gets printed vs. what stays internal

Print:
- `What I Notice First` — the visible first pass in short conversational form
- `What Starts To Break` — the strongest tensions or failures before any verdict
- `Verdict` — one short synthesis at the end
- `Fix Next` — only the strongest concrete changes
- `Limits` — only if image quality or hidden states materially limit the read

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

### 2. Internal audit

Internally inspect in this order:
- frame — visual mass, negative space, felt balance, scene presence;
- eye path — first anchor, second anchor, stalls, overloaded zones, dead zones;
- grouping and rhythm — containment, spacing cadence, alignment, structural breaks;
- surface and color — typography, contrast, readability, palette harmony or conflict.

Build the internal evidence ledger exactly to spec from [references/output-contract.md](references/output-contract.md).
Hold the verdict back until the inspection is finished.

### 3. Internal checks

Run the review progress checklist, re-attention pass, and fresh-eye sweep internally.

Do not print them in the answer unless the user explicitly asks to see the checking process.

### 4. Printed answer

Print only:
- `What I Notice First`
- `What Starts To Break`
- `Verdict`
- `Fix Next`
- `Limits`, only if needed

The visible path should feel like a designer looking carefully, then thinking, then concluding.
It must not read like a checklist and it must not spill into a raw stream of consciousness.

`What I Notice First` comes first and stays close to the pixels:
- 2-4 short bullets or sentences;
- whole frame before local details;
- what the eye catches, where the weight sits, what the empty space is doing.

`What Starts To Break` comes next:
- 2-4 short bullets or sentences;
- the strongest harmony, alignment, rhythm, or semantic-balance failures;
- each point ties a visible cue to its effect on reading, emphasis, or felt composition;
- still no final verdict yet.

`Verdict` comes at the end of the reasoning path:
- one short paragraph;
- synthesize the screen as a whole;
- use `broken`, `mixed`, `close`, or `resolved` only if helpful;
- the verdict must be earned by the two sections above, not assumed at the start.

`Fix Next` must include only the strongest 1-3 changes:
- highest leverage first;
- composition and frame before local polish;
- concrete enough that the next edit pass can start immediately;
- if the colors are visibly ugly, disharmonious, or contradictory, that must surface here when it materially harms the screen.

`Limits` is optional. Use it only when crop, image quality, or hidden states materially limit the verdict.

## Done when

- The printed answer contains only `What I Notice First`, `What Starts To Break`, `Verdict`, `Fix Next`, and optional `Limits` unless the user explicitly asked for the internal working
- The internal evidence ledger meets the minimum composition even though it is not printed
- Every printed reason and fix traces to internal ledger bullets
- The answer reads like delayed judgment, not early anchoring
- The verdict comes after the visible examination, not before it
- The skill is usable in repeated cycles on the same design without changing format or lowering discipline
- Comparison mode is used when multiple screenshots are present
- Internal checks happened, but were not printed unless the user asked
- Visible ugliness / disharmony / color conflict is always checked, and surfaces in recommendations when it materially harms the design
- The final answer passes [references/failure-modes.md](references/failure-modes.md)

## References

- [references/output-contract.md](references/output-contract.md) — ledger format, minimum composition, recommendations, comparison mode, measurement policy, final report template
- [references/failure-modes.md](references/failure-modes.md) — red flags, forbidden shortcuts, and final self-check
- [references/perception-limits.md](references/perception-limits.md) — fragile reads and confidence rules for screenshot perception
