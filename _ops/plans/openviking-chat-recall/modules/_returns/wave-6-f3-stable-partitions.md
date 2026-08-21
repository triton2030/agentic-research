---
kind: module-return
wave: 6
stage: F3-stable-partitions
state: accepted
date: 2026-08-22
---

# Wave 6 F3 — stable partitions

## Результат

Visible Luna Max task `01a02629-b1e2-71d2-949f-9a605f686b8b` построил F3 из
accepted F2 artifacts. Candidate `2b74df5` интегрирован в `main` как
`c5bbe41`.

Exact ownership: writer, его test, `partition-manifest.json` и восемь
`part-001` … `part-008/input.jsonl` в
`experiments/openviking-chat-recall/artifacts/full-build/clusters/`.

## Partition rule

`topic-first-session-bounded-lpt.v1`:

- `part_count=8`, target `ceil(1101/8)=138` records;
- normalized topic — primary semantic unit;
- topic до target остаётся целым;
- oversized `агенты-и-ии` из 624 records делится на 5 shards только между
  целыми `(topic, session)` groups;
- shards раскладываются largest-first в самый лёгкий part, tie — по part ID;
- строки сортируются по `metadata.topic`, `metadata.session`, `record_id`;
- fallback делит oversized group по stable record IDs и обязан явно поставить
  `session_split=true`; на frozen corpus fallback не активирован.

Parts содержат `138, 138, 136, 141, 140, 137, 136, 135` records: min 135,
max 141, median 137.5. Все 369 `(topic, session)` groups целы. Session может
пересекать parts только по границе normalized topic; только один topic
пересекает parts.

## Coverage и provenance

- 1101 records ровно один раз, exact object equality с F2;
- 1067 `used`, 34 `rejected`, 0 `skipped`;
- diagnostics 29 `duplicate-session-holder`, 4 `unmarked-approximate`,
  1 `invalid-type`;
- records SHA-256
  `868ffff05768e4ebac6893436141e99493e0582b6738845350b2aa805e99d69d`;
- coverage SHA-256
  `cbe369994c643fa3f0fddcdea6f107705360b3a6afbd4a6bade4698d4b9d32d2`;
- manifest SHA-256
  `a460a9b8b16fae3797beb1babf58cbafcff38fd0f66cb6be7f96348e16d430b1`;
- parts aggregate SHA-256
  `0f1f060e3cd98d8c16decb1c3255512342abe209a74be2572e305cfdfa48c2d8`.

## Проверка

На интегрированном `main` public `--check` вернул PASS, полный experiment suite
прошёл 43/43. Root отдельно:

- выполнил два fresh public-CLI builds с default inputs и только временным
  output root;
- сравнил оба build друг с другом и с committed artifacts byte-for-byte;
- пересчитал exact F2 object equality, membership, dispositions, diagnostics,
  balance, digests и отсутствие split у 369 groups.

Independent Luna Max auditor `/root/f2_fast_audit` вернул PASS без blockers.
Nested scheme advisor `01a0262c-8aab-7330-b90f-87dab509df30` и holder scout
`01a0262c-8b2e-7b80-b760-ce9c9986662b` завершены. Writer-owned independent
harness после повторных path assumptions объявлен UNKNOWN и не использован;
root заменил его direct public-boundary evidence.

## Frontier

F3 принят как deterministic foundation. Semantic utility partitions не
доказана и остаётся gate Wave 6b. До 6b остаётся F4 synthetic provider canary.
