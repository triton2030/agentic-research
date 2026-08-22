# Agent CSS Method

Use when the task is broad, ambiguous, or likely to create style debt. Do not
read for simple leaf edits after the owner is obvious. Avoid the common failure:
a local-looking class that creates an unowned future dependency.

## Pre-code Vocabulary Gate

Use one of two modes before the first source edit:

- **New build**: derive the smallest closed vocabulary from the current brief
  and references before scaffolding JSX, CSS, theme variables, or components.
- **Existing frontend**: inspect and reuse the current vocabulary and owners;
  consolidate drift instead of introducing a parallel system.

For broad work, name only the current roles for typography/fonts, colors,
spacing, radii, surfaces, repeated UI objects, and finite states. Use the
existing theme or a small selected subset of Tailwind defaults. Do not create a
plan file, speculative scale, component catalog, or token layer.

For a leaf fix with an obvious owner, skip the full inventory and make the
smallest owner-level change.

## Owner Layers

Classify before editing:

- **Token**: reusable design value; color role, spacing, radius, shadow,
  typography, breakpoint/container, z-index level.
- **Layout/composition**: spatial relationship; flex/grid flow, gap, wrapping,
  scroll, sticky, intrinsic layout.
- **Component/block**: stable UI object; button, card, field, modal, table row.
- **Variant/exception**: controlled difference; size, tone, density, selected,
  invalid, loading, destructive.
- **Global override**: base styles, uncontrolled Markdown/HTML, third-party
  markup, reset, CSS layers.

Default: choose the smallest layer with real ownership. If one change touches
many unrelated files, stop and reduce change radius.

## Agent Procedure

1. Name the observable result.
2. Select new-build or existing-frontend mode and pass the vocabulary gate.
3. Identify the existing or intended owner before editing.
4. Try the no-new-code path: delete a conflict, use a current token/variant,
   move one class to the owning element, or let intrinsic layout work.
5. Pick the owner layer with the smallest future blast radius.
6. Change only that layer.
7. Stress the relevant states.
8. Consolidate near-duplicates and delete redundant classes, wrappers, variants,
   arbitrary values, tokens, or stale CSS.

## Failure Modes

- **Override pile**: new class -> breakpoint -> `!important`. Fix owner first.
- **Screenshot fix**: one viewport passes, long content/mobile breaks. Run state
  matrix.
- **Arbitrary drift**: many `w-[317px]`-style values. Promote repeated roles to
  tokens; keep true one-offs local.
- **Variant leak**: callers pass long `className` patches. Add finite variants.
- **Breakpoint theater**: many viewport prefixes solving a container problem.
  Prefer intrinsic layout/container queries.
- **Best-practice cargo cult**: new token/variant/component/CSS layer because it
  is "cleaner". Add it only when it removes current duplication or risk.
- **Token mirror**: Tailwind's existing scale is copied into custom variables.
  Select a small working subset; add semantic tokens only for current roles.
- **Premature component system**: long class lists or possible future reuse
  produce a catalog of shallow components. Extract only stable repeated UI
  objects.
- **Global fog**: global selector changes many pages. Move to component/variant
  or isolate in a deliberate layer.

## Smell Radar

Inspect, do not auto-rewrite:

- hard-coded repeated values or duplicate selector blocks;
- high specificity, deep nesting, or global selectors outside base/prose;
- dynamic classes, unbounded `className`, or contradictory utilities;
- child margins instead of parent gap, fixed heights, or hidden layout errors.

## Delete Pass

Ask:

- Can `gap-*` replace child margins?
- Can `px-*`, `py-*`, or `size-*` replace side pairs?
- Can parent layout replace a wrapper?
- Can a variant replace repeated conditional classes?
- Can a token replace repeated arbitrary values?
- Can `min-w-0`, `min-h-0`, or `minmax(0,1fr)` solve overflow honestly?
- Can lower specificity or layer order replace override escalation?

Sources: [Tailwind utilities](https://tailwindcss.com/docs/styling-with-utility-classes),
[class detection](https://tailwindcss.com/docs/detecting-classes-in-source-files),
[Every Layout](https://every-layout.dev/rudiments/composition/),
[CUBE CSS](https://cube.fyi/), [CSS maintainability](https://digitalcommons.calpoly.edu/theses/1842/).
