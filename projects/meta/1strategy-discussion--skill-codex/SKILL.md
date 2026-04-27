---
name: 1strategy-discussion
description: >
  Use before planning or execution when the user brings a raw desire, uncertain
  start, new branch, risky framing, or proposed approach with hidden tradeoffs:
  "хочу сделать", "думаю про", "не знаю как", "какой подход выбрать",
  "появилась развилка", "давай обсудим стратегию", "raw desire",
  "what should I do", "which approach". Run an expert strategy discussion:
  name the useful expertise, explain how that expert would understand the
  question, reveal approach branches with cost/risk/tradeoffs, ask only
  consequential domain questions, capture durable user-truth candidates, then
  route to `project-strategy`, `1task-contract`, `user-truth`, `1before-work`, or
  execute. Skip trivial edits, typo fixes, pure code review, status-only project
  continuation, and stable active-task execution.
---

# Strategy Discussion

## Role

Hold the expert conversation before a wish becomes a plan or task.

Respect the user's goal, but do not accept the proposed method as the task. The
user may not know the domain, options, risks, or questions that matter. Your job
is to surface the missing professional knowledge at the right depth for the
decision currently being made.

This skill does not write code, execute work, or own project roadmap. It owns
only lightweight branch memory when a decision, rejected route, hypothesis, or
constraint will affect a future decision.

## Planning Boundary

This skill runs before the planning layer is chosen. It reveals the decision
and routes it to the owner: `project-strategy` for direction, `1task-contract`
for task scope, or `1before-work` when execution can start.

Do not maintain a competing planning map here. The canonical level contract
lives with `project-strategy`; this skill only decides which owner should receive
the selected route.

## Trigger Gate

First decide from the current user message, before reading project state:

- If there is a raw desire, uncertainty, new reality signal, risky proposed
  method, or unresolved approach choice, continue.
- If the message is only "continue", project status, a stable active task,
  a typo, pure review, or execution inside already chosen scope, skip silently.

Do not read `_ops` to manufacture a trigger. Project state is context, not the
source of this discussion.

## First Read

After the gate passes, read only what exists and only what changes this turn:

- `_ops/PROJECT-ROADMAP.md` for Goal, Approach, Stages, Anti-goals.
- `_ops/INTERVIEW.md` for durable user truth that changes scope, tone, or risk.
- `_ops/STRATEGY-DISCUSSION.md` for selected, rejected, deferred, and revisit
  routes already recorded.

## Workflow

1. Name the expert perspective that would help now, including the relevant
   experience and knowledge. This is a temporary lens, not a persona or team.
2. Say how that expert would understand the user's question, correcting hidden
   assumptions without losing the user's goal.
3. Reveal 2-4 meaningful approach branches with rough time, complexity, risk,
   future constraints, and cheaper ways to preserve the same business effect.
4. Ask at most 1-3 consequential questions. Ask only if different answers change
   strategy, scope, criteria, architecture, or verification. Otherwise take a
   position and name the assumption.
5. If a route is selected, name rejected or deferred routes and when to revisit
   them. A rejected route matters only if it could change a future decision.
6. Route next:
   - Goal, Approach, Stage, trajectory, or Anti-goal should be written ->
     `project-strategy`.
   - Durable user preference, constraint, red line, tone, or success picture
     should be saved -> `user-truth`.
   - Scope is stable enough for task criteria -> `1task-contract`.
   - Implementation path is stable and work may start -> `1before-work`.

## Depth Rule

Extract only as much domain knowledge as the current decision needs.

Do not dive into implementation details before the nature, goal, and approach
are clear. Do not stay abstract once the useful decision is implementation path,
task scope, or next reality check.

## Memory

If a decision will matter later, create `_ops/` if needed and append to
`_ops/STRATEGY-DISCUSSION.md`. Record only load-bearing state:

```md
## YYYY-MM-DD - <short topic>

**Selected route:** <chosen approach or "none yet">
**Rejected / deferred routes:**
- <route> - <why not now>. Revisit if <condition>.

**Working hypothesis:** <assumption still unproven>
**Constraint:** <must not violate, if any>
**Routes to:** <project-strategy | user-truth | 1task-contract | 1before-work | execute>

---
```

Do not write transcript, status report, or nice-to-have analysis.

## Output Shape

Prefer natural conversation. The useful content must appear before any receipt:

- Expert needed: <who/experience/knowledge>
- Expert read: <how they would understand the user's real question>
- Branches: <options with cost/risk/tradeoffs>
- Key questions: <only consequential questions>
- Selected/deferred routes: <if decided>
- Next route: <owner skill or action>

## Done When

The user has seen at least one branch, risk, expert question, or cheaper route
that was not explicit in the original ask, and the next owner/action is clear.
