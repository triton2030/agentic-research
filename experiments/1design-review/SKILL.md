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
   much meaningful surface.
3. Run:

   ```bash
   /path/to/1design-review/scripts/design-review \
     --url http://localhost:3000 \
     --project "$PWD" \
     --label design-pass \
     --plan _workspace/design-review/design-pass/screenshot-plan.json
   ```

4. During capture, watch the terminal heartbeat or open `capture-progress.md`.
   If capture is slow, identify the running shot there before deciding whether
   to keep waiting, narrow the plan, or fix a selector/click.
5. While the agents run, watch the runner heartbeat or open `progress.md` in the
   run directory. Do not poll group logs by hand unless progress reports a
   failure or stall.
6. Read `design-review.md`, group logs, manifest, screenshot ledger, and
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
scripts/design-review --url URL --project PROJECT --plan PLAN_JSON
```

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
`questions.md` into focused design lenses, then runs those lenses against each
2-3 screenshot group. This is intentionally more expensive than asking one
reviewer to answer the whole question list, but it preserves judgment quality.
After focused reviewers finish, an aggregate clean reviewer answers the full
`questions.md` from their outputs.

Each focused reviewer sees:

- only one screenshot group;
- only one focused question lens;
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

## Stop

Use this near the end of frontend programming work. Do not run it between every
small CSS edit unless the user explicitly asks for a visual checkpoint.
