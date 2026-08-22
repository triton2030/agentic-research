---
kind: module-card
wave: 7
state: superseded
role: semantic-candidate-writers-and-canonical-merger
system-owner: root
canonical-review: claude-opus-5
batch-model: gpt-5.6-luna
batch-thinking: max
---

# Модуль — semantic candidates и canonical claims

[parent: task.md](../task.md) · historical parallel semantic route ·
superseded by the chronological fold in Wave 6f]

## Contribution

Получить из frozen partitions проверяемые knowledge candidates, затем одним
serial owner слить их в canonical claims с явной currentness и rejection
причинами. До закрытия Wave 6b карточка остаётся только планом.

## Inputs

- frozen `part-*/input.jsonl` и partition manifest Wave 6;
- pinned OpenViking Wiki Skill/prompt/config/model tuple с provenance и digests;
- accepted claim schema, lifecycle vocabulary, privacy/provider gate и
  terminal Wave 6b matched utility PASS.

## Dependencies

S1 parallel candidate generation → deterministic validation → S2 serial
canonical merge. S2 начинается только после terminal return каждого part.

## Ownership

- Каждый S1 Luna Max writer владеет ровно одним
  `artifacts/full-build/semantic/part-*`, его `candidates.jsonl`,
  `rejections.jsonl` и private worker receipt.
- Shared generator/validator: `scripts/generate_semantic_candidates.py` и
  `tests/test_semantic_candidates.py`; назначается одному writer.
- S2 root-owned serial merge with read-only Opus review:
  `scripts/merge_canonical_claims.py`,
  `tests/test_canonical_claims.py`,
  `artifacts/full-build/canonical/{claims,rejections}.jsonl` и `index.json`.
- Root один пишет final semantic manifest, принимает commits и разрешает
  currentness; Luna S1 не принимает системные или lifecycle решения.

Каждый top-level writer запускает nested read-only checker своей зоны.

## Semantic contract

- Модель предлагает grouping, concise statement, applicability, claim type,
  lifecycle candidate и source record IDs; она не переписывает evidence.
- S1 видит только frozen quote records и contract. Упомянутые в цитатах
  project files, docs, code и project knowledge не входят в allowed surface и
  не открываются для обогащения claim-а.
- `latest` не означает `current`. Superseded, uncertain, contested и
  scope-dependent знания остаются различимы.
- Unsupported, dangling, conflicting или schema-invalid output отклоняется с
  адресуемой причиной; validator не исправляет его молча.
- Canonical merge сохраняет used/rejected relation каждого candidate и каждого
  source record.
- Claim без достаточного currentness evidence не попадает в default Wiki;
  superseded формулировка остаётся только в evidence/rejections, не рядом с
  актуальным знанием.

## Resume and privacy

Resume key включает input, model, prompt, config и code digests. Любой drift
инвалидирует part. Receipt хранит IDs/counts/digests/cost/retries, но не quotes,
API secrets или полный model transcript. Реальные holders не уходят provider-у
до принятого synthetic canary Wave 6.

## Falsifying checks

- invented/unknown record ID, mutated quote digest и missing provenance fail;
- project-file lookup или unsupported enrichment за пределами quote input fail;
- matched supersession fixture не выдаёт prior claim как current;
- no-gold fixture abstains;
- shuffled part order даёт тот же canonical output;
- collision/duplicate claim остаётся rejection или explicit merge evidence;
- interrupted part resumes только при полном digest match.

## Return

Part writers: commit SHA, part ID, input/output counts, cost/retry summary,
validator result и nested receipt. S2: canonical counts, disposition map,
tests, unresolved conflicts и exact downstream tuple. Любой material UNKNOWN
блокирует Wave 8.

## Prohibitions

Не писать L2/L1/L0, shared plan/status, holders или source evidence. Не считать
writer self-report semantic acceptance.
