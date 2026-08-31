# Review round 1 — 2026-08-29

Scope: uninstalled Codex candidate, теперь по адресу
`skills/1chat-recall/versions/draft-2026-08-29/codex/`.

## Independent checks

- Literal checker followed
  `/Users/triton/.codex/skills/1skill-creation/agents/check-instructions.md`.
- Trajectory checker followed
  `/Users/triton/.codex/skills/1skill-creation/agents/check-trajectory.md`.
- Neither checker saw the other's result before returning.
- Clean executor used only the candidate instructions and an isolated corpus at
  `/tmp/recall-skill-probe.UmTXmj`.

## Observed trajectory

Prompt: remember a correction that the probe project now requires explicit UTC
timestamps rather than local dates, then determine whether it cancels prior
owner speech.

The executor opened `SKILL.md` → `capture.md`, completed one write, returned to
the router, then opened `retrieval.md`. It wrote
`2026-08-29-152318-codex-01a04d0a.md#L15` with
`supersedes: 2026-08-01-100000-codex-00000000.md:15 sha:78ae8a90`, opened both
holders, ran the normal query plus a facet and `--since`, and returned the new
position rather than a quote dump.

The probe did not establish two obligations: the independent retrieval agent
could not start because all collaboration slots were occupied, and the prompt's
corpus-only boundary prevented a real live-owner check. The executor also
misprinted the old holder's absolute link once; the stored relative address and
the actual fixture filename were correct.

## Findings and decisions

| Finding | Evidence | Decision in round 2 |
| --- | --- | --- |
| Body and reference were counted separately although earlier instructions remain in context. | `_ops/chat-recall/2026-08-28-183116-claude-0713a127.md:24-25`; literal check finding 1 | Accepted. Count body + selected reference; redesign to 9 common units and at most 11 mode units. |
| Description exceeded the local 200-character rule and did not use literal `Use when`. | literal check finding 2; official OpenAI trigger guidance | Accepted. English `Use when` description reduced below 200 characters. |
| `transient logistics` and `screen-history lookup` lacked a recorded causal chain. | literal check finding 3 | Accepted. Removed; retained only the already accepted assent skip. |
| The candidate ignored the latest explicit request to translate the skill to English. | `_ops/chat-recall/2026-08-24-184002-codex-01a033fd.md:19` | Accepted. Entire runtime candidate translated to English; live remains untouched. |
| Ordinary Capture/Retrieval in references conflicts with the older hot-body decision. | `_ops/chat-recall/2026-08-19-135233-codex-01a01922.md:30`; clean probe trajectory | Unresolved owner choice. One clean probe shows the router can work, but installation still requires explicit approval of this topology. |
| Same-turn Capture and the `context-note` fallback were missing. | literal check findings 6-7; `product-frame.md:38-48`, `:56-59` | Accepted. Restored as explicit Capture steps. |
| `query_domain` lost lexical/empty/off-domain semantics. | literal check finding 8; live `SKILL.md:32-37` | Accepted. Restored in Retrieval. |
| Truncation/recovery state machine contradicted itself and did not return to a position or `abstain`. | both checkers; candidate round-1 `retrieval.md:33-47`, `reading-the-log.md:39-42` | Accepted. Only materially unresolved truncation yields `recovery-needed`; recovery returns through the body to Retrieval. |
| Two empty facets became a mandatory stop. | trajectory finding 4; `cut.md:129` | Accepted. It now permits stopping only when no named next facet could change the claim. |
| Repair was not standalone and had invalid one-shot CLI choreography. | literal check findings 10-11 | Accepted. Restored admission, usefulness, provenance, precision, sentinels, full capture metadata, separate commands, mutation boundary, and proof. |
| Structural validation was an un-routed mode inside recovery. | literal check finding 12 | Accepted. Routed through Repair and moved into its integrity proof. |
| Examples duplicated inventory and placed `--prepare` after retry. | literal check finding 13 | Accepted. One inventory call; standalone prepare precedes retry. |
| History snapshot contained shifted or unqualified evidence addresses. | literal check finding 14 | Accepted for the history copy. Live Product Frame remains unchanged until approval. |

## Round-2 falsifier

Reject the revision if either independent checker still finds more than 20
active units for any mode, a lost accepted invariant, a reference chain, or a
state that can exit without source-bound receipt / position / `abstain`.
