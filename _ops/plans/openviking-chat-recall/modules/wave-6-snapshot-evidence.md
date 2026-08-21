---
kind: module-card
wave: 6
state: planned
role: deterministic-foundation-writers
model: gpt-5.6-luna
thinking: max
---

# Модуль — frozen snapshot и evidence foundation

[parent: task.md](../task.md) · веха 2 · gate: accepted Wave 5 G0

## Contribution

Зафиксировать полный корпус одним explicit Git commit и превратить его в
детерминированный record/evidence layer со стабильными semantic partitions.
Карточка не разрешает исполнение, пока status.md не закрыл G0.

## Inputs

- exact corpus commit, выбранный root после принятия G0;
- действующий holder parser и правила `_ops/chat-recall/`;
- accepted distilled-claim contract и provider privacy fixture.

Планировочный baseline `a77fc4c` с 180 holders / 1074 records не является
автоматическим full-build snapshot.

## Dependencies

F1 frozen corpus lock → F2 records/evidence → F3 stable partitions. F2 не
читает live directory; F3 не меняет evidence-поля и не вызывает модель.

## Ownership

Три file-disjoint Luna Max writers, каждый с собственным nested read-only
checker:

- F1: `scripts/freeze_corpus.py`, `tests/test_freeze_corpus.py`,
  `artifacts/full-build/frozen/source-manifest.json`, `source-lock.json`;
- F2: `scripts/build_evidence_layer.py`, `tests/test_evidence_layer.py`,
  `artifacts/full-build/evidence/records.jsonl`, `coverage-input.json`;
- F3: `scripts/build_cluster_proposals.py`, `tests/test_cluster_proposals.py`,
  `artifacts/full-build/clusters/partition-manifest.json`,
  `artifacts/full-build/clusters/part-*/input.jsonl`.

Shared manifests интегрирует только root после независимой проверки returns.

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
- snapshot из live dirty tree отклоняется;
- synthetic provider canary доказывает auth, egress, logging, retry, cost и
  secret redaction до передачи реального holder content.

## Budget

Stdlib/deterministic work не тратит model tokens. Fan-out ограничен тремя
ownership zones; root останавливает волну при первом upstream FAIL.

## Return

Каждый writer возвращает commit SHA, exact changed paths, counts/digests,
test command/output, rejected inputs и nested-agent receipt. Root записывает
единый Wave 6 verdict; UNKNOWN не открывает Wave 7.

## Prohibitions

Не менять holders, prompt contracts, Wiki pages, plan/status или downstream
artifacts; не нормализовать и не чинить source text молча.
