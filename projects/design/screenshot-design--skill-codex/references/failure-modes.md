# Failure Modes

Read before sending the final answer.

## Core anti-bypass rule

A screenshot review is only good if a human reader can point from each conclusion back to something actually visible in the image.

The goal is not to sound like a designer.
The goal is to leave a visible audit trail of design judgment.

## Forbidden shortcuts

- Generic praise or critique without a visible anchor
- Importing code assumptions into a visual review
- Smuggling brand strategy that is not in the screenshot or the provided brief
- Applying the skill but leaving no visible trace in the chat that it was used
- Printing internal checking steps instead of using them silently
- Printing the whole internal ledger or long diagnostic essay by default
- Treating any large empty area as automatically elegant, premium, or minimal without judging what that negative space is doing
- Calling a screen balanced, harmonious, beautiful, or polished without evidence about visual mass distribution and eye path
- Skipping the explicit ugliness / disharmony / color-harmony check
- Praising component-level craft while ignoring stage-level imbalance or stranded whitespace
- Calling something balanced, premium, minimal, cluttered, clean, modern, or polished without visible support
- Writing an emotional ending that could have been written before looking at the screenshot
- Letting the emotional ending contradict the evidence-led critique above it
- Wrapping uncertainty in confident-sounding language
- Numeric scores without a visible basis
- Inferring invisible behavior from a static image
- Judging accessibility compliance beyond obvious visible symptoms
- Re-describing the product instead of reviewing it
- Conflating taste with craft

## Red flags

If any of these phrases appear in the draft, stop and return to the screenshot:

- "looks cleaner"
- "feels premium"
- "more modern"
- "spacing is off"
- "hierarchy is weak"
- "alignment seems weird"
- "the layout is balanced"
- "the whitespace makes it feel premium"
- "this is beautiful"
- "this feels harmonious"
- "probably"
- "likely accessible"
- "feels intuitive"
- "looks professional"

Replace each with a grounded ledger bullet or cut it.

## Self-check

- `Protocol Trace` is present as the first visible line
- The printed answer contains only `Protocol Trace`, `Protocol`, and `Recommendations` unless the user asked for more
- Every protocol point names a real conclusion earned from the internal ledger
- Every fix names a real conclusion earned from the internal ledger
- The ledger hits the minimum composition
- At least one ledger bullet judges composition, negative space, or visual mass at frame level
- Every ledger bullet has a `Perception:` tag
- Low-confidence reads did not silently become confident findings
- Uncertainty is surfaced in the protocol when needed
- Internal checks were done but not printed unless the user asked
- The protocol includes a visible `Color harmony` line
- The protocol includes a visible whole-screen `State` line: `broken`, `mixed`, `close`, or `resolved`
- Ugly, disharmonious, or contradictory color relationships become a recommendation when they materially hurt the screen
- Any beauty / harmony / balance claim cites ledger bullets about empty space, mass distribution, and eye path
- No red-flag phrase survived
