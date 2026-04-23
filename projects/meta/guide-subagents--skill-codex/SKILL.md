---
name: guide-subagents
description: >
  Use when the user explicitly wants Codex subagents or parallel delegation and the
  result depends on a clean split, strong briefs, and disciplined integration
  afterward. Decide whether delegation is worth it, keep the main agent on
  blocking or integration work, assign workers only disjoint clean scopes, and
  verify returned work on disk before trusting status reports. Do not use for
  vague multi-agent brainstorming, for work that is faster to do locally, or
  when ownership cannot be separated cleanly.
---

# Guide Subagents (Codex)

Prepare, launch, receive, and integrate native Codex subagents when delegation is genuinely the best execution path.

This skill is execution hygiene for native Codex subagents. It sits downstream of strategy, architecture, and task-criteria owners. Do not let it compensate for missing plan or missing scope decisions upstream.

## Upstream gate

If any of these are unresolved, do not force delegation yet:

- missing durable goal, plan, or user-preference context -> `main-strategy`;
- unresolved control-surface, folder ownership, or where a guardrail belongs -> `system-architect`;
- unresolved task-level acceptance criteria or proof boundary -> `task-planner`.

## When to use

- The user explicitly wants subagents, delegation, or parallel work in Codex.
- The task has at least one real sidecar stream that can run without blocking the main agent's next move.
- Better role split or better briefs would materially improve the result.
- Fresh-context validation, evidence collection, or leaf implementation can run in parallel while the main agent keeps the critical path moving.

## When not to use

- The task is trivial, linear, or faster to do directly.
- The main agent's immediate next step is the critical path and there is no real sidecar work.
- The user wants only the main agent and does not want delegation.
- Ownership cannot be separated cleanly.
- The split would require multiple workers to touch the same hotspot or integration surface.

## Hard gate

- Use native Codex subagents only.
- Do not present this as a philosophy brainstorm. It is a launch-and-integration helper.
- Do not force a confirmation pause just because subagents are involved.
- If the user explicitly asks to inspect or approve the split first, switch to plan-first mode for that turn and do not auto-launch.
- If delegation is not warranted, say so briefly and continue locally.
- Do not trust status updates as truth; truth comes from on-disk changes and real verification.

## Launch mechanics

- Reuse prepared briefs when the split is still valid; do not improvise a different split at launch time.
- If launch uses `fork_context=true`, do not override `agent_type`, `model`, or `reasoning_effort` unless the user explicitly asked for a different agent shape. This is a native Codex gotcha.
- Keep launch parameters minimal. Only set what materially changes the worker's job.
- Keep each coding worker on a disjoint write scope.

## Split discipline

Before assigning any worker, check the candidate files and workstreams.

Keep with the main agent:

- the immediate blocking next step;
- integration surfaces and cross-worker join points;
- hotspot files that many changes converge through;
- files that are already dirty or mix old diff with new work;
- repo-level verification after integration.

Prefer for workers:

- clean leaf files;
- new files;
- isolated module slices;
- one narrow question or one disjoint write scope.

Dirty worktree gate:

- Do not hand a worker a file that is already dirty unless the brief explicitly says it is dirty and the worker's task is limited to a clearly separable delta.
- If the file mixes preexisting edits with the new task, keep it with the main agent or find a cleaner leaf split.

## Briefing stance

Bias briefs toward:

- role;
- owned scope;
- task;
- role behavior and stance;
- work boundaries;
- quality criteria;
- evidence required;
- report discipline.

Default brief shape is: `role + owned task + work boundaries + quality criteria + evidence + report discipline`.

Do not give subagents a rigid algorithm by default. The brief should tell them what job they own, what stance to keep, what they may or may not do, and what counts as high-quality completion. Add ordered steps only when sequence is truly load-bearing, safety-critical, or the task is fragile enough that a free-form approach would predictably fail.

Every worker brief must make these boundaries explicit:

- report only owned scope;
- do not summarize adjacent workers;
- do not launch more subagents;
- do not comment on launcher or tool availability unless it blocks the owned task;
- if an owned file was already dirty before the worker edited it, say so explicitly and describe only the worker's delta.

Use [references/launch-brief-template.md](references/launch-brief-template.md) and [references/role-split-patterns.md](references/role-split-patterns.md).

## Output discipline

Scope discipline is mandatory. Brevity is not universal.

- A worker must report only its owned scope.
- The length and format of the return should fit the deliverable.
- For coding workers, concise scoped deltas are usually best.
- For strategist, writer, marketer, researcher, or business-analysis workers, a substantive answer in chat can be the correct deliverable if that is what the brief asked for.
- Do not force every worker into a short status-note shape when the real owned deliverable is a memo, critique, options analysis, or structured recommendation.
- Do not let a worker use "full analysis" as an excuse to drift into adjacent scopes.

## Current-reality signal

If the repo has a real current-reality artifact and it changes delegation quality, read it before splitting the work. `_state/YYYY-MM-DD-state.md` is only one possible example, not a required input.

Use such a snapshot only as read-only evidence of what still matters now. Do not let it replace `_ops/`, task criteria, or ownership.

## Process

1. Capture the ask and name the main agent's immediate next step.
2. Check whether any upstream owner layer is unresolved. If so, route there before launching workers.
3. Inspect candidate scopes for dirty files, hotspots, and integration surfaces.
4. Split the work into `Main agent does now` and real sidecar streams. If there is no true parallel-ready sidecar, do not force delegation.
5. Write one ready-to-send brief per worker. Make the owned scope, owned task, work boundaries, quality criteria, and report discipline unambiguous.
6. Decide mode:
   - `default launch mode`: delegation is warranted and the split is clear, so launch native Codex subagents;
   - `plan-first mode`: only when the user explicitly asked to inspect or approve the split before launch;
   - `no-launch mode`: delegation is not worth it, so continue locally.
7. After workers return, inspect the on-disk diff for each owned scope before trusting any status message.
8. Integrate locally. The main agent owns cross-scope joins, conflict resolution, and hotspot updates.
9. Run verification at the right level:
   - workers may report only scoped checks tied to their owned files or owned question;
   - the main agent owns repo-level `lint`, `tsc`, Playwright, browser truth, and other integration checks after the changes are merged.
10. If verification is mixed, separate `scope truth` from `preexisting unrelated failures` instead of collapsing them into one verdict.
11. Before finishing, run the checks in [references/red-flags.md](references/red-flags.md).

## Plan-first mode

In plan-first mode:

- show the split and worker briefs in chat;
- do not auto-launch until the user clearly asks to proceed.

Use the compact shape in [references/output-shape.md](references/output-shape.md). Keep full briefs internal unless the user explicitly wants to inspect them.

## Done when

- The main agent's local next step is named.
- Worker scopes are disjoint and preferably clean.
- Launch parameters do not accidentally trigger native Codex gotchas.
- Each brief defines role, owned task, work boundaries, quality criteria, report discipline, and evidence.
- Returned work is verified on disk before it is trusted.
- Repo-level verification is done by the main agent after integration.
- Any unrelated preexisting failures are separated from the truth about the delegated scope.
