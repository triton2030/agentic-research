---
kind: module-card
wave: 10
state: planned
role: build-finalizer-and-operations-auditors
system-owner: root
acceptance-review: claude-opus-5
---

# Модуль — full-build operations, coverage и reproducibility

[parent: task.md](../task.md) · вехи 3–4 · gate: Wave 9 PASS

## Contribution

Свести принятые stages в один возобновляемый batch run и доказать exhaustive
coverage, crash recovery, delete-rebuild identity и безопасные private receipts.

## Inputs

- frozen tuples, cumulative chronological run-state и accepted Wave 9 output;
- accepted generated-root ownership/containment contract Wave 5;
- stage validators; provider privacy/cost canary только для external
  provider route, не для owner-authorized local visible Codex route.

## Ownership

- Single finalizer: `scripts/run_full_build.py`, `tests/test_run_state.py`,
  `artifacts/full-build/run-state.json`.
- Coverage auditor: `artifacts/full-build/coverage-final.json`.
- Repro/recovery auditor: stage receipts и reproducibility verdict.
- Root единолично пишет `artifacts/full-build/build-receipt.json` и frozen
  candidate pointer после независимых returns.

Повторяемые mechanical probes могут исполняться Luna Max, но system verdict и
independent falsifier принадлежат root/Opus.

## Run-state contract

- Stage receipt фиксирует input/output/code/prompt/config/model digests, status,
  counts, timings, retries и predecessor tuple.
- Resume разрешён только для `pass` с полным digest match; drift инвалидирует
  stage и всех descendants.
- Crash до atomic publish не оставляет stage `pass` или частично принятый shared
  manifest.
- Новый frozen snapshot пересобирает affected semantic outputs и атомарно
  заменяет Wiki projection; append-only накопление старых страниц запрещено.
- Stale/superseded page исчезает из candidate Wiki, но остаётся трассируемой в
  holders/evidence; unchanged page может переиспользоваться только при полном
  digest match.
- Generated cleanup читает ownership marker, отклоняет traversal/symlink escape
  и никогда не удаляет внешний или unrelated sentinel.
- Receipts не содержат quotes, corpus dumps, API keys или private transcripts.

## Coverage contract

Для каждого frozen record существует ровно одна disposition: `used`, `rejected`
или `skipped` с машинно читаемой причиной. Объединение равно all records;
пересечения, missing IDs, duplicates и silent skips пусты. Derived claims/pages
ссылаются только на frozen quote membership и internal Wiki. Coverage receipt
публикует source quote text, visible Wiki text и compression ratio только как
диагностику; metric не ограничивает page count, file length или total output и
не участвует в PASS/FAIL.

## Falsifying checks

- crash injection после каждого stage и перед atomic rename;
- resume с изменённым input/model/prompt/config/code digest fail;
- clean delete-rebuild даёт byte-identical deterministic artifacts и явно
  классифицирует допустимую semantic nondeterminism;
- adversarial path traversal и symlink sentinel survive;
- secret/private-content scan receipts PASS;
- project-corpus link/access scan и stale-page scan PASS; compression ratio
  записан без threshold;
- coverage set equations PASS на полном snapshot, не sample.

## Budget

Root фиксирует фактические tokens/cost/time по part и total. Cost ceiling из
provider gate является stop rule; его нельзя увеличить writer-ом молча.

## Return

Finalizer возвращает exact command, stage matrix, crash/resume matrix и commit.
Auditors возвращают coverage equations, rebuild digests, containment/privacy
checks и UNKNOWN. Root публикует candidate только если hard FAIL и material
UNKNOWN отсутствуют; иначе сохраняет отказ и закрывает Wave 11.

## Prohibitions

Не переписывать holders, accepted outputs или plan truth для получения зелёного
receipt; не считать наличие файлов доказательством completed build.
