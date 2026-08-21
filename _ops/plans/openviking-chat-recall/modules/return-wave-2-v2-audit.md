---
kind: module-return
волна: 2
variant: diagnostic-v2
состояние: failed
записано: 2026-08-21
---

# Return — V2 semantic audit

## Verdict

V2 не готова к full backfill: recurrence audit дал `4 FAIL · 1 UNKNOWN · 1
PASS`; blind reader снова не восстановил current OpenViking outcome. Stock
runtime отдельно остаётся blocked несовместимостью VikingBot/SDK.

Threads:

- Blind v2 Wiki: `01a023fa-177f-7010-8e1f-121ccd352951`.
- Semantic audit: `01a023fa-1782-7563-979e-74a6428dde87`.

Оба были read-only. Blind arm видел только V2 pages; auditor — V2, selection и
six-holder corpus.

## Blind questions 9 и 11

На current OpenViking outcome blind V2 arm ответил `mixed`: OpenViking —
retrieval/discovery layer, не заменяющий owner evidence. Он не назвал документы
и отчёты, фиксацию повторов, static old-folder backfill, parallel folder,
почти полное использование технологии и проверку удобства агентам.

На no-gold prompt/config control он дал `abstain`; calibration pass.

Blind duration — 154.9 секунды при budget 120 секунд; efficiency не принята.

## Manual recurrence audit

| Canonical section | Verdict | Evidence result |
| --- | --- | --- |
| Dated shortened quotes | UNKNOWN | Count 3 верен для July cluster; later exact-words tension не adjudicated |
| Global and automatic skill | FAIL | Count 2; пропущены later H3/H4/H5 records, latest stale |
| Store in `_ops/chat-recall` | PASS | Count 2 и earliest/latest подтверждены direct owner records |
| Search aids route, not prove | FAIL | Count 3; actual direct count 4 |
| Backfill reads real sessions | FAIL | Count 2 включает context-only claim; direct exact claim один, earliest неверен |
| Simple runtime/no unproven claims | FAIL | Count 4; пропущен fifth direct simplification record, latest stale |

Главный повторяющийся дефект: модель считает semantically related records
неполно и иногда превращает `context-note` в owner evidence. Наличие полей и
source links не доказывает правильность count.

## Outcome omission и inversion

Frozen owner holder требует:

- отдельные документы/отчёты вместо цитирования цитат;
- фиксацию повторяемости, first/latest и развития позиции;
- static backfill старой папки в parallel folder;
- почти полное использование OpenViking prompts/IA/technology;
- проверку удобства поиска агентами;
- неизменяемые sources и derived Wiki.

V2 outcome page не переносит эти требования и переопределяет результат прежде
всего как retrieval aid. Valid boundary «Wiki не заменяет evidence» превращён в
сам outcome — semantic inversion.

## Snapshot integrity

Selection фиксирует H6 SHA
`c92addebb7e56454bb848a935f2bdfe6408f9b6949248c1ca56dd06ec0502443`,
5 239 bytes, 23 lines. Этот exact object восстанавливается из commit `919e0de`.
Live holder после approval-selection имеет SHA
`97b3a2f9768e1f677a3cc921cab559c04c9046b04d95ee61ee71bf9f55848c4b`,
9 240 bytes, 24 lines. Исходные owner records outcome сохранились; append не
объясняет omission V2.

## Stop

Не запускать full corpus и не объявлять diagnostic shim production route.
Следующий ход требует выбора владельца: минимально обернуть OpenViking
deterministic record/count validation или отказаться от runtime-библиотеки и
использовать её официальный Wiki Skill/IA в собственном compiler pipeline.
