# Architecture Critic Raw Output

Verdict: `architecture_risk`

## Finding 1 — Evidence Model Still Text-Corpus-Shaped

Domain-neutral intent is stated, but the durable schema still assumed evidence
was a local file plus `line_ref`. That works for Markdown docs, not cleanly for
films, slides, screenshots, landing pages, UI states, visual design, or timed
media.

Evidence:

- `README.md` names films/decks/landing pages/designs.
- `docs/RESEARCH.md` says anchors may be artifact elements, interviews, or
  measurements.
- The old `templates/evidence-ledger.tsv` and `scripts/check_run.py` required
  `local_path` + `line_ref`.

Alternative: replace `line_ref` as the universal locator with an
`artifact_anchor` contract: `artifact_ref`, `modality`, `locator_type`,
`locator`, `capture_ref`, optional `text_excerpt`. `line_ref` becomes one
locator type.

## Finding 2 — Run Gates Not Owned By Deterministic Layer

The architecture says no challenger, no source strength, no owner approval, and
no reality evidence are gates, but the checker mostly validates files, ledger
columns, source labels, weak `decision_ground`, and path existence.

Alternative: add a run manifest/report header with gate statuses, raw-role
files, independence labels, and closure status; make `check_run.py` validate
suite `required_roles` against `raw/`.

## Finding 3 — No Case Taxonomy Yet

Method docs are domain-neutral, but the only concrete case/run is a business
Markdown corpus with owner files, current/future boundaries, line refs, and
MAVO-specific decision chains.

Alternative: introduce a case contract: `artifact_type`, `decision_type`,
`oracle_types`, `anchor_adapter`, `reality_test_type`, `owner_status`. Add at
least one non-MAVO negative control before claiming generality.

## Finding 4 — v0 Failures Not Yet Demonstrated Closed

The rebuild names v0 errors, but the v1 run was incomplete at the time of
review. Architecture intent was present; evidence of closure was not.

Alternative: add a `v0-failure-map`: each v0 failure -> structural mechanism ->
deterministic/agent evidence proving it fired.

## Bottom Line

The central model is good: traceable decision audit under missing oracle, not
truth. The risky part is that the public surface was still too Markdown/MAVO-
shaped. Minimal fix: real artifact-anchor schema plus gate validation, then one
non-MAVO case.
