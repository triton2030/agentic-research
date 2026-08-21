---
kind: module-return
wave: 6
stage: F2-evidence-layer
state: accepted
date: 2026-08-22
---

# Wave 6 F2 — deterministic evidence layer

## Результат

Visible Luna Max task `01a025ef-35d5-7791-a2c8-323259126faa` построил F2 из
accepted F1 lock и Git objects exact corpus commit
`6f98fcccdbf4b4de45ef787239ad101f70d106e2`. Candidate `33ac583` интегрирован
в `main` как `ea569e2`.

Exact ownership:

- `experiments/openviking-chat-recall/scripts/build_evidence_layer.py`;
- `experiments/openviking-chat-recall/tests/test_evidence_layer.py`;
- `experiments/openviking-chat-recall/artifacts/full-build/evidence/records.jsonl`;
- `experiments/openviking-chat-recall/artifacts/full-build/evidence/coverage-input.json`.

`records.jsonl` — private evidence surface с quote, text, metadata и точным
Git provenance. `coverage-input.json` не содержит quote/text/metadata и
перечисляет каждый record ровно один раз.

| Поле | Значение |
| --- | --- |
| holder files | 184 |
| unique records / coverage entries | 1101 / 1101 |
| dispositions | 1067 `used`, 34 `rejected`, 0 `skipped` |
| diagnostics | 29 `duplicate-session-holder`, 4 `unmarked-approximate`, 1 `invalid-type` |
| records SHA-256 | `868ffff05768e4ebac6893436141e99493e0582b6738845350b2aa805e99d69d` |
| coverage SHA-256 | `cbe369994c643fa3f0fddcdea6f107705360b3a6afbd4a6bade4698d4b9d32d2` |
| writer SHA-256 | `467d4247538fa06182d059118f049483bf872c25f414922933a55d31bda52f12` |

Все 34 diagnostic records сохраняют exact source address и typed reason, но
не допускаются как accepted knowledge. Отдельного повторного diagnostic list
нет.

## Проверка

Writer и root независимо выполнили:

- F2 targeted suite — 8/8 PASS;
- полный `experiments/openviking-chat-recall/tests` suite — 32/32 PASS;
- committed-output `--check` — PASS;
- два fresh builds — byte-identical, unrelated output сохранён;
- exact-one JSON audit — 1101 unique IDs в records и coverage, одинаковый set;
- dirty и даже отсутствующий live holder directory не меняют output;
- HEAD/short SHA, F1 manifest drift, output drift и owned-output symlink
  отклоняются fail closed.

Nested Luna Max auditor `01a025f1-c6cb-7b63-8603-84c52afb5923` завершился как
incomplete advisory и не использован как acceptance evidence.

## Audit conflict и adjudication

Первый independent auditor `/root/f1_acceptance` дал FAIL: общий Wave 6 bullet
про dirty snapshot был прочитан как обязанность F2 падать при dirty live
holder. Второй independent Luna Max auditor `/root/f2_fast_audit` проверил
ownership и показал, что этот gate принадлежит F1: F2 по контракту не читает
live directory и должен быть инвариантен к нему. Он подтвердил byte-identical
build даже при удалённой live `_ops/chat-recall` и вернул F2 PASS.

Root принял adjudication: F1 отклоняет dirty source snapshot до lock; F2
отклоняет drift F1 lock/Git objects, но не вводит зависимость от текущего live
tree. Read-only symlink ancestry frozen input не является F2 acceptance gate:
input digests проверяются, а F2 туда не пишет.

## Frontier

F2 принят. F3 строит только deterministic partition proposals из этого
evidence layer, не меняет evidence fields и не вызывает модель.
