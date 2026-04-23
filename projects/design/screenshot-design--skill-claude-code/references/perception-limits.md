# Perception Limits

Read before writing the ledger. These are the kinds of visual judgement where multimodal models (this one included) systematically fail, based on 2026 research on VLM visual perception errors.

## Why this file exists

On fine-grained visual tasks top multimodal models still stay below ~50% accuracy, and around 29% of confidently-correct reasoning answers contain an underlying perception error. The failure is rarely in the reasoning — it is in how the image was read. Most of the damage in a screenshot review comes from treating low-confidence perceptual reads as if they were facts.

The fix is not to stop looking. The fix is to mark the uncertainty at the moment of looking, so it cannot silently propagate into protocol findings and recommendations.

## Fragile perceptions — mark or downgrade

For each item below: state the observation, mark it approximate, and prefer relative language over exact numbers.

### Counting

- Exact counts of icons, list items, rows, dots, cards are unreliable, especially above ~7.
- Use ranges or qualitative language: "roughly 8–10 items", "a dense list", "a short row of three". If an exact count matters for the review, say so and flag the uncertainty.

### Exact pixel measurements

- The model cannot measure in pixels. Do not claim "12 px" or "16 px padding".
- Prefer relative references: "~1x line-height", "~2x the gap above", "about the same as the padding on the card to its left".

### Tiny text / microcopy

- Small text, labels under roughly 10–12 px, and compressed regions are read unreliably. Wrong-reading is one of the canonical VLM hallucination modes.
- When quoting microcopy, mark it approximate ("appears to read ‘Upgrade plan’") or quote only the portion that is clearly legible.

### Hairline alignment

- 1–2 px alignment differences, sub-pixel offsets, and optical-vs-geometric alignment are below reliable perception.
- Say "appears aligned" / "appears slightly off" rather than asserting misalignment. If the misalignment is only suspected, mark confidence low.

### Color codes

- Do not guess hex, RGB, HSL, or token names from a screenshot.
- Describe color in perceptual terms: "cool neutral gray", "desaturated blue slightly darker than the background", "warm accent close to the primary brand color".

### Contrast ratios

- Do not cite WCAG ratios from a screenshot. They require measurement.
- You may flag contrast that looks visibly weak ("body copy sits close in value to the background, readability feels strained") and leave the exact ratio to accessibility tools.

### Spatial relationships

- "Above / below / to the left of" is reliable.
- "Exactly aligned to column N of a 12-col grid", "16 px from the edge", "perfectly centered" is not — treat as approximate unless directly visible as a bounding edge.

### Depth, occlusion, z-order

- Drop shadows, modal overlays, stacked cards: describe what is on top, not exact elevation tokens.

### Invisible states

- Hover, focus, pressed, disabled, loading, error states that are not currently displayed cannot be judged. Surface that limit in the protocol only when it materially matters.

### Reading intent from filenames or surrounding chat

- Only the pixels in the frame count as evidence. Do not let filenames, captions, or the user's phrasing decide what is "on the screen".

## Canonical hallucination modes (2026 literature)

Watch for these patterns in your own draft:

1. **Contextual guessing** — describing what usually appears on this kind of screen, not what is actually shown.
2. **Identity incongruity** — misnaming a component (calling a menu a modal, a tab a pill).
3. **Visual illusion** — misreading a composition because of an optical effect (e.g., claiming misalignment that is actually optical balance).
4. **Wrong reading** — OCR-style mistakes on small or stylized text.
5. **Numeric discrepancy** — wrong counts, wrong ordering, wrong cardinality.
6. **VLM-as-classifier** — collapsing nuance into a familiar template ("this is a SaaS dashboard, so…").
7. **Geographical / positional erratum** — claiming wrong relative positions.
8. **Attention dispersion under long reasoning** — perceptual description is correct, but later reasoning drifts away from the region of interest.

## Prompting rules for this skill

Applied across the workflow:

- **Ground every bullet** — `Location` is required on every ledger bullet. "General feel of the page" is not a location.
- **Mark confidence** — every ledger bullet ends with a confidence tag: `[HC]` for `high-confidence visible` or `[LC]` for `low-confidence read`. Use `[LC]` for counts, microcopy, hairline alignment, color guesses, or inferred state.
- **Re-attend before recommending** — after drafting recommendations, read the screenshot again against each one and delete any that do not survive the second look.
- **Describe before judging** — the Literal Read comes first. It anchors attention and reduces contextual guessing.
- **Check the frame before the parts** — note where the visual mass sits, which regions stay dormant, and whether the empty space acts as counterweight or merely leftover canvas.
- **Negative space is not automatically good** — empty area only helps if it sharpens focus, creates tension, or balances another active region. If one side is overloaded while the other side does nothing, call that stranded whitespace.
- **Color harmony is perceptual, not numeric** — check whether colors visibly clash, muddy each other, flatten the scene, or contradict the palette logic. Do not invent formal theory claims or exact color measurements you cannot actually see.
- **Prefer relative over absolute** — any time an exact number is tempting, switch to a ratio relative to a reference element in the frame.
- **Push unverifiable claims into uncertainty, not into verdicts** — if a claim cannot be shown on the pixels, it does not belong in the protocol findings or recommendations.
