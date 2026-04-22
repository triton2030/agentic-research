---
name: guide-subagents
description: "Use when the user wants Codex subagents or parallel delegation. Decide whether delegation is actually worth it, separate the main agent's immediate next step from sidecar work, choose clear roles and ownership, use `_state/YYYY-MM-DD-state.md` as read-only current-reality signal when present, write launch-ready briefs, and by default launch native Codex subagents directly when the split is clear. Do not use this skill for vague multi-agent brainstorming or for work that is faster to do directly."
---

# Guide Subagents (Codex)

Prepare and launch native Codex subagents when delegation is worth it.

This skill exists for one narrow moment: the user wants subagents to work through the Codex app, but the quality of the outcome depends on the prompts, boundaries, and launch plan being strong before any subagent is called.

This is a flexible skill. Keep the workflow, but adapt the role split and the briefs to the task.

## Briefing stance

Bias the subagent briefs toward:

- role;
- behavior and stance;
- owned scope;
- success criteria;
- evidence required.

Do not default to step-by-step instructions for each subagent. A brittle procedural brief often makes the subagent narrower in the wrong way and weakens judgment.

Add ordered steps only when sequence is load-bearing, safety-critical, or the task would otherwise become ambiguous.

## Special role: trajectory auditor

When the user wants a subagent to audit alignment rather than produce new work, use [references/trajectory-auditor.md](references/trajectory-auditor.md).

This role is read-only and evidence-first: it checks the current trajectory against `_ops`, active criteria, the relevant instruction files, and only the skill contracts actually in play.

Keep it outside the default owner-chain. Its job is to return `aligned` / `drift` / `unknown` plus the next best owner layer, not to replace `system-architect` or `criteria-generator`.

## State-aware splitting

If `_state/YYYY-MM-DD-state.md` exists, read it before you split the work.

Use `_state/` only as a read-only current-reality layer:

- which North Star criteria are still `in progress`;
- which strategic lines are compliant but still not producing enough real progress;
- what remaining gap makes delegation useful **now**, not in theory.

Do not treat `_state/` as strategy ownership, and do not let it override `_ops/`. `_ops/` says what the bet is; `_state/` says how far reality still is from that bet.

## When to use

- The user explicitly wants subagents, delegation, or parallel work in Codex.
- The task has at least one meaningful sidecar workstream that can run in parallel.
- Better role split or better briefs would materially improve the result.
- The user wants to think through the subagents first, even if launch may still happen later in the same turn.

## When not to use

- The task is trivial, linear, or faster to do directly.
- The immediate next step is blocking and should be done locally first.
- The user wants only the main agent and does not want subagents.
- The work cannot be split into clean app-native sidecar streams.
- The subagents would duplicate each other because ownership cannot be separated cleanly.
- The immediately previous turn already produced a launch plan from this skill and the user is now explicitly approving that plan or asking to execute it. In that case, do not rerun this skill; launch the prepared native Codex subagents directly.

## Hard gate

- Do not substitute some other execution flow while presenting this as native subagent preparation.
- Do not force a confirmation checkpoint just because subagents are involved.
- Do not dump the full launch plan or every launch brief into chat unless the user explicitly asked to inspect the split first.
- If delegation is warranted and the split is clear, launch native Codex subagents directly.
- If delegation is not warranted, say so briefly and continue locally.
- If the user explicitly asks for plan-first review or approval before launch, switch to plan-first mode for that turn and do not auto-launch.

## Input context

Bring in only the context that changes delegation quality:

- the user's current task;
- the main agent's likely next local step;
- the candidate sidecar workstreams;
- the current `_state/` signal, if it changes what is actually worth delegating now;
- the files, paths, or thread facts that matter for each subagent;
- any constraint that must not be broken.

If a fact would not change the role split, ownership, or brief, leave it out.

## Process

1. Capture the ask. Restate the task and why subagents might help now.
2. Check current state. If `_state/YYYY-MM-DD-state.md` exists, extract only the lines that change delegation quality: criteria still `in progress`, remaining gaps, or clean strategy compliance that still has no substantive artifact behind it.
3. Split the work into `Main agent does now` and candidate sidecar workstreams. If no workstream is truly parallel-ready, say so plainly and do not force delegation.
4. Use `_state/` to bias the split: the main agent should usually keep the most immediate blocking move, while subagents should target independent remaining gaps, fresh evidence sweeps, or independent checks that the snapshot says still matter.
5. Resolve only the unknowns that materially change the split, ownership, or evidence. Ask 1-3 questions only if the answer changes the plan. Otherwise record assumptions.
6. Shape the subagent set. Give each proposed subagent one role, one owned scope, and one useful return. Use [references/role-split-patterns.md](references/role-split-patterns.md).
7. Write one ready-to-send brief per subagent. Use [references/launch-brief-template.md](references/launch-brief-template.md). Prefer role, stance, criteria, and evidence over procedural micromanagement.
8. Decide mode:
   - `default launch mode`: if delegation is warranted and the split is clear, launch native Codex subagents immediately;
   - `plan-first mode`: only if the user explicitly asked to inspect or approve the split before launch;
   - `no-launch mode`: if delegation is not worth it, continue locally.
9. Use the compact chat shape from [references/output-shape.md](references/output-shape.md). Keep full briefs internal by default. Paste them into chat only in `plan-first mode` or when a boundary decision truly needs visibility.
10. Before finishing, run the checks in [references/red-flags.md](references/red-flags.md).

## Launch behavior

In default launch mode:

- Launch native Codex subagents only.
- Reuse the prepared briefs instead of improvising new ones.
- Start the main agent's local next step immediately while sidecar subagents run.
- Keep each coding worker on a disjoint write scope.

In plan-first mode:

- Present the split and briefs in chat.
- Do not auto-launch in that turn unless the user then clearly asks to proceed.

If a previous turn already produced a launch plan and the user now says "execute this plan", "use this scheme", or equivalent explicit handoff with no material change in ask, do not re-prepare; launch.

## Done when

- The local next step is named.
- The launch plan reflects current `_state/` when that snapshot exists and materially changes what should be delegated.
- Each proposed subagent has a distinct owned scope.
- Each brief is driven by role, behavior, and success criteria rather than a brittle step list.
- Each brief asks for observable evidence, not confidence.
- Any load-bearing unknowns are either resolved or written as assumptions.
- If subagents are warranted and the user did not explicitly request plan-first review, they are launched without a forced confirmation pause.
- User-facing chat output stays compact unless the user explicitly asks to inspect the split.

## References

- [references/role-split-patterns.md](references/role-split-patterns.md)
- [references/launch-brief-template.md](references/launch-brief-template.md)
- [references/output-shape.md](references/output-shape.md)
- [references/trajectory-auditor.md](references/trajectory-auditor.md)
- [references/red-flags.md](references/red-flags.md)
