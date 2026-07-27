# Tailwind Patterns

Use when editing class strings, variants, tokens, Tailwind theme CSS, `@apply`,
`@utility`, `clsx`, `cva`, or `tailwind-merge`.

Contents:

- Reader Job
- Static Classes
- Duplication Rule
- Variant APIs
- className Boundary
- Tokens and Naming Priority
- Arbitrary Values
- @apply and Custom CSS
- Ordering

## Reader Job

Keep Tailwind as a constrained design API, not a string pile.

## Static Classes

Tailwind needs complete class strings in source. Replace
`` `bg-${tone}-600` `` with a finite map like
`{ info: "bg-sky-600", danger: "bg-red-600" }`.

If classes are missing in build, check dynamic construction before config.

## Duplication Rule

Do not abstract just because a class list is long.

Keep repeated utilities when local and easy to multi-edit. Create a component
when the repeated markup is a UI object. Create a token when a value is a
repeated design role. Create custom CSS for uncontrolled markup or third-party
selectors.

Before extracting, ask whether the duplicate is stable enough to name. Two
nearby repeats often cost less than a premature component, variant, or token.

## Variant APIs

Reusable components should expose named visual choices: `variant`, `size`,
`tone`, `density`, and `state`.

Use small maps first. Use `cva` only when compound variants or shared variant
logic make maps error-prone.

## `className` Boundary

Good `className`: outer layout, rare positioning, low-level primitive escape
hatch. Bad `className`: caller changes tone/size/state, overrides component
internals, or `tailwind-merge` hides missing variants.

Use `clsx` for conditions. Use `tailwind-merge` only where external utilities
are intentionally allowed to override internal classes.

Do not add `tailwind-merge` to make uncontrolled overrides feel safe. A missing
variant is usually the smaller fix.

## Tokens

Tailwind v4 theme variables are the design-system API. Name roles, not
accidents: `--color-danger`, `--radius-card`, `--shadow-panel`; avoid
`--spacing-17`, `--color-new-blue`, `--width-temp`.

Promote arbitrary values when they repeat or carry design intent. Keep one-offs
local.

Do not prebuild a complete type, spacing, radius, or color scale and do not copy
Tailwind's defaults into parallel custom variables. Select the smallest current
subset. Add a semantic token only when a distinct role repeats in the UI.

### Naming Priority

Apply this only after the token, variant, or component has earned an owner:

1. Preserve the existing project's established name.
2. Otherwise use Tailwind's official utility vocabulary, theme namespace, and
   default scale name.
3. Then use an already installed framework's semantic role when it is an exact
   fit.
4. Add the smallest conventional local role only when the earlier names would
   misstate its meaning.

Prefer `gap-4`, `rounded-md`, and `text-sm` to aliases such as
`gap-content-default`, `radius-interface-normal`, or `text-body-compact`.
Familiarity never excuses a false role.

In an existing shadcn/ui project, keep its established roles such as
`background`, `foreground`, `primary`, `muted`, `destructive`, `border`,
`input`, and `ring`. Without that framework or an equivalent local owner, do
not create its whole semantic map merely because the names are familiar.

## Arbitrary Values

Accept token-derived one-offs like
`max-h-[calc(100dvh-(--spacing(6)))]`; question visual magic like
`top-[13px] w-[317px] gap-[11px]`.

## `@apply` / Custom CSS

Use `@apply` sparingly for third-party/uncontrolled selectors or migration
bridges. Use `@utility` for missing low-level utilities that belong to the
design system, not one component. Prefer low-specificity global CSS such as
`:where()` for base/prose rules.

## Ordering

Use `prettier-plugin-tailwindcss` when the repo has Prettier. Do not hand-sort
large unrelated class lists in feature edits.

Sources: https://tailwindcss.com/docs/detecting-classes-in-source-files,
https://tailwindcss.com/docs/theme,
https://tailwindcss.com/docs/functions-and-directives,
https://ui.shadcn.com/docs/theming,
https://cva.style/docs,
https://github.com/dcastil/tailwind-merge/blob/main/docs/what-is-it-for.md,
https://evilmartians.com/chronicles/5-best-practices-for-preventing-chaos-in-tailwind-css
