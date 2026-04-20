---
name: playwright-guide
description: >
  Use when the task touches browser automation, live-page evidence collection,
  Playwright script authoring, UI-flow verification, or layout/design checks
  where the first job is to route work through already installed official
  Playwright skills instead of inventing a local browser workflow. This skill
  is a guide and router: choose between `$playwright`,
  `$playwright-interactive`, and adjacent review skills, expose only the
  context that changes the browser path, and gather evidence before judgment.
  Use for one-shot browser checks, persistent interactive debugging, section
  evidence capture, and algorithmic checks of spacing, block order, and visual
  weight. Do not use for pure code review or screenshot-only critique where a
  screenshot skill already fits directly.
---

# Playwright Guide

Flexible routing skill for browser and layout work in Codex.

This skill does not replace official installed Playwright skills. It decides which one to invoke, what context to expose, and when to hand the work off to a narrower visual-review skill.

## When to use

- The task needs real browser automation or live-page evidence
- It is unclear whether the work should go through `$playwright` or `$playwright-interactive`
- The user wants a Playwright script or test, but the evidence path should be chosen first
- The task is about spacing, hierarchy, grouping, block order, visual weight, or rendered layout logic
- A live page must be checked first and only then handed off into screenshot or section review

## When not to use

- The main evidence is already a screenshot and no live page is needed
- The request is pure code review or static CSS reasoning
- The user already explicitly invoked the exact official downstream skill and no routing help is needed
- The task has nothing to do with browser behavior, rendered UI, or Playwright-based checking

## Hard rules

- Prefer already installed official skills for browser execution
- Do not invent a parallel custom browser workflow if an official skill fits
- Load only the reference file for the current case, not the whole pack
- Gather evidence before verdicts
- If the job becomes screenshot-first, hand it off instead of forcing Playwright to stay in the loop

## Input context

Bring in only the facts that change routing quality:

- user goal
- URL, route, page, or dev server if known
- one-shot vs persistent investigation
- evidence needed on output
- whether the result should be a verdict, a handoff, or a Playwright script/test

If a fact would not change the skill choice, evidence plan, or output shape, leave it out.

## Workflow

1. Classify the task. Use [references/routing-matrix.md](references/routing-matrix.md).
2. Load only the relevant context pack from [references/context-packs.md](references/context-packs.md).
3. Choose the downstream skill:
   - one-shot browser pass -> `$playwright`
   - persistent live session -> `$playwright-interactive`
   - screenshot-first review -> `$screenshot-design`
   - captured section audit -> `$screenshot-design`
4. If the task stays in Playwright, load only one flow file:
   - `$playwright` path -> [references/live-flow.md](references/live-flow.md)
   - `$playwright-interactive` path -> [references/interactive-flow.md](references/interactive-flow.md)
5. If the task is about spacing, block order, grouping, or visual weight, load [references/layout-signals.md](references/layout-signals.md).
6. If the result should become a visual review instead of further browser work, use [references/design-audit-handoff.md](references/design-audit-handoff.md).
7. Before sending the final answer, run [references/red-flags.md](references/red-flags.md).

## Output logic

- If routing only: name the downstream skill and the evidence plan
- If evidence already exists: state what was collected before any larger conclusion
- If a script or test is requested: move to authoring only after the evidence path is clear
- If the task becomes review-shaped: separate evidence capture from judgment

## Done when

- The right downstream skill is chosen
- Only the needed context pack was loaded
- Evidence is separated from judgment
- Layout meaning is not inferred from one weak signal
- The next step is clear: execute, hand off, author script, or stop

## References

- [references/routing-matrix.md](references/routing-matrix.md)
- [references/context-packs.md](references/context-packs.md)
- [references/live-flow.md](references/live-flow.md)
- [references/interactive-flow.md](references/interactive-flow.md)
- [references/design-audit-handoff.md](references/design-audit-handoff.md)
- [references/layout-signals.md](references/layout-signals.md)
- [references/red-flags.md](references/red-flags.md)
