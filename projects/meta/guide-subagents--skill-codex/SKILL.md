---
name: guide-subagents
description: "Use when the user wants help preparing native Codex subagents before launch in chat. This skill is a guide and handoff helper: first decide whether delegation is actually worth it, separate the main agent's immediate next step from sidecar work, choose clear roles and ownership, write ready-to-send briefs for each subagent, show the launch plan in chat, and only then ask whether to call the subagents. Do not use this skill for automatic launches or vague multi-agent brainstorming."
---

# Guide Subagents (Codex)

Prepare native Codex subagents before launch.

This skill exists for one narrow moment: the user wants subagents to work through the Codex app, but the quality of the outcome depends on the prompts, boundaries, and launch plan being strong before any subagent is called.

This is a flexible skill. Keep the workflow, but adapt the role split and the briefs to the task.

## When to use

- The user explicitly wants subagents, delegation, or parallel work in Codex.
- The task has at least one meaningful sidecar workstream that can run in parallel.
- Better role split or better briefs would materially improve the result.
- The user wants to think through the subagents first and approve the launch in chat.

## When not to use

- The task is trivial, linear, or faster to do directly.
- The immediate next step is blocking and should be done locally first.
- The user wants only the main agent and does not want subagents.
- The work cannot be split into clean app-native sidecar streams.
- The subagents would duplicate each other because ownership cannot be separated cleanly.

## Hard gate

- Do not call native Codex subagents while running this skill.
- Do not substitute some other execution flow while presenting this as native subagent preparation.
- This skill prepares the launch plan and the briefs only.
- End with exactly one question: `Хотите, чтобы я вызвал субагентов?`
- Wait for the user's explicit reply before launching anything.

## Input context

Bring in only the context that changes delegation quality:

- the user's current task;
- the main agent's likely next local step;
- the candidate sidecar workstreams;
- the files, paths, or thread facts that matter for each subagent;
- any constraint that must not be broken.

If a fact would not change the role split, ownership, or brief, leave it out.

## Process

1. Capture the ask. Restate the task and why subagents might help now.
2. Split the work into `Main agent does now` and candidate sidecar workstreams. If no workstream is truly parallel-ready, say so plainly and do not force delegation.
3. Resolve only the unknowns that materially change the split, ownership, or evidence. Ask 1-3 questions only if the answer changes the plan. Otherwise record assumptions.
4. Shape the subagent set. Give each proposed subagent one role, one owned scope, and one useful return. Use [references/role-split-patterns.md](references/role-split-patterns.md).
5. Write one ready-to-send brief per subagent. Use [references/launch-brief-template.md](references/launch-brief-template.md).
6. Present the launch plan in the chat shape from [references/output-shape.md](references/output-shape.md).
7. Before sending, run the checks in [references/red-flags.md](references/red-flags.md).
8. End with exactly one question: `Хотите, чтобы я вызвал субагентов?` If you recommend no launch, say so in the plan but still end with that question.

## After approval

If the user explicitly says yes:

- Launch native Codex subagents only.
- Reuse the prepared briefs instead of improvising new ones.
- Start the main agent's local next step immediately while sidecar subagents run.
- Keep each coding worker on a disjoint write scope.

## Done when

- The local next step is named.
- Each proposed subagent has a distinct owned scope.
- Each brief asks for observable evidence, not confidence.
- Any load-bearing unknowns are either resolved or written as assumptions.
- The final line is `Хотите, чтобы я вызвал субагентов?`

## References

- [references/role-split-patterns.md](references/role-split-patterns.md)
- [references/launch-brief-template.md](references/launch-brief-template.md)
- [references/output-shape.md](references/output-shape.md)
- [references/red-flags.md](references/red-flags.md)
