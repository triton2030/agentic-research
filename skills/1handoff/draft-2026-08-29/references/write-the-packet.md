# Write the packet

You are writing for an agent who holds this repository and this path and no
conversation. Write only what that reader cannot obtain from live files, and
point at live files for everything else.

1. Keep a fact, choice, failure or observation only when its loss could change
   the next action, decision, veto or risk, or let a paid mistake repeat. Omit
   the rest. Where live state still holds the information, give one exact
   address and why it matters instead of copying the explanation.
2. Carry owner evidence only as its recall address plus one line on how it
   changes continuation, never as your retelling of what the owner said.
3. Write one file `_ops/handoffs/<timestamp>-<actual-model>.md`, where
   `<timestamp>` is the current system time as `YYYY-MM-DD-HHMMSS`. Its
   frontmatter carries `description` (`Handoff <timestamp>: <one line>`),
   `model` and `date` built from that same value. For `model` use a short
   honest identifier of the model actually running, and do not invent a
   subversion.
4. Immediately after the frontmatter, address the reader in three lines: read
   this file in full; live files and runtime state override this dated
   snapshot; first state the next action and why, then compare the recorded
   HEAD with `git log`.
5. Give that reader four sections — `## Terrain Model`, `## Where We Are`,
   `## Next Step`, `## Anchors` — exposing where the work stopped, one next
   action with its reason, and in `## Anchors` the exact live addresses, HEAD,
   the recall and cleanup outcomes, and the previous received handoff if this
   session inherited one.
6. Put every continuation-changing veto, blocker or unverified state
   immediately after the three-line preamble or into `## Anchors`, because the
   middle of a file is where a reader stops seeing things.
7. Label every continuation-changing state claim twice: `knowledge` is the
   command, test, diff or other observation that verified it, or `unverified`;
   `consequence` is `none`, `accepted assumption`, `blocker` or `reframe`. One
   label cannot carry both meanings.
8. `## Terrain Model` holds the minimal causal model the next agent needs —
   the reading this session held, the evidence that changed it, and what it
   believes now — written as `initial model or action -> evidence or result ->
   resulting model`. A still-plausible reading this session disproved belongs
   here; a chronological diary of the session does not.
9. Add `## Incidents` only when new evidence invalidated work already begun or
   changed the route, and record the prior model, the trigger, the cost paid in
   timestamps or `unknown`, why it was found late, and the durable cleanup
   outcome.
10. Add one `## Advice to the Next Agent` only for new session-grounded
    observations tied to a file or a kind of work, with their cost or benefit.
    Observations only: what you disliked or how something could be improved
    does not belong here, and a lesson already routed to a guardrail or a
    finding is not repeated here.
11. Give each independent terrain correction, incident and advice item its own
    addressable `###` block, and omit a gated section entirely when its
    evidence is absent — confirm that absence instead of inventing a dead end,
    an incident or a trap.
