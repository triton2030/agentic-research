# Verification And Tooling

Use when choosing checks, screenshots, visual regression, Tailwind/CSS tooling,
or closeout evidence.

## Reader Job

Prevent false confidence. CSS is done when rendered states are checked, not when
source looks plausible.

## Verification Layers

- **Static**: syntax, lint, class construction, formatting, contradictory
  classes.
- **Runtime**: rendered layout, overflow, focus, responsive, dark mode, assets.
- **Semantic**: hierarchy, scanability, visual consistency, variant API.

Project commands win. Do not invent a new stack during a styling task.

## Minimum Render Check

Scale checks to blast radius. For a tiny leaf tweak, one affected viewport/state
may be enough if the owner is local. For layout, responsive, reusable component,
or token changes, check:

- desktop viewport;
- mobile viewport;
- long content;
- hover/focus/disabled/loading if interactive;
- dark mode if present.

For reusable components, also test narrow parent/container. Viewport checks are
not enough. Do not build a screenshot matrix for an unrelated leaf edit.

## Useful Viewports

Use project standards first. If absent:

- 1440x900 desktop;
- 390x844 mobile;
- 320x720 narrow stress;
- 768x1024 tablet-ish;
- wide dashboard viewport when relevant.

## Visual Regression

Use Playwright screenshots when the repo already has Playwright or a local route
is easy to open:

```ts
await expect(page.getByTestId("summary-card")).toHaveScreenshot();
```

Good targets:

- design-system components;
- nav/shells;
- modals;
- data tables;
- marketing heroes;
- dashboards.

Avoid snapshots for unstable dynamic content unless masking or fixture control
exists.

Use Storybook/Chromatic when components already have stories and reviewable
visual diffs matter.

## Tooling Cues

- `prettier-plugin-tailwindcss`: class sorting, reduces diff noise.
- Tailwind source detection: check dynamic classes, ignored paths, monorepo base,
  third-party UI package scanning.
- ESLint Tailwind plugins: useful only when repo already owns the convention.
- Stylelint: useful for CSS-heavy repos or global CSS, less so for pure utility
  component repos.
- Build/CSS size checks: only when bundle size or production CSS is part of the
  failure.

## Closeout

Good:

```md
Changed: src/components/Button.tsx
Checked: npm run lint; screenshot 390x844 and 1440x900; hover/focus/disabled
Risk: no visual regression coverage for dark mode
```

If skipped, say why: no dev server, route needs auth, no browser tool, no story,
or no visual harness. Do not hide skipped rendering behind passing lint.

Sources:

- https://playwright.dev/docs/test-snapshots
- https://storybook.js.org/docs/writing-tests/visual-testing
- https://tailwindcss.com/docs/editor-setup
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://prettier.io/blog/2022/01/19/tailwindcss-plugin
