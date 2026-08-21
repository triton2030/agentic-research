# Distilled probe receipt

Status: `candidate` — deterministic evidence passed; semantic acceptance is external.

## Frozen provenance

- Commit: `09d2a48b2a82ff4b35ffb739a11b5721351d7dd6`
- Manifest: `experiments/openviking-chat-recall/artifacts/distilled-gold-manifest.json`
- Sources: `2`; records: `7`; claims: `6`.

## Design trace

- Owner: `scripts/build_distilled_probe.py`; manifest owns frozen membership and explicit claim status; tests own the boundary proof.
- Chosen seam: one stdlib compiler with `manifest → evidence validation → input/Wiki projection`; a multi-module package was rejected because the probe has one writer and no evidenced independent runtime seam.
- Applied project principles: Product Frame P-001/P-003/P-004/P-005/P-008; this keeps the derived experiment separate from immutable holders, makes the evidence chain visible, and leaves semantic self-report unaccepted.

## Deterministic validation

- `exact-source-quotes-absent`: `pass`
- `history-fields-absent`: `pass`
- `lifecycle-filter-is-explicit`: `pass`
- `no-gold-boundary`: `pass`
- Rebuild check: the test suite compares every generated input/Wiki file byte-for-byte across two temporary output roots and verifies receipt regeneration.

## Semantic boundary

- Status: `candidate`.
- The builder accepts `current`/`contested` as explicit candidate input and suppresses `non-current`/`uncertain`; it never derives currentness from `latest`.
- No-gold controls remain explicit `abstain`/`unknown` gaps with checked source addresses; they are not projected as claims.
- Not proven here: semantic grouping quality, currentness beyond the manifest status, and blind retrieval usefulness.

## Falsifying checks

- frozen blob, line, record ID, timestamp or quote-digest drift fails closed;
- unknown record ID or lifecycle status fails closed;
- dangling `superseded_by` fails closed;
- exact source quotes and count/first/latest/evolution markers cannot enter default Wiki;
- non-current/uncertain claims and no-gold controls cannot enter default Wiki;
- deterministic rebuild must be byte-identical.

## Test command

`python3 -m unittest discover -s tests -p 'test_*.py' -v` (run from a clean checkout of the writer commit).
