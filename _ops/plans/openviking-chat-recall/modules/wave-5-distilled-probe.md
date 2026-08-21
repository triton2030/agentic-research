---
kind: module-card
волна: 5
роль: writer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — representative distilled-knowledge probe

## Outcome

Построить самый маленький исполнимый probe, который на реальных frozen owner
records отделяет current distilled knowledge от полной source chronology.

## Оркестрация

- Сначала `$1orchestration`; внутренние субагенты независимо проверяют frozen
  evidence и semantic/currentness candidate до записи.
- Ты не один в кодовой базе. Не откатывай чужие правки; подстройся под main,
  меняй только перечисленные ownership paths.
- Перед кодом используй `$1codebase-design` и `$1readable-code`; запиши в
  terminal return выбранный seam и falsifying checks.

## Ownership

Только:

- `experiments/openviking-chat-recall/scripts/build_distilled_probe.py`;
- `experiments/openviking-chat-recall/tests/test_build_distilled_probe.py`;
- `experiments/openviking-chat-recall/artifacts/distilled-gold-manifest.json`;
- `experiments/openviking-chat-recall/artifacts/distilled-input/**`;
- `experiments/openviking-chat-recall/artifacts/distilled-wiki/**`;
- `experiments/openviking-chat-recall/artifacts/distilled-probe-receipt.json`;
- `experiments/openviking-chat-recall/artifacts/distilled-probe-receipt.md`.

Не менять README, pyproject/lock, старый typed probe, старые artifacts, `_ops`
или shared hot files. Stdlib only; без network, OpenViking runtime и API.

## Required cases

1. Stable repeated claim.
2. Supersession из frozen
   `_ops/chat-recall/2026-08-20-181330-claude-a7539038.md`: итоговая knowledge
   surface не должна выдавать раннюю отменённую/суженную формулировку за current.
3. Scope-dependent или contested claim; если source не разрешает currentness,
   status остаётся non-current/uncertain.
4. No-gold boundary: unsupported knowledge не появляется.

Используй exact commit карточки как frozen provenance commit, не `HEAD` и не
worktree content. Manifest адресует source path, line, record ID, timestamp,
quote digest и source blob SHA-256. Exact quotes нужны валидатору, но не
копируются в Wiki body.

## Minimal contract

- Evidence владеет membership/count/timestamps/provenance.
- Claim владеет concise statement, applicability, lifecycle status и source
  record IDs. `latest` не вычисляет status.
- Default Wiki body содержит только current/contested distilled knowledge;
  superseded text не печатается как current. Count/first/latest/evolution не
  являются default page content.
- Semantic candidate может быть написан writer-ом, но receipt честно отделяет
  deterministic validation от semantic self-report.

## Falsifying checks

- frozen blob/line/quote drift fail closed;
- неизвестный record ID или lifecycle status fail closed;
- dangling `superseded_by` fail closed;
- exact source quote, count/first/latest/evolution в default Wiki body fail;
- deterministic rebuild byte-identical;
- tests запускаются из clean worktree одной командой, записанной в receipt.

## Return

Сделай один commit только ownership paths. Верни `THREAD_DONE`: commit SHA,
changed files, test command/output, deterministic-vs-semantic boundary,
remaining UNKNOWN и nested-agent receipts.
