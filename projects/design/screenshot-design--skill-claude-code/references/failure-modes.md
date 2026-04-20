# Failure Modes

Read when the review starts to sound smarter than it looks.

## Core anti-bypass rule

A screenshot review is only good if a human reader can point from each conclusion back to something actually visible in the image. The goal is not to sound like a designer — the goal is to leave a visible audit trail of design judgment.

## Forbidden shortcuts

- Generic praise or critique without a visible anchor.
- Claimed exact pixel measurements not actually read from the image. If measurement is needed, mark it approximate ("~2× line-height", "about 1.15× padding") and tie it to what is visible.
- Importing code assumptions into a visual review. The screenshot is the evidence.
- Smuggling brand strategy that is not in the screenshot or in the provided brief.
- Calling something balanced, premium, minimal, cluttered, clean, modern, or polished without explaining what specifically creates that effect.
- Wrapping uncertainty in confident-sounding language. If confidence is low, say so.
- Numeric scores without a visible basis. If a score is given, its components must be traceable to ledger bullets.
- Inferring invisible behavior from a static image — hover, focus, motion, responsive, onboarding flow, error states.
- Judging accessibility compliance beyond what is visibly wrong in the frame (e.g., obvious low contrast). Real a11y needs tools, not a screenshot.
- Reading intent from filenames or screenshot titles. Only the pixels count.
- Re-describing the product instead of reviewing it. Literal read is two or three lines, not the whole response.
- Conflating taste with craft. "I would do it differently" is not a finding — a finding has a visible fact behind it.

## Perception hallucinations to catch in your own draft

Documented failure modes for multimodal models on visual tasks (2026 literature). Watch for these:

- **Contextual guessing** — describing what usually appears on this kind of screen, not what is actually shown. Cut anything you cannot point to.
- **Identity incongruity** — calling a menu a modal, a tab a pill, a toast a banner. Slow down and name only what the pixels show.
- **Visual illusion** — asserting misalignment or imbalance driven by optical effects. Mark as `low-confidence read` or drop.
- **Wrong reading** — OCR mistakes on small or stylized text. Quote only clearly legible portions; mark the rest approximate.
- **Numeric discrepancy** — wrong counts, wrong ordering, wrong cardinality. Default to ranges ("roughly 8–10") for counts above ~7.
- **VLM-as-classifier** — collapsing nuance into a familiar template ("this is a SaaS dashboard, so…"). Review this specific screen, not the genre.
- **Attention dispersion under long reasoning** — perceptual description is correct, but diagnosis and recommendations drift away from the region of interest. If the draft became abstract, return to the screenshot and re-anchor.

See [perception-limits.md](perception-limits.md) for the full catalog and the rules for marking fragile reads.

## Red flags

If any of these phrases appear in the draft, stop and return to the screenshot:

- "looks cleaner"
- "feels premium"
- "more modern"
- "spacing is off"
- "hierarchy is weak"
- "alignment seems weird"
- "the layout is balanced"
- "probably"
- "likely accessible"
- "feels intuitive"
- "looks professional"

Replace each with a three-line ledger bullet (`Location` / `Visible fact` / `Read on the relationship`) or cut it.

## Self-check before sending

- Every judgement in Diagnosis names at least one ledger bullet.
- Every Recommendation names the ledger bullet(s) it rests on.
- The ledger hits the minimum composition (spacing, hierarchy, alignment, readability).
- Every ledger bullet has a `Perception:` tag; low-confidence reads have not silently been promoted into confident diagnoses or recommendations.
- The Re-attention pass actually happened: each recommendation was checked against the screenshot again.
- The uncertainty block is present, and anything not visible in the image lives there, not in the diagnosis.
- No red-flag phrase above survived.
