---
name: 1handoff
description: >-
  Use when $1handoff or /1handoff is requested, or when long repository work
  must move to a fresh session before continuation-critical state is lost. Not
  for summaries, final reports, file transfer, or a second handoff in the same
  chat.
---

# Handoff

Close one repository work session so a fresh agent can continue without the old
chat. Produce two independent outcomes:

- `1chat-recall` preserves qualifying owner evidence under its own contract.
- A continuation packet in `_ops/handoffs/` preserves the dated,
  action-changing session delta.

Successful continuation—not conversation completeness—decides what belongs in
the packet. Together, packets form a history of work, mistakes, and useful
observations.

## Outcome

With only the repository and the explicit packet path, a fresh agent can begin
the correct next action for the right reason, avoid errors and disproved models
paid for in this session, and inherit the management layer without state made
stale by this session.

## Boundaries

- Create no more than one handoff in a chat.
- Deliver the returned path manually to the next session. Do not create or use
  a “latest handoff” index, hook, automatic discovery, or consumed state.
- A packet is not a transcript, chat summary, task plan, or new project canon.
  Include only the dated delta from the current session. Do not transfer other
  sessions, a user profile, or general project rules.
- Follow the owning skill for plans, findings, indexes, instructions, and other
  managed surfaces. Outside those named contracts, change only work authorized
  by the project, recoverable in one Git operation, and not requiring owner
  approval. Hand off everything else with an exact anchor.
- Record the actual running model with a short, honest identifier. Do not invent
  a subversion.

## Closeout

The order matters: recall and cleanup must resolve before their outcomes enter
the packet, and the packet must pass its consumer check before delivery.

1. **Resolve recall.** Invoke `1chat-recall` through the current runtime’s skill
   mechanism and follow its contract. If unavailable or blocked, continue the
   packet and state the exact reason; never imitate recall inside the handoff.
   A statement may enter both recall and the packet when it passes both gates.

2. **Clean the management layer.** Review the entire layer for state affected
   by this session:

   - update the active plan and status through `1planning`;
   - close or mark findings made stale by this session;
   - add an `INDEX.md` route through `1index` when expensive discovery found
     knowledge somewhere non-obvious;
   - update instructions or documentation made stale by this session;
   - resolve Git state as project instructions authorize—commit and push only
     when allowed; otherwise record the exact state;
   - remove only temporary material whose loss is recoverable or reproducible.

   Search earlier `Advice to the Next Agent` sections for each candidate
   recurring observation. If it has recurred, install a guardrail when current
   authority and its owning contract allow the change; otherwise create a
   finding and anchor the reason.

   Report named changes, `nothing to clean`, or what was handed off.

3. **Select the continuation delta.** For each candidate:

   - If a live file or runtime state can recover it, keep only
     `path: what changed / why this address matters`.
   - If losing it cannot change the next action, decision, veto, risk, or a
     repeated mistake, omit it.
   - Otherwise record
     `fact or choice -> reason or evidence -> consequence for continuation`.

   Represent an owner decision or correction only with its `1chat-recall`
   address and a one-line statement of relevance. Capture a missing address
   through the recall branch first. If recall rejects the evidence but losing
   it would change continuation, mark the block `no recall address`.

4. **Write the packet.** Create `_ops/handoffs/` if needed. Generate the
   timestamp with `date +"%Y-%m-%d-%H%M%S"` and write
   `_ops/handoffs/<timestamp>-<model>.md`.

   Frontmatter contains `description`
   (`Handoff <timestamp>: <one line>`), `model`, and `date` using the same
   timestamp.

## Packet Content

Place these three lines immediately after frontmatter:

1. Read this file in full.
2. Live files and runtime state override this dated snapshot.
3. First state the next action and why, then compare the recorded HEAD with
   `git log`.

Place every continuation-changing veto, blocker, or unverified state from this
session immediately after the preamble or in `## Anchors`; do not bury it in the
middle.

Always include:

- `## Terrain Model`
- `## Where We Are`
- `## Next Step`
- `## Anchors`

Add `## Incidents` and `## Advice to the Next Agent` only when their gates admit
content. Do not create empty sections. Use one addressable `###` block per
meaning.

The packet records:

- where work actually stopped, including unfinished and unverified work;
- continuation-changing completed work, what changed, and why;
- one next action and its reason;
- exact paths, commands, IDs, and runtime state, each with one line explaining
  why the anchor matters;
- relevant owner decisions and corrections as recall addresses;
- open questions, rejected routes, tool failures, and surprises that passed
  delta selection;
- the HEAD commit, recall and cleanup outcomes, and the path of the previous
  received handoff, if there was one.

Every state claim carries two labels:

- `knowledge`: the command, test, or diff that verified it, or `unverified`;
- `consequence`: `none`, `accepted assumption`, `blocker`, or `reframe`.

### Terrain Model

Write a 3–5 line working model of the system as understood when the session
ended. Preserve causal history as addressable beliefs:

`initial model or action -> evidence or result -> resulting model`.

Do not write a chronological diary.

Add 2–4 trap blocks only for misleading terrain that still exists:

`obvious reading -> model it suggests -> evidence that disproved it -> what is
true`.

Do not record a corrected file as a trap or a surprise with no consequence for
the next agent.

### Incident

Add an incident only when new evidence, tool output, or an owner correction
changed the route or invalidated work already begun:

`before -> trigger -> cost -> why discovered late -> cleanup outcome`.

Use timestamps for cost or write `unknown`. Write `unknown` when the reason for
late discovery is unavailable. Point to the guardrail or finding produced
during cleanup; do not decide or install it here. Advice to a future reader is
not a guardrail.

### Advice to the Next Agent

Record observations, not improvement proposals:

`what was difficult, mistaken, slow, or unexpectedly helpful -> file or work
type -> cost or benefit`.

A new observation remains advice. If cleanup found the observation in an
earlier handoff, do not repeat it as advice; record only the guardrail or finding
produced during cleanup.

## Consumer Check

Before returning the path, reread the packet as an agent with the repository
and path but no chat. It must answer:

- What is the next action, and why?
- Which continuation-changing decision, blocker, veto, or unverified state from
  this session is pending?
- Which paid dead end must not be repeated, if any?
- Which obvious reading of the terrain is false, if any?
- Where is current live truth?

Confirm absence rather than inventing a dead end or trap. If an answer is
missing, add the continuation-changing delta. If a block can be replaced by
reading one live file, replace it with that file’s anchor.

## Completion

Return the exact packet path or the exact packet blocker. When a packet exists,
add one line describing it.

Report these outcomes once:

- `recall`: `captured`, `no qualifying evidence`, or `blocked`;
- `cleanup`: named changes, `nothing to clean`, or `handed off`;
- `packet`: exact path or `blocked`;
- `consumer check`: `passed`, or the exact blocker.

A blocked outcome does not erase a successful one or become silent completion.
State residual risk only for unavailable context or unverified claims. Stop when
more text cannot change continuation. Do not run broad indexing or
repository-wide checks only for the handoff.
