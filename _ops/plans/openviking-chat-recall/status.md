---
эпик: "самостоятельный experiment: openviking-chat-recall"
состояние: в работе
режим: Execution
вех-готово: 0
вех-всего: 5
обновлено: 2026-08-21
kind: status
---

# Статус — batch compiler знаний

## Next

Запустить шесть Luna Max read-only тредов в worktrees. Каждый использует
`$1orchestration` и делит свою зону между внутренними субагентами. Root сводит
их returns в один непротиворечивый contract и только после этого открывает
writer-волну вехи 2.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Контракты | в работе | Шесть карточек `modules/wave-4-*.md` |
| 2. Compiler | ожидает | После принятого seam и file-disjoint writer cards |
| 3. Full build | ожидает | После sample gates вехи 2 |
| 4. Normalize | ожидает | После coverage-complete full build |
| 5. Acceptance | ожидает | После frozen candidate Wiki |

## Текущая доказательная база

- Stock OpenViking runtime отклонён как рабочий route: health/resource import
  работали, но SDK skill upload и Compile расходились; receipt:
  `experiments/openviking-chat-recall/artifacts/wave-3-receipt.md`.
- Typed-evidence candidate `9319f71`: 5/5 tests, byte-identical rebuild и exact
  count/first/latest на frozen records.
- Blind Luna Max reader восстановил exact recurrence и пять обязательств из
  трёх Wiki pages; return:
  `modules/return-wave-3-typed-evidence-probe.md`.
- Владелец после split verdict утвердил custom compiler и текущую схему
  оркестрации; точные слова записаны в holder, указанный в `task.md`.

## Wave 4 registry

Пока не запущено. Registry заполняет только root после фактического создания
тредов: task ID, title, card, worktree и итоговый lifecycle state.

## Блокеры

Нет owner-блокера. До writer-волны должен быть принят один contract вехи 1;
это dependency gate, а не запрос решения владельцу.
