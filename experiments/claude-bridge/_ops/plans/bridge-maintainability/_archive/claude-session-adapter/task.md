---
description: "Completed bounded transient Claude session adapter cutover and acceptance evidence"
kind: task
---

# Claude Session Adapter

## Outcome

Keep `claude_ask` as the compatible blocking default and add an opt-in,
process-local adapter for parallel Claude sessions that can be observed,
steered, and stopped without introducing a second durable agent runtime.

## Accepted Contract

- `claude_ask` remains the ordinary one-call/one-result interface.
- `claude_session.open_fresh` includes the initial prompt and returns Claude's
  native `session_id`. `open_resume` accepts that ID plus a new prompt; send,
  steer, and stop address the same ID.
- `claude_observe` is pull-only. Each call returns one bounded summary,
  activity, conversation, or diagnostic view; it does not stream updates.
- A live lease is process-local state keyed by native `session_id`, not a second
  public handle or identity. The native ID remains the durable conversation
  identity.
- Restart loses active leases and in-memory observations. A caller with a known
  native `session_id` can call `open_resume` with a new prompt; the bridge does
  not reconstruct abandoned transport state.
- Multiple leases may run in parallel without sharing prompts, queues,
  revisions, cancellation, or result state.
- The bridge never forwards a continuous raw transcript, extended thinking, or
  raw tool input/output into Codex context.
- Every active-turn deadline expires before the Codex host tool timeout, leaving
  time for a typed terminal result and bounded process cleanup.

## Scope

- In:
  - the transient SDK session adapter and its bounded in-memory observation;
  - the three MCP tools, existing request/subscription policy, shutdown, and
    timeout ordering;
  - deterministic, live-Claude, and fresh-host proof;
  - runtime owner docs and any accepted client projection after runtime proof.
- Out:
  - durable registries, persistence, restart recovery, transcript or event
    stores, push streaming, polling daemons, tmux, relays, and worker paths;
  - a second session identity, private Claude session-format parsing, or a
    multi-provider/billing route;
  - unrelated trust-boundary, skill-trigger, hook, or settings redesign.

## Milestones

- [x] Prove the pinned SDK lifecycle needed for one long-lived input mailbox,
      one output pump, interrupt/steer, close, and native resume.
- [x] Add the transient session owner and keep `claude_ask` compatible over the
      same deep execution seam.
- [x] Expose bounded session control and observation with focused isolation,
      cleanup, restart, and timeout tests.
- [x] Pass live parallel/steer/stop/resume checks and the fresh-host MCP gate,
      then reconcile docs and projections with the proven runtime.

## Done

- [x] Fresh discovery exposes exactly `claude_ask`, `claude_session`, and
      `claude_observe`; `claude_ask` keeps its accepted request/result contract
      and remains the documented default.
- [x] Parallel fresh and resumed leases remain isolated, and concurrent resume
      of one native `session_id` is rejected while its lease is active.
- [x] Send, steer, stop, host cancellation, MCP shutdown, and adapter timeout
      have deterministic terminal ownership with no observed process tail.
- [x] Observation is pull-only and bounded for summary, activity, conversation,
      and diagnostic views; no response contains extended thinking or raw tool
      input/output.
- [x] Restart demonstrably drops active leases and retained observations; a
      known native `session_id` remains resumable through a new lease.
- [x] The internal active-turn timeout is strictly shorter than the configured
      Codex host timeout and returns a typed timeout before host transport loss.
- [x] Focused tests, clean install, live Claude acceptance, fresh Codex
      discovery, one real blocking call, and one real session flow all pass.
- [x] `README.md`, `AGENTS.md`, host configuration, and any accepted installed
      projection describe the same proven interface and bounds.

## Final Reconciliation

- The bridge already has the three-tool contract, pull-only bounded
  observations, native-ID leases, parallel isolation, follow-up, steer, stop,
  native resume, compact typed warnings, and one context-bearing MCP success
  carrier.
- A final developer review found three lifecycle gaps after the earlier green
  run: SDK subscription init had to be validated before forwarding any SDK
  event, a cancellation arriving during async preflight had to prevent process
  launch, and `command_lifecycle` completion had to correlate through
  `command_uuid`.
- Those three fixes and deduplicated capacity accounting for failed-reopen
  cleanup are present locally. Focused regressions, the deterministic suite,
  full live runtime, and a fresh Codex host have now passed against them.
- Official Anthropic guidance for
  [streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)
  confirms it is the recommended long-lived interactive Agent SDK mode and
  supports queued messages, interruption, native tools, and multi-turn context.
  Its [session guide](https://code.claude.com/docs/en/agent-sdk/sessions)
  records that the TypeScript V2 session-holder API was removed, so the bridge
  remains a narrow adapter around supported `query()` streaming input rather
  than replacing an available SDK session object.
- Developer and architecture re-reviews found no remaining material blocker.
  The acceptance audit passed all nine contract conditions. Skill, Markdown,
  graph, syntax, and diff validators passed; the completed task was archived
  before the scoped commit and push to `main`.

## Closeout Evidence

- `npm ci` completed against the exact lockfile; Agent SDK `0.3.219` and Claude
  Code `2.1.219` remained pinned.
- `npm run ask:test` passed 34 deterministic tests, including MCP-visible schema,
  bad-init event ordering, parallel isolation, duplicate resume, warning
  redaction, newest-answer budgeting, correlated turn completion, steer
  ordering, unique retained-cleanup capacity, typed session timeout,
  cancellation-before-launch, and restart-like `open_resume`.
- `npm run ask:live` passed blocking Opus/Fable in parallel, native resume,
  native `Read`, bounded observations, same-engine follow-up, live interrupt
  with a forced native resume, stop, and cancellation with no surviving
  observed child PID.
- A final fresh ephemeral Codex process made five valid MCP calls with zero
  failures: blocking ask, session open, summary, conversation, and stop. It
  recovered both markers available only through `structuredContent`; every
  text carrier remained the same constant receipt. An earlier probe exceeded
  the documented `wait_ms` maximum once, was rejected by schema validation, and
  recovered; it is not counted as the green host receipt.
- Both skill copies passed `quick_validate.py`, matched with `diff -qr`, and all
  changed Markdown passed `rumdl`, `md check`, and `md cycles`.
- The final developer critic returned `satisfied`, the architecture critic
  returned `architecture_ok`, and the acceptance auditor returned `pass` across
  all nine checked conditions.

## Stop / Handoff

- Stop and return to the owner if the pinned public Agent SDK cannot prove
  steering, bounded cleanup, or native resume without an undocumented protocol,
  durable bridge state, or a widened trust/billing boundary.
- Do not hide an SDK or host limitation behind polling, persistence, a second
  identity, a longer context feed, or a silent increase of the turn limit.
