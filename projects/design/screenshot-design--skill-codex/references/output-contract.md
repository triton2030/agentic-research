# Output Contract

Read when composing the internal ledger, the visible protocol, and the compact recommendations.

This contract is meant for repeated passes on the same design.
Use it, fix the strongest problems, then apply it again to the updated screenshot until the screen looks resolved.

## Protocol Trace

Every printed answer must start with one compact visible line:

`Protocol Trace: screenshot-design applied | evidence gate: ok | audit: ok | internal checks: ok | comparison: n/a|done | uncertainty: none|present`

Rules:

- this line must be visible in chat
- keep it to one line
- do not print the full internal checklist
- do not fake `ok`; only print a status that was actually earned
- use `n/a` when a branch did not apply

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

## Protocol

Print only a short visible protocol.

Recommended shape:

- `Evidence gate:` one short line
- `State:` one short line on the screen as a whole: `broken`, `mixed`, `close`, or `resolved`
- `Scene:` one short line
- `Structure:` one short line
- `Surface:` one short line
- `Color harmony:` one short line
- `Internal checks:` one short line
- `Comparison:` only if multiple screenshots
- `Uncertainty:` only if needed

The protocol is not a checklist recital.
Open with the strongest frame-level truth, then cover the minimum proof surface compactly.

## Strongest fixes

List only the strongest 1-4 fixes.

Use this shape for each issue:

`[Severity] Short issue name`
- `Fix:` `<concrete change>`
- `Why:` `<one clause tied to scene / structure / surface / color harmony>`

## Comparison mode

Use only when there are multiple screenshots or a before/after pair.

Rules:

- keep ledger bullets tagged by screen (`Screen A`, `Screen B`, etc.)
- identify what actually changed before judging whether it improved
- never treat `different` as `better`
- state whether each change improved clarity, regressed it, or left a real tradeoff unresolved
- do not create a separate `Comparison` section by default; fold the result into `Protocol` and `Recommendations`

## Uncertainty handling

By default, surface uncertainty as one compact `Uncertainty:` line inside `Protocol`.
Do not create a separate uncertainty section unless the user explicitly asks for more detail.

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
Protocol Trace: screenshot-design applied | evidence gate: ok | audit: ok | internal checks: ok | comparison: n/a | uncertainty: none

## Protocol
- Evidence gate: screenshot is legible enough for aesthetic judgement.
- State: broken; the frame is still compositionally unresolved.
- Scene: left-heavy composition; empty right field reads unused, not intentional.
- Structure: headline, subhead, and payload stack too densely in one zone.
- Surface: typography is readable, but the screen feels more document-like than staged.
- Color harmony: palette feels inert / clashes / no visible color conflict.
- Internal checks: re-attention + fresh-eye sweep completed.
- Comparison: Screen B improves eye path but weakens rhythm. [only if multiple screenshots]
- Uncertainty: crop hides the footer, so final balance judgement is partial. [only if needed]

## Recommendations
[High] Short issue name
- Fix: ...
- Why: ...
```
