---
kind: module-card
волна: 5
роль: read-only-contract-red-team
модель: gpt-5.6-luna
thinking: max
---

# Модуль — red-team distilled claim contract

## Outcome

До интеграции probe найти один минимальный counterexample, на котором граница
`holders → evidence → claims → Wiki` уверенно выдаст stale, merged или
неприменимое знание, хотя все record IDs формально валидны.

## Оркестрация

- Сначала `$1orchestration`; внутренние субагенты отдельно атакуют semantic
  grouping, currentness/scope и reader routing.
- Репозиторий строго read-only; ничего не редактировать и не коммитить.

## Смотреть

- `_ops/plans/openviking-chat-recall/task.md`;
- `_ops/plans/openviking-chat-recall/context.md`;
- `_ops/plans/openviking-chat-recall/modules/_returns/fresh-eyes-distilled-knowledge.md`;
- `experiments/openviking-chat-recall/scripts/build_typed_probe.py`;
- `experiments/openviking-chat-recall/tests/test_build_typed_probe.py`;
- representative holders, выбранные из `_ops/chat-recall/` по source-bound
  addresses.

Будущий distilled candidate другого треда не читать: это contract review, не
post-hoc critique.

## Return

`THREAD_DONE`: strongest counterexample с source address, cheapest falsifying
test, какой field/route действительно нужен, какая предлагаемая сложность не
нужна, ближайшая альтернатива, UNKNOWN и nested-agent receipts. Self-report или
один smooth example не evidence.
