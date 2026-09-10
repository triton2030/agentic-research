# Civic-Chain Design System

One brand pair, four editorial tones, two type registers, ten patterns.
See `../design-system.html` for the living reference — it renders every
token, primitive, and pattern this folder offers.

## Layering

```
tokens.css   →   primitives.css   →   patterns.css
```

- **tokens.css** — every hex, size, spacing step, radius, shadow, motion
  curve, and semantic alias. No selectors, no geometry — just
  `:root { --name: value }`.
- **primitives.css** — utility classes, each with ONE job.
  Base reset · typography (`type-*`) · radius (`radius-*`) · spacing
  (`stack`, `pad-*`, `gap-*`, `max-w-*`) · colors (`text-*`) ·
  `badge`, `btn` variants, `icon-chip` (+ size modifiers), `stage-pill`,
  `surface` (+ `tone-*` variants), `landing-grid-overlay`, the
  `expandable` mechanism, `scroll-reveal`.
- **patterns.css** — composites. Section shell + bento grids, hero-grid,
  portal-card, problem-card, vignette (how-it-works), metric-card,
  workflow grid & cards, trust/proof stack, CTA, FAQ grid,
  problem-illustration, compact-portal (sticky role chooser).

## Primitive catalogue (quick reference)

| Class | What it does |
|---|---|
| `surface` + `tone-cream`/`tone-dusty`/`tone-gold`/`tone-sage` | Card with border, ambient shadow, one of 4 tones |
| `surface.interactive` | Adds hover lift + shadow transition |
| `badge` | Uppercase section eyebrow pill |
| `btn` + `btn-primary`/`btn-outline`/`btn-ghost` + `btn-lg` | Buttons |
| `icon-chip` + `icon-chip-sm`/`icon-chip-md`/`icon-chip-lg` | Round-square glyph chip (2.25 / 3 / 3.5rem). Override via `--icon-chip-size` inline for one-offs. |
| `stage-pill` | Small uppercase status pill |
| `type-display`/`type-heading`/`type-heading-sm` | Serif display register |
| `type-title`/`type-title-sm`/`type-body-lg`/`type-body`/`type-body-sm`/`type-label` | Sans register |
| `text-muted`/`text-c75`/`c68`/`c58`/`c42` | Foreground tints (currentColor blended with transparent) |
| `stack` + `stack-*` | Grid-based spacing rhythm |
| `pad-card`/`pad-card-vignette`/`pad-pill`/`pad-fact` | Named padding presets |
| `max-w-sm`…`max-w-72ch` | Measure limiters |
| `[data-expandable]` + `.expandable-body > .inner` + `.expandable-hint`/`.expandable-toggle`/`.expandable-label` | Click-to-reveal blocks (see below) |
| `[data-scroll-reveal]` | Progressive-enhancement scroll-timeline fade-up |

## Pattern catalogue

| Class | Used by |
|---|---|
| `section.shell` + `.shell-inner` | Every landing section |
| `stack-section-heading` + `stack-heading-copy` | Badge / heading / supporting copy block |
| `hero-grid` | Hero |
| `bento-3` / `bento-12` | Portal hub, problem, how-it-works, numbers |
| `portal-card-inner` | Three role cards |
| `problem-card-inner` + `problem-artwork` | Problem trio |
| `vignette` + `vignette-blob-*` + `vignette-content` + `vignette-topbar` + `stages` | How-it-works blocks |
| `how-card-inner` | Outer wrapper for how blocks |
| `metric-card-inner` + `metrics-layout` | Numbers section |
| `workflow-grid` + `workflow-card` + `workflow-card-inner` + `workflow-card__chip` + `workflow-scenario` | Expandable capability cards |
| `trust-layout` + `trust-quote-card` + `proof-card` + `proof-lead`/`proof-fact`/`proof-wide` + `proof-supporting-grid` | Trust/proof stack |
| `cta-layout` + `cta-illustration` + `cta-footer-links` + `btn-row` | Final CTA |
| `faq-grid` + `faq-card-inner` | FAQ accordion |
| `problem-illustration` | Full-bleed interstitial image |
| `compact-portal` + `compact-portal-link` | Sticky role-picker bar |

## The layering rule

> A pattern never redefines a primitive's geometry (size, radius, color).
> It picks a variant or sets a custom property. If the variant you need
> doesn't exist, add it in `primitives.css`.

**Wrong:**
```css
.workflow-card .icon-chip { width: 2.25rem; height: 2.25rem; border-radius: 0.75rem; }
```

**Right:**
```html
<span class="icon-chip icon-chip-sm workflow-card__chip">…</span>
```
```css
/* patterns.css — layout only */
.workflow-card__chip { position: absolute; top: 1rem; right: 1rem; }
```

## Expandable mechanism

`[data-expandable]` is the one way to build a reveal-on-click block
(workflow tool cards, FAQ accordion, any future "show more").

```html
<div class="surface tone-cream" data-expandable>
  <h3>Title</h3>
  <div class="expandable-body"><div class="inner">
    <p>Body copy that fades in.</p>
  </div></div>
  <span class="expandable-hint">
    <span class="hint-open">Expand</span>
    <span class="hint-close">Close</span>
    <span class="arrow">↗</span>
  </span>
</div>
```

- `data-expandable-group="multi"` (default) — toggles independently.
- `data-expandable-group="single"` inside a `[data-expandable-scope]`
  wrapper — accordion, only one open at a time.
- Hydrated by `ds/expandable.js` on DOMContentLoaded. For JS-rendered
  cards, call `window.DSExpandable.hydrate()` after injection.

## Adding a new token

`tokens.css` is the canon. A new color, size, or motion curve belongs
here first. Keep semantic names (`--muted-foreground`), not
usage-specific names (`--problem-text-color`).

## Adding a new primitive

Prefer a size modifier on an existing primitive (e.g. `icon-chip-xl`)
over a brand-new class. Only add a full new primitive when it genuinely
has one isolated job (`badge`, `btn`, `stage-pill` are examples —
small, single-purpose, reused across patterns).

## Adding a new pattern

Open `patterns.css`, add a banner comment, compose from existing
tokens + primitives. Then add a demo card to `design-system.html` so
the reference stays complete.
