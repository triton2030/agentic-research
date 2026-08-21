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

Закрыть три follow-up gap: точные L0/L1 prompt templates, совместный
Wiki-L2/Context-L0-L1 seam и execution route для текущего корпуса против
будущего reusable tool. После независимой сверки root фиксирует contract вехи
1 и открывает file-disjoint writer-волну вехи 2.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Контракты | в работе | Шесть Wave 4 returns + три карточки `wave-4b-*.md` |
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
| `01a024a2-245a-7a91-95c2-d5cacb530c76` | OpenViking: L0 L1 prompts | `wave-4b-context-layer-prompts.md` | `a5dc` | active |
| `01a024a2-245a-7a91-95c2-d58e0db293a2` | OpenViking: layered seam | `wave-4b-layered-seam.md` | `aa2d` | active |
| `01a024a2-245a-7a91-95c2-d5aeba7a18cc` | OpenViking: generation execution | `wave-4b-generation-execution.md` | `57af` | active |

Все три — `gpt-5.6-luna/max`, read-only, с обязательным nested
`$1orchestration`. Root принимает returns и единолично пишет plan/observations.

## Блокеры

Нет owner-блокера. До writer-волны должен быть принят один contract вехи 1;
это dependency gate, а не запрос решения владельцу.
