---
kind: module-card
wave: 6
state: active
role: deterministic-foundation-writers
model: gpt-5.6-luna
thinking: max
---

# Модуль — frozen snapshot и evidence foundation

[parent: task.md](../task.md) · веха 2 · gate: accepted Wave 5 semantic contract

## Contribution

Зафиксировать полный корпус одним explicit Git commit и превратить его в
детерминированный record/evidence layer со стабильными semantic partitions.
Pre-build utility PASS не является dependency: полезность измеряется после
representative ingestion в Wave 6b.

## Inputs

- exact corpus commit
  `6f98fcccdbf4b4de45ef787239ad101f70d106e2`, выбранный root после принятия
  semantic contract;
- действующий holder parser и правила `_ops/chat-recall/`;
- accepted distilled-claim contract и provider privacy fixture.

Планировочный baseline `a77fc4c` с 180 holders / 1074 records не является
автоматическим full-build snapshot.

## Selected source frontier

Commit `6f98fcc` содержит 184 holder files и 1101 parsed records. Non-strict
structural check завершился с 34 diagnostics: 29 `duplicate-session-holder`,
4 `unmarked-approximate` и 1 `invalid-type`. Snapshot сохраняет их дословно;
F1/F2 обязаны адресовать diagnostics и передать каждому record явный
coverage-disposition, а не исключать файл или чинить source молча.

## Dependencies

F1 frozen corpus lock → F2 records/evidence → F3 stable partitions. F2 не
читает live directory; F3 не меняет evidence-поля и не вызывает модель. F4
synthetic provider canary идёт отдельной веткой после pinned execution seam.
Wave 6 PASS требует F1 + F2 + F3 + F4.

## Ownership

Четыре file-disjoint Luna Max writers, каждый с собственным nested read-only
checker:

- F1: `scripts/freeze_corpus.py`, `tests/test_freeze_corpus.py`,
  `artifacts/full-build/frozen/source-manifest.json`, `source-lock.json`;
- F2: `scripts/build_evidence_layer.py`, `tests/test_evidence_layer.py`,
  `artifacts/full-build/evidence/records.jsonl`, `coverage-input.json`;
- F3: `scripts/build_cluster_proposals.py`, `tests/test_cluster_proposals.py`,
  `artifacts/full-build/clusters/partition-manifest.json`,
  `artifacts/full-build/clusters/part-*/input.jsonl`.
- F4: отдельная card
  [wave-6-provider-canary](./wave-6-provider-canary.md), writer/test и dedicated
  `artifacts/full-build/provider-canary/**`.

Shared manifests интегрирует только root после независимой проверки returns.

## Execution state

- F1 accepted на `main` commits `acb3def` + `31c8a4f`; exact return —
  [_returns/wave-6-f1-source-lock](./_returns/wave-6-f1-source-lock.md).
- F2 accepted на `main` commit `ea569e2`; exact return —
  [_returns/wave-6-f2-evidence-layer](./_returns/wave-6-f2-evidence-layer.md).
- F3 accepted на `main` commit `c5bbe41`; exact return —
  [_returns/wave-6-f3-stable-partitions](./_returns/wave-6-f3-stable-partitions.md).
- F4 next: synthetic provider canary; реальные holders запрещены.

## Contract

- Source lock содержит commit, path, blob SHA-256 и parser/config/code digests.
- Каждый валидный source record получает стабильный record ID и точный source
  address; полные quotes не попадают в публичные receipts.
- `coverage-input.json` перечисляет каждый record ровно один раз до semantic
  обработки.
- Partition ID вычисляется детерминированно; один record принадлежит ровно
  одному part. Перезапуск не меняет membership или порядок.
- Никаких абсолютных worktree paths, `HEAD`, mtime или live-file fallback.

## Falsifying checks

- commit/blob/line/timestamp/record drift fail closed;
- missing, duplicate или cross-part record fail;
- два fresh builds byte-identical;
- F1 отклоняет dirty source snapshot до lock; F2 игнорирует live tree и
  доказывает byte-identical output из accepted lock/Git objects;
- synthetic provider canary доказывает auth, egress, logging, retry, cost и
  secret redaction до передачи реального holder content.

## Budget

Stdlib/deterministic work не тратит model tokens. Fan-out ограничен четырьмя
ownership zones; root останавливает волну при первом upstream FAIL.

## Return

Каждый writer возвращает commit SHA, exact changed paths, counts/digests,
test command/output, rejected inputs и nested-agent receipt. Root записывает
единый Wave 6 verdict; UNKNOWN не открывает Wave 7.

## Prohibitions

Не менять holders, prompt contracts, Wiki pages, plan/status или downstream
artifacts; не нормализовать и не чинить source text молча.
