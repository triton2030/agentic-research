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

Заморозить исправленный contract знания и провести один representative
supersession probe: Wiki должна вернуть текущий дистиллированный факт, не
пересказывать историю и адресно раскрыть holders при проверке. Только после
этого root закрывает contract вехи 1 и открывает file-disjoint writer-волну.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Контракты | в работе | Wave 4/4b returns + Fresh Eyes correction; ждёт supersession probe |
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
- Владелец затем снял chronology-heavy Wiki: источники сохраняют историю, а
  Wiki хранит дистиллированные знания. Fresh Eyes route записан в
  `modules/_returns/fresh-eyes-distilled-knowledge.md`.

## Wave 4 registry

| Task | Title | Card | Worktree | State |
| --- | --- | --- | --- | --- |
| `01a0248f-9a1b-71d0-ac76-9c9247e0d23d` | OpenViking: карта корпуса | `wave-4-corpus-map.md` | `25bc` | terminal candidate |
| `01a0248f-9a14-7a53-877a-56a4f0acb12a` | OpenViking: seam компилятора | `wave-4-compiler-seam.md` | `1b54` | terminal candidate |
| `01a02490-90e6-7a71-8120-8451f7ad4016` | OpenViking: prompt и IA | `wave-4-openviking-ia.md` | `93c9` | terminal candidate |
| `01a0248f-9a1b-71d0-ac76-9c52161efcf2` | OpenViking: LLM route | `wave-4-llm-route.md` | `2901` | terminal candidate |
| `01a0248f-9a14-7a53-877a-568219d57716` | OpenViking: acceptance contract | `wave-4-acceptance.md` | `2e80` | terminal candidate |
| `01a0248f-9a1b-71d0-ac76-9c7d8ac02686` | OpenViking: privacy и recovery | `wave-4-privacy-operations.md` | `b2e6` | terminal candidate |

Все треды запущены на `gpt-5.6-luna/max`, обязаны использовать
`$1orchestration` и внутренний fan-out. Репозиторий для них read-only; запись
returns и `observations/` остаётся у root.

Wave 4 закончена как candidate: все шесть top-level returns terminal. Root
независимо подтвердил baseline `180 holders / 1072 records`, stale committed
inventory `182`, typed tests `5/5`, текущий Codex CLI surface и разделение
upstream owners. Веха ещё не закрыта из-за трёх Wave 4b gaps.

## Wave 4b registry

| Task | Title | Card | Worktree | State |
| --- | --- | --- | --- | --- |
| `01a024a2-245a-7a91-95c2-d5cacb530c76` | OpenViking: L0 L1 prompts | `wave-4b-context-layer-prompts.md` | `a5dc` | terminal candidate |
| `01a024a2-245a-7a91-95c2-d58e0db293a2` | OpenViking: layered seam | `wave-4b-layered-seam.md` | `aa2d` | terminal candidate |
| `01a024a2-245a-7a91-95c2-d5aeba7a18cc` | OpenViking: generation execution | `wave-4b-generation-execution.md` | `57af` | terminal candidate |

Все три — `gpt-5.6-luna/max`, read-only, с обязательным nested
`$1orchestration`. Root принимает returns и единолично пишет plan/observations.

Wave 4b закончена как candidate. Root подтвердил: L1 sidecar использует
`overview_generation.yaml`; L0 directory abstract извлекается из `Brief
Description` L1; `context_generation.yaml` не является прямым sidecar prompt.
Контракт записан в `modules/_returns/wave-4b-contracts.md`.

## Wave 5 registry

| Task | Title | Card | State |
| --- | --- | --- | --- |
| `01a024c0-0f08-7870-85ef-d9d0b1784da5` | OpenViking: distilled probe | `wave-5-distilled-probe.md` | active |
| `01a024c0-0f10-7f02-b209-d0524247d432` | OpenViking: acceptance lock | `wave-5-distilled-acceptance.md` | active |
| `01a024c0-0f0e-7220-861e-aeb7f67e570d` | OpenViking: contract red-team | `wave-5-distilled-red-team.md` | active |

Все три запускаются на `gpt-5.6-luna/max`. Каждый top-level тред обязан сначала
использовать `$1orchestration` и разделить свою карточку между внутренними
субагентами. Writers владеют непересекающимися файлами; red-team read-only.

## Блокеры

Нет owner-блокера. До writer-волны должен быть принят один contract вехи 1;
это dependency gate, а не запрос решения владельцу.
