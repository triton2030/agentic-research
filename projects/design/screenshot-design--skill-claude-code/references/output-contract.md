# Output Contract

Read when composing the internal ledger and the printed review.

This contract is meant for repeated passes on the same design.
Use it, fix the strongest problems, then apply it again to the updated screenshot until the screen looks resolved.

## Internal evidence ledger

The ledger is still mandatory, but by default it stays internal.
Do not print it in chat unless the user explicitly asks to see the evidence trail.

Produce 8-12 internal one-line bullets.

Format:

`- Slot / location — visible fact → read on the relationship. [HC|LC]`

Where:

- `Slot` is a compact reading lane such as `Canvas`, `Payload`, `Eye path`, `Rhythm`, or `Craft`
- `location` can be full-frame or local
- `HC` means `high-confidence visible`
- `LC` means `low-confidence read`

Use [perception-limits.md](perception-limits.md) when deciding the `Perception:` tag.

At least one bullet must operate at scene level rather than only at component level. "This card has good spacing" is not enough if the overall frame is compositionally dead.

Minimum composition:

- >= 1 full-frame bullet on composition, negative space, visual mass distribution, or scene balance
- >= 1 bullet on eye path, hierarchy, or emphasis
- >= 1 bullet on grouping, spacing, containment, or rhythm
- >= 1 bullet on typography, contrast, color, or readability
- >= 1 bullet on color harmony, palette energy, or visible color conflict when color is materially in play

Do not proceed to critique until all five are covered.

### Good bullets

- `Canvas / full frame` — left half carries nearly all active text and rule weight while the right ~40% stays mostly empty. → The eye runs out of work and the frame reads as a left-aligned document, not a staged composition. `[HC]`

- `Eye path / hero` — the headline dominates immediately, but there is no secondary anchor on the right or lower-right to catch the gaze. → Attention lands hard and then stalls instead of traveling through a composed scene. `[HC]`

- `Craft / pricing row` — the middle card appears to have slightly stronger border contrast and a touch more vertical padding than its neighbors. → It reads as the emphasized option even without an explicit label. `[LC]`

### Weak bullets

- "Spacing feels off."
- "The hierarchy is weak."
- "This looks cleaner."
- "It feels more premium now."

## Printed review

Print only a short visible review with this fixed order:

- `## What I Notice First`
- `## What Starts To Break`
- `## Verdict`
- `## Fix Next`
- `## Limits` only if needed

Rules:

- Do not give the verdict first.
- Do not print a progress trace, status ledger, or checklist.
- Do not dump raw internal reasoning.
- The visible order should feel conversational, but compressed.

`What I Notice First`:

- 2-4 short bullets or sentences
- whole frame before local details
- where the weight sits, what the eye catches, what the empty space is doing
- no final verdict yet

`What Starts To Break`:

- 2-4 short bullets or sentences
- the strongest failures in harmony, alignment, rhythm, or semantic balance
- each point ties a visible cue to its effect on reading, emphasis, or felt composition
- still no final verdict yet

`Verdict`:

- one short paragraph
- comes after the visible examination
- synthesizes the screen as a whole
- may use `broken`, `mixed`, `close`, or `resolved` only if helpful

`Fix Next`:

- list only the strongest 1-3 changes
- highest leverage first
- composition and frame before local polish
- make each item concrete enough for the next edit pass to start immediately

`Limits`:

- optional and brief
- use only when crop, image quality, or hidden states materially limit the read

### Good `What I Notice First` lines

- `The headline wins immediately, but almost all active weight still sits on the left, so the frame reads as one loaded column plus passive canvas.`
- `The first pass feels orderly, but the page has no second anchor after the hero, so the eye lands and then stalls.`

### Good `What Starts To Break` lines

- `The hero CTA hangs lower than the supporting copy, so the action feels detached from the argument that should justify it.`
- `The empty space on the right is large enough to matter, but it is not balancing anything yet, so it reads as leftover space rather than compositional tension.`

### Weak printed lines

- "Spacing feels off."
- "It looks more premium."
- "The hierarchy is weak."
- "Everything is fine except some polish."

## Comparison mode

Use only when there are multiple screenshots or a before/after pair.

Rules:

- keep ledger bullets tagged by screen (`Screen A`, `Screen B`, etc.)
- identify what actually changed before judging whether it improved
- never treat `different` as `better`
- say which change improved clarity, which regressed, and which tradeoff remains unresolved
- put the winner or tradeoff in `Verdict`, not at the top of the answer

## Limits handling

By default, surface limits as a short `Limits` section only when needed.

Typical items:

- hover, focus, pressed, or motion behavior
- responsive behavior across breakpoints
- hidden or secondary states not shown
- real accessibility compliance beyond obvious visible symptoms
- exact spacing tokens, grid, or type scale
- actual copy correctness beyond what is clearly legible
- screenshot quality limits such as crop, compression, or low resolution

Keep the uncertainty language tight and specific.

## Measurement policy

Never state as fact:

- exact pixel values
- exact counts above ~7
- exact color codes
- WCAG ratios from a screenshot
- 1-2 px alignment differences
- microcopy that is visibly tiny or compressed

Prefer:

- relative size: "about the same gap as the padding on the card next to it"
- ratios: "roughly 2x the line-height"
- qualitative color: "cool desaturated gray"
- approximate counts: "roughly 8-10 items"
- approximate microcopy: "appears to read 'Upgrade plan'"

## Final report template

```text
## What I Notice First
- The headline reads clearly, but most of the active weight still sits on the left, so the frame opens as one heavy text column plus passive space.
- The eye lands hard on the hero and then struggles to find a second anchor.

## What Starts To Break
- The CTA sits low enough below the supporting copy that it feels detached from the message instead of completing it.
- The right-side space is large, but it is not counterbalancing anything yet, so it reads as leftover canvas rather than intentional tension.
- The palette stays too quiet to build a strong emphasis ladder after the headline.

## Verdict
The screen is mixed: the message is readable, but the composition still feels under-resolved. It has decent local craft, yet the frame does not distribute weight and emphasis deliberately enough to feel harmonious.

## Fix Next
- Rebalance the frame: either give the right side a real visual anchor or tighten the left block so the empty field starts working as counterweight.
- Pull the CTA into the hero unit: reduce the gap below the supporting copy so the action reads as the close of the message.
- Strengthen the second emphasis point: add enough contrast or shape that the eye has a meaningful stop after the headline.

## Limits
- The crop hides the footer, so the final balance read is limited to the visible frame.
```
