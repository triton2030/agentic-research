---
name: 1handoff
description: >-
  Use when $1handoff or /1handoff is requested, or when long repository work
  must move to a fresh session before continuation-critical state is lost. Not
  for summaries, final reports, file transfer, or a second handoff in the same
  chat.
---

# Handoff

Close one repository work session as a reliable bridge to a fresh agent. The
closeout has three independent outcomes: `1chat-recall` preserves qualifying
owner evidence under its own contract, affected management state is current or
explicitly unresolved, and a dated packet in `_ops/handoffs/` preserves the
action-changing session delta.

## Goal

With only the repository and the explicit packet path, a fresh agent can begin
the correct next action for the right reason, inherit current project state,
and avoid paid mistakes or disproved mental models from this session.

Choose whatever means are necessary to make that outcome true within the
active task's existing authority and the project's rules. Named means and
examples are non-exhaustive; explicit boundaries and the packet contract remain
required. This skill grants no new permission: resolve what current authority
allows and anchor the rest with its consequence.

## Boundaries

- Create no more than one handoff in a chat.
- Return the exact packet path for manual delivery. Do not add a latest-handoff
  index, hook, automatic discovery, consumed state, or another lifecycle
  surface.
- Treat the packet as a dated delta, never as live truth. It is not a
  transcript, summary, task plan, user profile, or project canon. Live files
  and runtime state override it.
- Resolve owner evidence through `1chat-recall` under its own contract. Never
  imitate recall inside the packet.
- Follow the owning contract for every managed surface. Change only state made
  stale or unsafe by this session and already within the active task's
  authority; hand off everything else with an exact anchor.
- Outside an owning contract, change only project-authorized state recoverable
  in one Git operation. Anchor irreversible, veto-class, or approval-dependent
  work instead of treating closeout as permission.
- Record the actual running model with a short, honest identifier. Do not
  invent a subversion.

## Required State Before Delivery

Recall and project-state outcomes must exist before the packet records them;
consumer evidence must exist before the path is returned. Within that causal
order, derive the work from the goal.

### Owner Evidence

Qualifying owner decisions and corrections have a `1chat-recall` outcome. If
recall is unavailable or blocked, preserve the independent packet outcome and
state the exact reason. Represent owner evidence in the packet only by its
recall address plus one line explaining how it changes continuation.
If recall provides no address for continuation-changing owner evidence, expose
`no recall address` separately as a continuation blocker with its consequence;
do not relabel recall's own outcome.

### Project State

Leave every management owner affected by this session current, or expose its
exact unresolved state and consequence. The management layer includes plans
and status, findings, paid-search INDEX routes, instructions and documentation,
Git, and temporary state; this list does not limit the outcome. Do not audit or
improve unrelated project state.

A recurring paid lesson does not remain another advice item. Before delivery,
it has an authorized decision-time guardrail at the correct owner, or a finding
that anchors why the guardrail could not be installed.

### Continuation Delta

Preserve any current-session fact, choice, failure, or observation whose loss
could change the next action, decision, veto, risk, or repeat a paid mistake.
Omit everything else. When live state can recover the information, prefer one
exact address and why it matters over a copied explanation. Preserve material
causal history as:

`initial model or action -> evidence or result -> resulting model`

## Packet Contract

Write one `_ops/handoffs/<timestamp>-<actual-model>.md` file, where
`<timestamp>` is the current system time in `YYYY-MM-DD-HHMMSS` form. Its
frontmatter contains `description` (`Handoff <timestamp>: <one line>`),
`model`, and `date` using that same value.

Place these lines immediately after frontmatter:

1. Read this file in full.
2. Live files and runtime state override this dated snapshot.
3. First state the next action and why, then compare the recorded HEAD with
   `git log`.

Put every continuation-changing veto, blocker, or unverified state immediately
after this preamble or in `## Anchors`; do not bury it in the middle.

The consumer interface has four required sections:

- `## Terrain Model`
- `## Where We Are`
- `## Next Step`
- `## Anchors`

It exposes where work stopped, one next action and its reason, exact live
anchors, HEAD, recall and cleanup outcomes, and the previous received handoff
if any. Every continuation-changing state claim names both:

- `knowledge`: the command, test, diff, or other observation that verified it,
  or `unverified`;
- `consequence`: `none`, `accepted assumption`, `blocker`, or `reframe`.

`## Terrain Model` preserves the minimal causal model needed to continue. Add
misleading terrain only when an obvious reading is still plausible and this
session produced evidence that disproved it. Do not invent traps or write a
chronological diary.

Add `## Incidents` only when new evidence invalidated work already begun or
changed the route. Record the prior model, trigger, paid cost, why it was found
late, and the durable cleanup outcome. Use timestamps for cost or `unknown`;
write `unknown` when the late cause is unavailable.

Add one separate `## Advice to the Next Agent` only for new, session-grounded
observations tied to a file or work type and their cost or benefit. Do not put
improvement proposals in the history, and do not repeat a lesson already
routed to a guardrail or finding. Omit optional sections when their evidence
gate is not met.

Use one addressable `###` block for each independent terrain correction,
incident, or advice item.

## Consumer Evidence

Before delivery, reread the packet as an agent with the repository and path but
no chat. The packet passes only if that reader can:

- name and begin the correct next action, and explain why;
- distinguish dated claims from live truth and find evidence for material
  state;
- see every pending decision, veto, blocker, risk, and unverified assumption
  that can change continuation;
- avoid any paid dead end or surviving false terrain from this session; and
- locate the current owners of live truth.

Confirm absence instead of inventing a dead end, incident, or trap. Completing
the named sections is not a stop condition: repair the packet or report the
exact blocker whenever the consumer outcome is still false.

## Completion

Return the exact packet path or exact packet blocker, plus one line describing
the packet when it exists. Report these independent outcomes once:

- `recall`: `captured`, `no qualifying evidence`, or `blocked`;
- `cleanup`: named changes, `nothing to clean`, or `handed off`;
- `packet`: exact path or `blocked`;
- `consumer check`: `passed` or the exact blocker.

A blocked outcome does not erase a successful one. State residual risk only
for unavailable context or unverified claims. Stop when further text or
cleanup cannot change continuation.
