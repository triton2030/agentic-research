---
name: 1tailwind-dev
description: >
  Автоматически активируй при любой frontend design/implementation работе до
  создания или правки component/theme/style source: переиспользуй current
  owners и Tailwind/framework-native vocabulary, иначе агент изобретает
  параллельные tokens/components/styles. Не для critique без перехода к коду.
---

# Tailwind Dev

## Result

New or continued frontend work starts from the smallest current visual
vocabulary and owner set. New names follow the most familiar exact-fitting
Tailwind or installed-framework convention, so their role is legible without a
private glossary. The requested result then uses the least new CSS, classes,
components, tokens, wrappers, and variants that remain inspectable and
verifiable.

## Two Modes

### New Build

For a new site, page, dashboard, or frontend surface, activate before
scaffolding components or writing JSX/CSS/theme code. Inspect the brief,
references, and any existing project setup, then choose only the visual roles
the current UI needs.

### Existing Frontend

Before the first source edit of the current work session, inspect the rendered
state and existing tokens, components, variants, and style owners. Extend or
consolidate them; do not start a parallel visual system. A leaf fix may skip the
full vocabulary inventory once its current owner is obvious.

## Pre-code Gate

Before writing code, name the mode, observable result, existing reuse, smallest
needed vocabulary, and component/style owners. Keep this in working context;
do not create a planning or design-system document unless requested.

For a new or broad UI, bound the vocabulary before implementation:

- typography roles and font families;
- color roles, spacing/gaps, radii, and surfaces actually used;
- stable repeated UI objects and their finite states/variants;
- true one-offs that should stay local rather than become tokens.

Before adding vocabulary, run the naming gate:

1. Keep the existing project's established owners and terms.
2. Otherwise use Tailwind's official utility vocabulary, theme namespaces, and
   default scale names.
3. Then use an already installed component framework's exact semantic roles.
4. Invent the smallest local role only when a familiar name would misstate it.

Do not rename established vocabulary unless migration is explicitly in scope.
Use only the small current subset. Prefer one font family; add a second family
or another scale step only for a distinct current role.

## Work Path

1. Select `New Build` or `Existing Frontend` and pass the pre-code gate before
   the first source edit.
2. Classify each style owner: token, layout/composition,
   component/block, variant/exception, or global override.
3. Run the code-budget gate: can this be solved by using the selected Tailwind
   scale, deleting a conflict, reusing a current component/token/variant,
   changing one owner, or relying on intrinsic layout?
4. Create a shared component only for a stable repeated UI object. Repeated
   values become tokens only when they carry a repeated design role; keep true
   one-offs local.
5. Implement with static Tailwind class strings. Map props to complete classes;
   do not build class names with string interpolation.
6. Inspect the rendered UI. Check relevant desktop/mobile, long-content,
   hover/focus/disabled/loading, dark-mode, and overflow states.
7. Run a consolidation/delete pass: collapse near-duplicate values and remove
   conflicting utilities, redundant wrappers, stale variants, unused tokens,
   and override patches.

## Reference Routes

- Read `references/agent-css-method.md` when the task is broad, ambiguous, or
  risks creating style debt.
- Read `references/tailwind-patterns.md` when editing className logic, variants,
  tokens, Tailwind v4 theme CSS, `@apply`, `@utility`, `clsx`, `cva`, or
  `tailwind-merge`.
- Read `references/defensive-layout.md` when fixing layout, overflow,
  responsive behavior, long content, flex/grid, container queries, or sticky /
  scroll issues.
- Read `references/verification.md` when choosing checks, browser screenshots,
  visual regression, lint/format tooling, or closeout evidence.

## Guardrails

- Do not begin a new or broad frontend by generating a comprehensive token,
  primitive, component, or utility layer.
- Do not mirror Tailwind's type, spacing, radius, or color scales into custom
  variables. Add a semantic token only for a distinct repeated current role.
- Do not create a component because a class list is long or future reuse seems
  plausible; require a stable repeated UI object in the current scope.
- Do not fix CSS by stacking another override before identifying the owner.
- Do not add `!important`, ID selectors, deep descendant selectors, or global
  rules unless the target is third-party/unowned markup or a deliberate base
  layer.
- Do not use `className` as an unlimited escape hatch for reusable components;
  prefer named `variant`, `size`, `tone`, `density`, and `state`.
- Do not add a new token, variant, wrapper, breakpoint, utility, animation, or
  state matrix unless an existing owner cannot express the current requirement.
- Do not accept visual green from source reading only. Render or screenshot when
  the task changes layout, spacing, color, motion, or responsive behavior.

## Closeout

Include at least these facts; add concise rationale or caveats when they are
material to understanding the visual decision or its limits:

```md
Changed: <paths>
Checked: <commands/screenshots/viewports>
Risk: <remaining visual/style risk or none>
```
