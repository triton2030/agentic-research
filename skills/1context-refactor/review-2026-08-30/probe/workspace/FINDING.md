# Finding: stale rollout draft conflicts with current sources

## Observation

`release-plan.md` still records Europe as the first proposed market in an April
draft, while `docs/operating-model.md` and `config/rollout.yaml` contain the
current Kazakhstan-first sequence.

## Consequence

The stale draft is a competing source for market sequencing. The session shows
that the agent read it before the first wrong choice, but does not establish
that it caused either error.

## Disposition

Recorded only. The source was not repaired because its influence is unproven
and its owner did not authorize a change.
