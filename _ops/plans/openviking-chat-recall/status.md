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

Дождаться шести Luna Max read-only returns, проверить evidence и расхождения
между зонами, затем свести их в один непротиворечивый contract вехи 1. Только
после этого root открывает file-disjoint writer-волну вехи 2.

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

| Task | Title | Card | Worktree | State |
| --- | --- | --- | --- | --- |
| `01a0248f-9a1b-71d0-ac76-9c9247e0d23d` | OpenViking: карта корпуса | `wave-4-corpus-map.md` | `25bc` | active |
| `01a0248f-9a14-7a53-877a-56a4f0acb12a` | OpenViking: seam компилятора | `wave-4-compiler-seam.md` | `1b54` | active |
| `01a02490-90e6-7a71-8120-8451f7ad4016` | OpenViking: prompt и IA | `wave-4-openviking-ia.md` | `93c9` | active |
| `01a0248f-9a1b-71d0-ac76-9c52161efcf2` | OpenViking: LLM route | `wave-4-llm-route.md` | `2901` | active |
| `01a0248f-9a14-7a53-877a-568219d57716` | OpenViking: acceptance contract | `wave-4-acceptance.md` | `2e80` | active |
| `01a0248f-9a1b-71d0-ac76-9c7d8ac02686` | OpenViking: privacy и recovery | `wave-4-privacy-operations.md` | `b2e6` | active |

Все треды запущены на `gpt-5.6-luna/max`, обязаны использовать
`$1orchestration` и внутренний fan-out. Репозиторий для них read-only; запись
returns и `observations/` остаётся у root.

## Блокеры

Нет owner-блокера. До writer-волны должен быть принят один contract вехи 1;
это dependency gate, а не запрос решения владельцу.
