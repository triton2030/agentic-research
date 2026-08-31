# Final review — exact candidate — 2026-08-31

## Exact candidate

- `candidate-high-level-2026-08-31/SKILL.md` — SHA-256
  `25d7109c42f176bd25f3b81108d000a463dd55ea9cc3d0b556ff1849467fa41c`.
- `candidate-high-level-2026-08-31/platforms/codex/agents/openai.yaml` —
  SHA-256
  `5e8e66e2b2b42b0f7475cb1293d932f52dfd6cfe24f0eac92d661ceb7498f100`.
- Deterministic package manifest SHA-256 —
  `97504926e9486a0f2dd5262556063ad6098533d4c34e38a3aa31932e5dbcbeee`.

Package hash algorithm: from candidate root, sort every file path, emit
`shasum -a 256` manifest with relative paths, then SHA-256 the manifest bytes.

Authoring baseline during final review:
`/Users/triton/.codex/skills/1skill-creation/SKILL.md` SHA-256
`11e82449797be9615b92976f2fe33f8677f74429a10fc2564a91b7a09fae344e`.

## Reviews

Wave 1 literal findings were accepted: false counts, rigid Frame fields,
ambiguous conflict ownership, missing two-way `GOAL` conflict and stale
authoring SHA. Wave 1 trajectory findings were accepted: one-signal admission,
free-form Frame and isolated application test.

Wave 2 literal finding was accepted: independent predicates are now separate
numbered lines and the count over 20 is explicit. Wave 2 trajectory findings
were accepted: holdouts are prepared before the pair and independently of its
text; update mode presents every removed or changed meaning from the prior
approved pair.

No reviewer approved the package; decisions above belong to the root author.
Both allowed reviewer waves are exhausted.

## Clean trace

`wave2-clean-probe.md` is a real clean run of the pre-final candidate. It began
with «Я делаю приложение для детей», asked three high-leverage questions,
rejected unsupported principles, produced a three-principle pair and used a
separate clean validator for product, UI and implementation decisions. It
stopped before approval and made no canonical write.

The final candidate strengthens two properties after that probe:

- holdout cases must be prepared before and independently of pair wording;
- update mode must expose every changed or removed prior meaning.

The first property was not rerun on exact final bytes; the old validator chose
its cases after reading the pair. The second was not exercised because the
probe created a pair without a prior approved version. These are explicit
evidence gaps, not content findings.

## Counts

- `SKILL.md`: 56 lines; 3 routing distinctions, 4 goal properties and 38
  independently checkable protocol predicates.
- `openai.yaml`: 7 lines; 4 independently checkable fields.
- Runtime references: 0; the earlier `pair-contract.md` was removed.
- The conservative terminal active set exceeds the soft target of 20. It is a
  known cognitive risk. Further deletion would remove a named source,
  abstraction falsifier, independent holdout, update-loss guard or authority
  boundary.

## Mechanical and preservation verdict

- `skill-creator` quick validation: pass.
- Candidate internal reference scan: empty; no stale `pair-contract` link.
- Candidate trailing-whitespace scan: empty.
- Tracked/live `1product-shaping` remain byte-identical to each other at
  `f1867a192c68200ab72e63a2f05c41ba0306928b7da1337707d4b7070a4fa896`.
- Tracked/live `1use-principles` remain byte-identical to each other at
  `f3525c759e7b723b3c5792af3fe693b55826c627ec332c70b9c4a9584497cbf9`.
- No candidate was installed and no official/live file was changed by this
  repair.

Terminal verdict: `CANDIDATE_READY_WITH_EVIDENCE_GAPS`; exact owner approval
and installation were not requested or performed.

