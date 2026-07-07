---
name: 1design-review
description: >
  Use after frontend implementation work is complete when Codex should inspect
  the live UI, write a curated screenshot plan, capture 2-3 related screenshots
  per group, then fan out many clean terminal design reviewers with progress
  tracking. Creates project-local `_workspace/design-review/` evidence. Skip
  blind auto-scroll audits, mid-implementation tweaks, Figma work, and technical
  browser QA that does not need visual design judgment.
---

# Design Review

## Outcome

Produce a design signoff from curated visual evidence:

- the main agent first inspects the page and decides which moments matter;
- screenshots are captured from a written `screenshot-plan.json`;
- optional `design-brief.md` gives reviewers a positive taste/character target;
- optional project-local comments ledger gives the aggregate reviewer iteration
  memory without contaminating clean focused reviewers;
- capture writes `capture-progress.md` and `capture-progress.json`;
- each plan group contains 2-3 related screenshots;
- multiple clean terminal Codex reviewers run in parallel by screenshot group
  and focused question lens;
- the reviewer runner writes `progress.md` and `progress.json` while agents run;
- a clean aggregate reviewer answers `questions.md` from focused review outputs.

The clean reviewers must not inherit chat history, project `AGENTS.md`, global
skills, source code, or the main agent's interpretation. They judge only the
attached screenshots, manifest, group context, and question contract.

## Default Path

1. Open the live page yourself before running the skill command. Inspect desktop
   and mobile, scroll through the important flow, and identify section starts,
   transitions, sticky-header edge cases, dense areas, and interaction states.
2. Write `<project>/_workspace/design-review/<label>/screenshot-plan.json`.
   Plan groups by judgment unit, not by scroll distance. Each group must contain
   2-3 related screenshots. For nontrivial pages, separate independent visual
   questions into separate groups; 4-8 groups is normal when the page has that
   much meaningful surface. Group purpose should name the visual question and,
   when known, the user's intended action or decision.
3. If this is a repeated pass or the project tracks reviewer comments, identify
   the project-local comments ledger and pass it with `--comments-ledger FILE`.
   Use a compact tracked owner when background worktrees must see it; keep
   long screenshot/run evidence in ignored workspace files.
4. If the design has a desired character beyond "clean and correct", write a
   short `<run-dir>/design-brief.md` or pass `--brief FILE`. Keep it concrete:
   audience, primary action, intended feeling, what must not be flattened, and
   2-4 creative/taste constraints. Skip it for ordinary utility checks.
5. Run:

   ```bash
   /path/to/1design-review/scripts/design-review \
     --url http://localhost:3000 \
     --project "$PWD" \
     --label design-pass \
     --comments-ledger _ops/design-review-agent-comments.md \
     --plan _workspace/design-review/design-pass/screenshot-plan.json
   ```

   Omit `--comments-ledger` when the project has no durable review-comment
   memory.
6. During capture, watch the terminal heartbeat or open `capture-progress.md`.
   If capture is slow, identify the running shot there before deciding whether
   to keep waiting, narrow the plan, or fix a selector/click.
7. While the agents run, watch the runner heartbeat or open `progress.md` in the
   run directory. Do not poll group logs by hand unless progress reports a
   failure or stall.
8. Read `design-review.md`, group logs, manifest, screenshot ledger, and
   `progress.md`. Report both the design verdict and whether the evidence plan
   was sufficient.

## Planning Rule

Do not let the script choose the page for you. The script executes the plan; the
main agent owns the plan.

A good group compares one visual question across adjacent or responsive states:

- first fold + bridge into next section;
- desktop section + mobile equivalent;
- dense component before/after scroll;
- sticky header edge + section anchor;
- closed state + opened state + settled state.

Do not make one group per whole page, per arbitrary viewport, or per every scroll
position. If you cannot name why 2-3 screenshots belong together, inspect the
page again before running the clean agents.

Do not collapse a broad page into one or two giant groups. Group count follows
the number of independent visual questions. The runner parallelizes those
groups; do not create artificial groups just to occupy reviewer slots.

Plan format: read `references/screenshot-plan-format.md` when writing or
debugging a plan.

## Workspace Rule

Keep all artifacts inside the reviewed project:

```text
<project>/_workspace/design-review/<timestamp-or-label>/
```

Do not scatter screenshots in the repository root, desktop, downloads, or the
skill folder. The skill folder is reusable tooling; `_workspace` is per-run
evidence.

## Command Modes

Plan-first review:

```bash
scripts/design-review --url URL --project PROJECT --plan PLAN_JSON [--brief BRIEF_MD]
```

Lightweight follow-up after fixes or for open ledger rows:

