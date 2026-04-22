---
name: screenshot-design
description: Runs an evidence-based visual audit of UI screenshots — landing pages, dashboards, product flows, competitor interfaces, before/after comparisons. MANDATORY only when the screenshot is a UI artifact and the task is to judge visible design qualities such as layout, spacing, hierarchy, typography, color, density, composition, polish, or harmony. Do not trigger just because an attachment happens to be a screenshot. Use by default when the user asks to "analyze this UI", "visually review this interface", "audit this design", "check this screen layout", "compare these product screens", or "review the spacing, hierarchy, or block logic", and for Russian phrasings like "проверь дизайн этого экрана", "визуально проверь интерфейс", "оцени дизайн по скрину", "что не так в этом экране", "сравни эти экраны". Forces the calling model to prove it actually examined the screenshot by producing a Visual Evidence Ledger before any verdict, anchoring every conclusion to visible spacing, grouping, block logic, alignment, hierarchy, typography, color, density, or readability. Do NOT use for receipts, passports, IDs, invoices, scanned documents, chat logs, terminal captures, OCR/extraction, factual reading, proof/evidence review, code review, Figma editing, live-browser verification, accessibility compliance checks beyond visible symptoms, or claims about hover, focus, motion, responsive, or other states that are not visible in a static image.
---

# Screenshot Design

Rigid, screenshot-first visual review skill. Follow the workflow exactly — the discipline is the value.

If the main evidence is a screenshot and the question is visual, produce the full output. Do not shortcut to verdicts without the ledger — this is how screenshot reviews drift into generic praise.
Do not trigger the skill for non-UI screenshots or for screenshots attached only as evidence, identity, paperwork, or factual context.

## When to use

- Static screenshot or multiple screenshots of a UI
- Screenshot-based design critique or visual verification
- Before/after screenshot comparison
- Competitor teardown from screenshots
- Requests about spacing, hierarchy, grouping, density, polish, readability, or block logic on a screen

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

Copy this checklist into the response and tick items off as the review advances:

```
Review Progress:
- [ ] 1. Evidence gate
- [ ] 2. Literal read
- [ ] 3. Visual Evidence Ledger (validated against the minimum composition)
- [ ] 4. Diagnosis on four axes
- [ ] 5. Recommendations
- [ ] 6. Re-attention pass (re-read the screenshot against each recommendation)
- [ ] 7. Comparison mode (if multiple screenshots)
- [ ] 8. What I cannot conclude from this screenshot
```

Before the ledger, skim [references/perception-limits.md](references/perception-limits.md). Multimodal models make perception errors on ~30% of confident answers — most of that damage comes from fragile reads (counts, exact pixels, tiny text, hairline alignment, color codes) treated as facts. The `Perception:` tag on each ledger bullet exists to stop that leakage.

### 1. Evidence gate

Confirm the screenshot is legible enough to judge. Stop and ask for a better image if it is cropped, blurred, tiny, partial, or noisy. If code is also attached, ignore it until the visual pass is done — do not smuggle code assumptions into a visual review.

### 2. Literal read

State what is actually visible before judging any of it:
- screen type and purpose;
- main regions or blocks, in reading order;
- dominant visual element;
- obvious crowding, drift, asymmetry, or gaps.

Keep this factual. No adjectives about quality yet.

### 3. Visual Evidence Ledger

Produce a `Visual Evidence Ledger` of 6–12 bullets. Every bullet must contain four lines:
- `Location:` where on the screen
- `Visible fact:` what is literally true in the image
- `Read on the relationship:` what that visible fact implies for the user
- `Perception:` `high-confidence visible` or `low-confidence read` (counts, microcopy, hairline alignment, color guesses, inferred state — see [references/perception-limits.md](references/perception-limits.md))

Minimum composition — do not proceed to diagnosis until all four are satisfied:
- ≥ 2 bullets on spacing, grouping, or block boundaries;
- ≥ 2 bullets on hierarchy or eye path;
- ≥ 1 bullet on alignment or rhythm;
- ≥ 1 bullet on typography, color, or readability.

If the ledger does not meet the minimum, return to the screenshot and add bullets — do not write the diagnosis.

Prefer relative language ("~2× line-height", "about the same padding as the card to its left") over exact numbers. The model cannot measure in pixels reliably. Treat counts above ~7, microcopy, 1–2 px alignment, and color codes as fragile by default.

For the full contract, good/bad bullet examples, and the report template, read [references/output-contract.md](references/output-contract.md).

#### Quick example bullet

- `Location:` hero block.
  `Visible fact:` the primary CTA sits ~2× the line-height below the subcopy, while secondary links sit tight under it.
  `Read on the relationship:` the CTA reads as a separate island instead of the closing move of the hero message.
  `Perception:` high-confidence visible.

### 4. Diagnosis

Use the ledger to judge exactly four axes:
- block logic;
- spacing and alignment;
- hierarchy and emphasis;
- readability, typography, color.

Every conclusion must point back to specific ledger bullets. If a judgement cannot be traced to a ledger bullet, drop it or add the missing bullet first.

### 5. Recommendations

Turn only the strongest visual findings into fixes. Use this format for each issue:

`[Severity] Short issue name`
- `Location:` where it happens
- `Visual evidence:` the ledger bullet(s) this is based on
- `Why it matters:` effect on clarity, trust, scanability, or perceived quality
- `Better direction:` concrete visual change
- `Confidence:` high | medium | low

Severity: `Blocker` | `High` | `Medium` | `Polish`. Full severity definitions live in [references/output-contract.md](references/output-contract.md).

### 6. Re-attention pass

After the recommendations are drafted, read the screenshot one more time against each one. This exists because extended reasoning in multimodal models causes measurable attention drift — the perceptual description stays correct, but later claims drift away from the region of interest ("Deeper Thought, Weaker Aim", 2026).

For each recommendation:
- locate the region on the screenshot again;
- confirm the ledger bullet(s) it rests on actually say what the recommendation claims;
- delete or downgrade any recommendation whose visual anchor does not survive the second look;
- move any claim that turned out to rest on a low-confidence read into the uncertainty block.

### 7. Comparison mode

If there are multiple screenshots or a before/after pair:
- keep ledger bullets tagged by screen;
- identify what actually changed before judging whether it improved;
- never treat `different` as `better`;
- name which change improved clarity, which regressed, and which tradeoff is still unresolved.

### 8. Uncertainty block

End with a section titled `What I cannot conclude from this screenshot`. Call out specifically:
- hover, focus, or motion behavior;
- responsive behavior;
- hidden or secondary states;
- real accessibility compliance beyond obvious visual symptoms;
- exact spacing tokens, grid, or type scale;
- screenshot quality limits (cropped, low-res, compressed, noisy).

If confidence was reduced by image quality or missing context, say so directly.

## Done when

- The response follows the checklist above and every item is ticked
- The `Visual Evidence Ledger` meets the minimum composition and every bullet has `Location`, `Visible fact`, `Read on the relationship`
- Every diagnosis and recommendation traces to ledger bullets
- Comparison mode is used when multiple screenshots are present
- The `What I cannot conclude from this screenshot` section is present
- No red-flag phrases from [references/failure-modes.md](references/failure-modes.md) survived the draft

## References

- [references/output-contract.md](references/output-contract.md) — full ledger spec, recommendation format, comparison mode, final report template
- [references/failure-modes.md](references/failure-modes.md) — red flags, forbidden shortcuts, anti-bypass rules
- [references/perception-limits.md](references/perception-limits.md) — what multimodal models systematically get wrong on screenshots (counts, tiny text, hairline alignment, color codes) and how to mark fragile reads
