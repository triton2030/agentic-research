# Output Contract

Exact response shape for a screenshot review. Read when composing the ledger, the recommendations, or the final report.

## Contents

- Visual Evidence Ledger — format, composition, perception tags, examples
- Recommendation format — structure, severity, examples
- Comparison mode
- Uncertainty block
- Final report template
- Measurement policy — what can and cannot be stated exactly

## Visual Evidence Ledger

Produce 6–12 bullets. Each bullet is four labeled lines:

- `Location:` where on the screen this is happening
- `Visible fact:` what is literally true in the image
- `Read on the relationship:` what that visible fact implies for the user
- `Perception:` `high-confidence visible` (directly readable from pixels) or `low-confidence read` (counts above ~7, microcopy, 1–2 px alignment, color codes, inferred state). See [perception-limits.md](perception-limits.md).

Minimum composition (do not skip ahead to diagnosis until all four are satisfied):

- ≥ 2 bullets on spacing, proximity, grouping, or block boundaries
- ≥ 2 bullets on hierarchy, eye path, emphasis, or contrast
- ≥ 1 bullet on alignment, containment, or rhythm
- ≥ 1 bullet on typography, color, or readability

### Good bullets

- `Location:` hero.
  `Visible fact:` headline and subcopy sit close enough to read as one unit, but the primary CTA is pushed ~2× line-height below.
  `Read on the relationship:` the CTA reads as a separate island rather than the closing move of the hero message.
  `Perception:` high-confidence visible.

- `Location:` left sidebar.
  `Visible fact:` icon labels align cleanly, but the active item is signaled mostly through fill color, not weight or shape.
  `Read on the relationship:` the active-state signal is visually thin and easy to miss on a quick scan.
  `Perception:` high-confidence visible.

- `Location:` pricing row.
  `Visible fact:` the three plan cards share the same container width, but the middle card appears to have slightly more vertical padding and a marginally darker border.
  `Read on the relationship:` the middle plan reads as the emphasised "recommended" option even though no label says so.
  `Perception:` low-confidence read — the padding and border-weight differences are close to the limit of what can be judged from the image.

- `Location:` table header.
  `Visible fact:` column labels are the same weight and size as cell values.
  `Read on the relationship:` header and body blur into one texture, so the row-scan anchor disappears.
  `Perception:` high-confidence visible.

### Weak bullets (do not use)

- "Spacing feels off."
- "The hierarchy is weak."
- "This looks clean and modern."
- "I checked the alignment."
- "Feels more premium now."

The failure mode behind weak bullets is always the same: a verdict with no visible anchor. Replace with one of the three-line bullets above.

## Recommendation format

Use this format for each issue:

`[Severity] Short issue name`
- `Location:` where it happens
- `Visual evidence:` the ledger bullet(s) this is based on
- `Why it matters:` effect on clarity, trust, scanability, or perceived quality
- `Better direction:` concrete visual change
- `Confidence:` high | medium | low

### Severity levels

- `Blocker` — breaks comprehension of the screen or the primary action
- `High` — materially weakens the screen or pushes users toward the wrong action
- `Medium` — noticeable degradation, survivable
- `Polish` — refinement, not structural

### Good recommendation

`[High] CTA detached from hero message`
- `Location:` hero
- `Visual evidence:` ledger bullet 1 — CTA sits ~2× line-height below subcopy
- `Why it matters:` the CTA is the closing move of the hero message; when it floats away from the copy, scanning users do not connect offer and action
- `Better direction:` reduce the gap between subcopy and CTA to roughly one line-height, keeping the CTA inside the visual group of the message
- `Confidence:` high

### Weak recommendation (do not write)

"The CTA could be closer to the subcopy to feel more connected."
- No location, no evidence, no severity, no confidence. Reader cannot act or verify.

## Comparison mode

If the review covers multiple screenshots or a before/after pair:

- keep ledger bullets tagged by screen (`Screen A`, `Screen B`, etc.)
- identify what actually changed visually before judging whether it improved
- never treat `different` as `better`
- state, for each change: did it improve clarity, regress it, or shift an unresolved tradeoff

Expected comparison block format:

```
## Comparison — Screen A vs Screen B

### Changed and improved
- [change]: [why the visible evidence supports "better"]

### Changed and regressed
- [change]: [why the visible evidence supports "worse"]

### Changed, tradeoff unresolved
- [change]: [what is gained, what is lost, what would settle it]
```

## Uncertainty block

End the review with a section titled `What I cannot conclude from this screenshot`. Typical items:

- hover, focus, pressed, or motion behavior
- responsive behavior across breakpoints
- hidden or secondary states not shown
- real accessibility compliance beyond obvious visual symptoms
- exact spacing tokens, grid, or type scale
- actual copy correctness beyond what is legible
- screenshot quality limits (cropped, low-resolution, compressed, visually noisy)

Be direct. If the image quality or missing context lowered confidence, say so.

## Measurement policy

Never state as fact — always approximate or describe qualitatively:

- exact pixel values ("16 px gap", "48 px button height")
- exact counts above ~7
- exact color codes (hex, RGB, HSL, token names)
- WCAG contrast ratios from a screenshot
- 1–2 px alignment differences
- microcopy that is visibly small or compressed

Safe patterns:

- relative size: "about the same gap as the padding on the card next to it"
- ratios: "roughly 2× the line-height", "about 1.15× the adjacent card's padding"
- qualitative color: "cool desaturated gray, slightly darker than the background"
- approximate counts: "roughly 8–10 items", "a short row of three"
- approximate microcopy: "appears to read ‘Upgrade plan’"

## Final report template

Use this structure for the full output. Adjust only where the task demands it.

```
## Literal read
[screen type, blocks in reading order, dominant element, obvious issues]

## Visual Evidence Ledger
1. Location: … / Visible fact: … / Read on the relationship: … / Perception: high-confidence visible | low-confidence read
2. …
…

## Diagnosis
- Block logic: [judgement tied to ledger bullets]
- Spacing and alignment: [judgement tied to ledger bullets]
- Hierarchy and emphasis: [judgement tied to ledger bullets]
- Readability, typography, color: [judgement tied to ledger bullets]

## Recommendations
[Severity] Short issue name
- Location: …
- Visual evidence: …
- Why it matters: …
- Better direction: …
- Confidence: …

(repeat)

## Comparison (if multiple screenshots)
Changed and improved / regressed / tradeoff unresolved

## What I cannot conclude from this screenshot
- …
```
