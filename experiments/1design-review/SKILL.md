---
name: 1design-review
description: >
  After frontend implementation, inspect the live UI and produce a
  screenshot-grounded design verdict. Use clean reviewer fanout only for an
  explicit request, milestone signoff, or high-risk redesign. Not browser QA.
---

# Design Review

## Outcome

Produce an evidence-backed visual verdict: what holds, what blocks signoff, and
which rendered states support that judgment. The main agent owns the normal
review. Independent clean reviewers are an escalation path, not the default.

## Default: Main-Agent Review

1. Open the live UI and inspect the important flow at the viewports and states
   that can change the verdict. Prefer the smallest sufficient screenshot set.
2. Judge the rendered result, not only DOM or source: hierarchy, composition,
   typography, spacing, responsive behavior, interaction states, accessibility
   cues, and fit with the product/design context.
3. Report prioritized findings tied to concrete screenshots or states. Include
   what works, evidence gaps, and whether the surface is ready to sign off.
4. Stop when the verdict is supported or when a specific missing state blocks
   judgment. Do not create reviewer fanout merely because the page is large.

Use the existing browser or screenshot tooling directly for an ordinary pass.
If repeatable capture is useful, write a plan and run capture-only mode:

```bash
scripts/design-review \
  --capture-only \
  --url URL \
  --project PROJECT \
  --plan PLAN_JSON
```

## Escalate to Clean Reviewers When

- the user explicitly asks for independent reviewers or fresh eyes;
- this is milestone, release, or final design signoff;
- a broad or high-risk redesign benefits from independent visual lenses;
- the main-agent verdict remains genuinely ambiguous after inspecting the
  relevant states.

For a narrow post-fix check, stay with the main agent unless independence is the
point of the request.

## Curated Evidence for Fanout

Before launching clean reviewers, inspect the page yourself and write:

```text
<project>/_workspace/design-review/<label>/screenshot-plan.json
```

Plan by independent visual question, not scroll distance or reviewer capacity.
Each group should contain 2-3 related screenshots. Use only as many groups as the
decision needs; there is no target group count. A useful group might compare:

- first fold and transition into the next section;
- desktop state and its mobile equivalent;
- closed, opened, and settled interaction states;
- a dense component before and after scroll;
- sticky-header behavior at a section boundary.

Read `references/screenshot-plan-format.md` when writing or debugging the plan.
Check `capture-progress.md` and `manifest.json` before review; fix missing or
mis-targeted captures rather than asking reviewers to judge incomplete evidence.

Optional inputs:

- `design-brief.md` or `--brief FILE` for audience, primary action, intended
  character, and concrete taste constraints;
- `--comments-ledger FILE` for durable iteration decisions. The ledger goes only
  to the aggregate reviewer, never to focused clean reviewers.

## Fanout Command

```bash
scripts/design-review \
  --url URL \
  --project PROJECT \
  --plan PLAN_JSON \
  [--brief BRIEF_MD] \
  [--comments-ledger PROJECT_LEDGER.md] \
  [--parallel N]
```

The runner defaults to three concurrent focused reviewers. Raise concurrency
only when the evidence groups are independent and the runtime budget justifies
it. For a focused milestone follow-up, pass
`references/follow-up-questions.md`; use the full `questions.md` only when the
whole review contract matters.

While agents run, use `progress.md` or `progress.json` instead of polling every
log. If a focused reviewer fails, report the failed task and log path; do not
silently aggregate partial work.

## Clean-Room Contract

Focused reviewers see only one screenshot group, one question lens, optional
design-brief content, and enough manifest context to identify the evidence. They
must not inherit chat history, project instructions, global skills, source code,
or the main agent's interpretation. A separate clean aggregate reviewer combines
their outputs and, when provided, the iteration ledger.

The runner enforces this with a temporary `CODEX_HOME`, linked auth only,
neutral cwd, ignored user config/rules, ephemeral execution, and screenshot-only
attachments. If source access is needed, run a separate technical review.

## Workspace and Stop

Keep run artifacts under:

```text
<project>/_workspace/design-review/<timestamp-or-label>/
```

Do not scatter screenshots in the repository root, desktop, downloads, or the
skill folder. Use this near the end of frontend work or at an explicit visual
checkpoint, not between routine CSS edits.

## Validation

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /path/to/1design-review

scripts/design-review --help
scripts/run-clean-design-agent.sh --help
node --check scripts/capture-design-screenshots.mjs
node --check scripts/design-review-progress.mjs
node --check scripts/prepare-design-review-groups.mjs
```

For a live fanout, verify that captured files match the plan, all focused tasks
produced outputs, progress reached a terminal state, and the aggregate names any
uncovered questions.
