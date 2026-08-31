# Состояние рефактора — 1document-system v2

## Текущее состояние

`нужен новый commander's intent` — 2026-08-31.

Сохранённого состояния стадии у этого скила не существовало: папок `work/` и
`versions/` в истории не было, последняя запись — рефактор 2026-08-09. Поэтому
вход в `refactor.md` идёт разделом «До нового намерения».

Нумерация версий: `baseline-2026-08-09/` — пакет до первого рефактора,
установленный сейчас пакет считается v1, новый — v2.

## Источники старого пакета

Владелец пакета по реестру `skills/shared/README.md` —
`skills/shared/1document-system/portable/`, а не установленная проекция.
Прочитаны целиком все 24 `.md`; отпечаток — `old-package-fingerprint.txt`
(manifest `5266326f…`).

- `SKILL.md` — 120 строк, разделы Goal · Success criteria · Invariants (9) ·
  Delta (4) · Known failures (8 маршрутов) · Mechanics (4) · Completion.
  Форма канона мета-семьи до `1skill-creation` v13.
- `references/catalog.md` — реестр 15 стандартных типов с authority, домом и
  ссылкой на шаблон; alias-роутинг; гейт допуска нового типа.
- `references/system-mode.md`, `direct-mode.md` — два режима работы.
- `references/topology-contract.md` — зоны `canon/` · `_ops/` ·
  `projections/`, алгоритм папок, роутер.
- `references/metadata-contract.md` — семь полей, description как поверхность
  retrieval, условные поля, approval.
- `references/projections.md` — граница производного вида.
- `references/compaction-safety.md` — 99 строк, защита живого корпуса от
  молчаливой потери при сжатии.
- `references/delegation.md` — гейт fan-out, DAG стадий, контракты воркеров.
- `references/template-*.md` × 15 — DEC · MRD · OPM · SBP · PRD · BRC · SEM ·
  DOM · ARCH · EDD · API · RSP · RPT · EXP · PROC. Инверсия уже применена:
  Purpose · Ban · Non-obvious contracts · Conditional modules · Completion.
- `platforms/codex/agents/openai.yaml` — Codex UI metadata (только у shared
  owner).

История: `origin.md` (триада владельца и карта 8 групп), `cut.md` (карта
потерь рефактора 2026-08-09), `evidence.md` (объём и проверки),
`baseline-2026-08-09/` (пакет до рефактора).

## Наблюдения по старому пакету, влияющие на рефактор

- `SKILL.md` несёт 30 маркеров; даже консервативный счёт (9 инвариантов +
  8 маршрутов + 4 механики) даёт 21 единицу — за бюджетом v13 в 20.
- Пятнадцать шаблонов уже сжаты до неочевидного и в бюджет укладываются.
- Владелец пакета разошёлся со всеми четырьмя проекциями: `catalog.md`,
  `template-brc.md`, `topology-contract.md` у shared owner называют
  `1instruction-authoring`, а установленные копии и оба tracked runtime —
  несуществующий `1instruction-placement`. Закрывается установкой нового
  пакета.

## Буквальные слова владельца

Собраны в `user-said.md` папки-истории.