```bash
scripts/design-review \
  --url URL \
  --project PROJECT \
  --plan PLAN_JSON \
  --comments-ledger PROJECT_LEDGER.md \
  --questions /path/to/1design-review/references/follow-up-questions.md
```

Use follow-up mode for tight rechecks. Use the full `questions.md` fanout for
milestone signoff, broad redesign review, or when new surface area is being
judged.

Capture-only broad fallback:

```bash
scripts/design-review --auto-capture --capture-only --url URL --project PROJECT
```

Use broad auto-capture only to explore or debug the capture machinery. Do not
use it for final clean design judgment.

## Clean Agent Fanout

Before launching clean reviewers, check `capture-progress.md` and `manifest.json`.
If planned shots failed or the captured files do not match the intended moments,
fix the plan and rerun capture. Do not ask reviewers to judge incomplete or
mis-targeted evidence.

`scripts/run-clean-design-agent.sh` prepares `group-reviews/<task-id>/` and
starts multiple `codex exec` reviewers with `--parallel 6` by default. It splits
`questions.md` into focused, non-synthetic design lenses, then runs those lenses
against each 2-3 screenshot group. Verdict and fix recommendations are aggregate
only because they synthesize the focused reviewers instead of owning a separate
visual lens. This is intentionally more expensive than asking one reviewer to
answer the whole question list, but it preserves judgment quality. After focused
reviewers finish, an aggregate clean reviewer answers the full `questions.md`
from their outputs.

Each focused reviewer sees:

- only one screenshot group;
- only one focused question lens;
- optional design brief content when `--brief FILE` is passed or
  `<run-dir>/design-brief.md` exists;
- enough group context to ground findings in screenshot ids/files.

The runner writes:

- `progress.md` for human-readable waiting and handoff;
- `progress.json` for scripts/tools;
- heartbeat lines every `--progress-interval` seconds, default `10`.

Use those progress files instead of repeatedly checking each group log. If a
run is slow, the main agent should keep waiting while `progress.md` shows
running reviewers. Investigate only failed groups, missing outputs, or a stale
heartbeat.

If any focused reviewer fails, stop and report the failed task and log path. Do
not silently merge partial reviews into a final verdict.

## Iteration Memory

Clean focused reviewers are stateless by design. They must not inherit previous
review passes, accepted fixes, rejected comments, implementation progress, or
project code.

The main agent owns iteration memory. For repeated passes on the same surface,
use a project-local comments ledger with only durable decisions: issue, source
run/screenshot, decision, reason, and the next evidence gate. Keep it
project-independent in shape: ids and statuses are fine; project-specific design
law belongs to that project's own design skill or instructions.

Pass the ledger with `--comments-ledger FILE`. The runner sends it only to the
aggregate reviewer, not the focused reviewers. The aggregate must map findings
to existing rows, mark repeated closed/deferred/routed comments as non-work
unless fresh screenshot evidence contradicts the row, and propose new row
candidates instead of turning every reviewer sentence into a UI patch.

Do not rely on reviewer repetition as progress tracking. If reviewers keep
rediscovering the same class of issue, stop the loop and decide whether the row
is fixed, rejected, deferred, routed, or still a real blocker. A
`needs-final-pass` row should shape the next curated screenshot plan, not trigger
blind micro-edits.

## Clean Runtime Boundary

Each terminal reviewer uses a temporary `CODEX_HOME`, links only
`~/.codex/auth.json`, unsets API-key environment variables, runs from a neutral
temporary cwd, passes `--ignore-user-config`, `--ignore-rules`, `--ephemeral`,
and attaches only the group's screenshots.

If source-code access is needed, run a separate technical review. Do not widen
this design review into a code reviewer.

## Validation

Before trusting changes to this skill package:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /path/to/1design-review

/path/to/1design-review/scripts/design-review --help
/path/to/1design-review/scripts/run-clean-design-agent.sh --help
node --check /path/to/1design-review/scripts/capture-design-screenshots.mjs
node --check /path/to/1design-review/scripts/design-review-progress.mjs
node --check /path/to/1design-review/scripts/prepare-design-review-groups.mjs
```

For a real frontend, verify:

- the plan has 2-3 shots per group;
- captured screenshots match the intended moments;
- `capture-progress.md` reached `complete` or clearly names the stuck/failed
  planned shot;
- every focused review task produced a review;
- `progress.md` reached `complete` or clearly names the failed stage;
- the aggregate explicitly names uncovered questions.
- follow-up runs use `references/follow-up-questions.md` only when the reviewed
  surface is already narrowed by ledger rows or a specific post-fix question.

## Stop

Use this near the end of frontend programming work. Do not run it between every
small CSS edit unless the user explicitly asks for a visual checkpoint.
