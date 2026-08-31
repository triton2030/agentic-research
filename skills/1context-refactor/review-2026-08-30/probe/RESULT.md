# Probe result

## Verified input

- `1index/SKILL.md` component: `1314f3cccb237206c2d5c1f7d5ed4837ba52a26a21bdd661957f666afe0b94c1`.
- `1index` package: `6c8f0af1a15a9ac1d55a5dd442a90be343d9040ef7d6e1b53c4588b474625d4b`.
- `1context-refactor/SKILL.md` component: `c1e85a65762d764f4a3a9f20b9835045758e7d344a793da911dd50664a6c8bc1`.
- `1context-refactor` package: `172f2648c4c99a65a9190f4d32ce1add2ce631fcbc6fdf8f99c2058213a5737f`.

The component hashes were recomputed before semantic reading. Each package
hash was recomputed from the sorted SHA-256 listing of `SKILL.md` and
`platforms/`; all four values matched `REQUEST.md` exactly.

## Causal verdict

Unknown. The trace does not distinguish the influence of the large tool
output, the stale release plan, instruction overload, or loss of the user's
correction during summarization. The strongest alternative to the immediately
preceding large output is the stale release plan: it was available before the
first error and contains the repeated Europe-first proposal.

The distinguishing counterfactual is to replay the final-summary step while
holding the correction, release plan, and instructions constant and varying
only whether the large output is present. A changed outcome would support an
effect from that output; an unchanged Europe-first result would leave the
other alternatives live. This replay was not available in the probe.

## Actual path

1. Read the complete available session and fixture sources.
2. Left causality unknown because the trace contains no activation evidence or
   distinguishing observation.
3. Applied `1index` independently to the costly search. Added one-hop routes
   for `docs/operating-model.md#market-sequencing` and
   `research/pilot-results.md#retention-gate` to the existing
   `workspace/INDEX.md`.
4. Did not route `config/rollout.yaml`: its location is obvious and the session
   shows it was already found before the error.
5. Recorded the observed stale-source conflict in `workspace/FINDING.md`.
6. Skipped causal advice because no wording was shown to have caused the
   repeated choice. Skipped source repair because causality and owner authority
   were both absent.

## Direct checks

- Both new INDEX targets resolve as existing files, and their fragments match
  the exact `Market sequencing` and `Retention gate` headings.
- Starting from the session's external intents—plan rollout sequencing and
  check whether the pilot gate permits the next market—each INDEX route reaches
  the relevant live source owner in one Markdown transition.
- The routes contain no market decision, pilot result, numeric threshold, or
  copied source prose.
- `workspace/INDEX.md` has exactly two new routes; no route was added for
  `config/rollout.yaml`.
- Source fixture hashes were checked before and after the writes; `REQUEST.md`,
  `SESSION.md`, `README.md`, `config/rollout.yaml`,
  `docs/operating-model.md`, `release-plan.md`, and
  `research/pilot-results.md` were unchanged.
- Candidate component and package hashes were recomputed after the writes and
  remained identical to the verified input above.
- The only probe outputs written were `workspace/INDEX.md`,
  `workspace/FINDING.md`, and `RESULT.md`.

## Residual unknowns

- Which available context, if any, caused either Europe-first choice.
- Whether removing only the large output would change the final summary.
- Whether the stale release plan should be revised, archived, or retained as
  historical evidence; its owner and intended lifecycle are not in the probe.

## Terminal verdict

PASS. The candidate path produced only the authorized routes and finding,
preserved unknown causality, and declined advice and source repair without
proof or authority.
