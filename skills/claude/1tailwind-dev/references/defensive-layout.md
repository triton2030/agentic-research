# Defensive Layout

Use when fixing layout, overflow, responsive behavior, long content, flex/grid,
container queries, sticky, or scroll.

## Reader Job

Remind the agent about browser layout traps that source reading often misses.

## First Question

When layout breaks, ask: which element may shrink, who owns
wrapping/truncation, which parent owns scroll, whether flex/grid minimum content
size is involved, and whether fixed size fights dynamic content.

Do not start with `overflow-hidden` unless clipping is intended.

## Flex

Use `min-w-0` on flex children that contain truncating/wrapping text:

```tsx
<div className="flex gap-3">
  <div className="min-w-0 flex-1">
    <p className="truncate">...</p>
  </div>
</div>
```

Use `min-h-0` in vertical flex layouts where a child should scroll:

```tsx
<main className="flex min-h-0 flex-1 flex-col">
  <section className="min-h-0 overflow-auto" />
</main>
```

Use `shrink-0` for icons/avatars/controls, not large content regions unless
overflow is intended.

## Grid

Use `minmax(0,1fr)` when a grid track must shrink around long content:

```tsx
<div className="grid grid-cols-[minmax(0,1fr)_auto]" />
```

If a grid child contains a carousel/table, put `min-w-0` on the grid item that
owns the scroll.

## Intrinsic Before Breakpoints

Before adding breakpoint stacks, try `flex-wrap`, `gap`, `max-w-*`,
`aspect-*` + `object-cover`, `repeat(auto-fit,minmax(...))`, `clamp()`, or
container queries.

Use viewport breakpoints for page shells; container queries for reusable
components whose layout depends on parent width.

## Spacing Ownership

Parent owns spacing between children: `grid gap-6`, `flex gap-2`, `space-y-4`.
Child owns internal padding. Repeated `mt-*` on siblings usually means missed
parent layout.

## Stress Cases

Check relevant stressors: long unbroken word, 2x translation, empty/missing
optional content, wrong image ratio, one item/many items, narrow container,
nested scroll, loading/error states.

Choose deliberately: truncate secondary text, wrap important text, clamp card
rhythm, scroll expected overflow regions.

## State Traps

- Loading should preserve dimensions.
- Error text should not push primary actions away.
- Focus-visible must remain visible.
- Selected/active should not shift layout.
- Dark mode should use tokens, not guessed inversions.

Sources:

- https://defensivecss.dev/tip/flexbox-min-content-size/
- https://defensivecss.dev/tip/grid-min-content-size/
- https://defensivecss.dev/tip/long-content/
- https://every-layout.dev/
- https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries
