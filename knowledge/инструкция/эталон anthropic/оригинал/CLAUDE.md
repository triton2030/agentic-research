# Civic-Chain — Project guide

Single-page civic-tech landing + lightweight design-system reference.
One brand pair (deep civic blue `#131F86` + warm cream `#F3F1E8`), DM Serif
Text + DM Sans, four editorial surface tones (cream / dusty / gold / sage).

## Files

```
Landing Page.html    — the landing (hero, portal, problem, how, numbers,
                       workflow, trust, CTA, FAQ). One <script> at the
                       bottom holds the content data + small hydrations.
design-system.html   — living reference for tokens, primitives, patterns.
                       Read this to see anything the DS offers in one page.

ds/
  tokens.css         — all design tokens. Hex, sizes, spacing, motion.
                       Never hard-code a hex or a px size in the other files.
  primitives.css     — small, focused building blocks. Each class has ONE
                       job: type, spacing, surface, icon-chip, badge, btn,
                       stage-pill, expandable mechanism, scroll-reveal.
  patterns.css       — composites that carry meaning (hero-grid, bento-3,
                       portal-card, vignette, metric-card, workflow-card,
                       proof stack, CTA, FAQ, compact-portal).
  expandable.js      — hydrator for [data-expandable] reveal blocks.
  icons.svg          — sprite; referenced with <use href="#icon-…"/>.

brand/               — logos + webp illustrations.
```

## The layering rule (read this before editing CSS)

```
tokens.css   →   primitives.css   →   patterns.css   →   HTML
(values)         (how it looks)       (how it composes)   (what it says)
```

- **Primitives never reach up into tokens with magic numbers.** Always
  `var(--token-name)` — add a new token in `tokens.css` if you need one.
- **Patterns never redefine a primitive's geometry.** If a pattern needs
  a different icon-chip size, it picks a size modifier (`icon-chip-sm/md/lg`)
  or sets `--icon-chip-size` inline. It does NOT write `.pattern .icon-chip
  { width: … }`. Same rule for radii, font-sizes, colors.
- **Patterns may own layout only** — position, grid-column, z-index, margins
  that are specific to the composition. If you find yourself writing
  `.some-pattern .icon-chip { width: 2rem }` you are restyling a primitive;
  add a new size modifier in `primitives.css` instead.
- **HTML uses tokens & utility classes first; inline `style=""` only for
  truly one-off values** (max-widths, `color-mix` tweaks on a single tone).

## Expandable pattern

Any clickable reveal block — workflow tool cards, FAQ accordion, future
"read more" — uses the same mechanism.

```html
<div class="surface tone-cream" data-expandable>
  <!-- always-visible content -->
  <h3>Title</h3>
  <p>Short scenario.</p>

  <!-- reveals on click -->
  <div class="expandable-body"><div class="inner">
    <p>Body that fades in.</p>
  </div></div>

  <span class="expandable-hint">
    <span class="hint-open">Expand</span>
    <span class="hint-close">Close</span>
    <span class="arrow">↗</span>
  </span>
</div>
```

- `data-expandable-group="multi"` — each card toggles independently (default).
- `data-expandable-group="single"` + `[data-expandable-scope]` wrapper —
  accordion: only one open at a time inside the scope.
- Hydrated automatically by `ds/expandable.js` on DOMContentLoaded.
  For dynamically-rendered content (e.g. workflow grid built via
  innerHTML), call `window.DSExpandable.hydrate()` after injecting.

## Landing content data

Workflow tools and FAQ items live as JS arrays at the bottom of
`Landing Page.html` (`workflowTools`, `faqItems`). To add or reorder:
edit the arrays. Templates are inline so grep for `workflow-card` or
`faq-card` to find the markup.

## Cache-busting

`ds/*.css` and `ds/expandable.js` are imported with a `?v=N` query string
in `Landing Page.html`. Bump N when you change CSS/JS and reviewers seem
to be seeing stale output. `design-system.html` imports them unversioned
(it reloads freely during DS work).

## Adding a new landing section

1. Decide the surface tone (rotate the four — never two adjacent cards
   in the same tone).
2. Reuse an existing pattern (`bento-3`, `metric-card-inner`,
   `problem-card-inner`, `vignette`, `trust-layout`, `faq-card-inner`).
   Nothing exists? Add a new pattern in `patterns.css` under a clear
   comment banner, using only tokens + existing primitives.
3. Wrap in the standard section shell:
   ```html
   <section class="shell" id="my-section">
     <div class="shell-inner">
       <div class="stack stack-section-heading">
         <div><span class="badge">Eyebrow</span></div>
         <div class="stack stack-heading-copy">
           <h2 class="type-heading max-w-4xl">Headline.</h2>
           <p class="type-body-lg text-muted max-w-2xl">Supporting copy.</p>
         </div>
         <!-- content -->
       </div>
     </div>
   </section>
   ```
4. Update `design-system.html` if you introduced a new primitive or
   pattern — the DS page should always show everything the system offers.

## Verifying a change

1. `done Landing Page.html` → check console clean.
2. Open `design-system.html` → all sections still render.
3. If you touched CSS, bump the `?v=N` in `Landing Page.html`.
4. `fork_verifier_agent` for a background screenshot sweep.

## Deliberate non-goals

- No build step. No bundler. No Tailwind. No React. Stay vanilla.
- No external icon library — `ds/icons.svg` is the only sprite.
- No dark mode (explicit: `color-scheme: light`).
- No JS framework. `ds/expandable.js` is the only behavior script; the
  rest is small IIFEs inside `Landing Page.html`.
