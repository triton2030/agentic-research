---
эпик: "самостоятельный experiment: openviking-chat-recall"
состояние: в работе
режим: Wayfinding
обновлено: 2026-08-21
kind: status
---

# Статус — OpenViking Wiki для chat-recall

## Next

Вторая диагностическая волна: две blind Luna Max руки отвечают на locked вопросы
9 и 11 — одна только по diagnostic Wiki, другая только по six-holder source.
После прямого сравнения решить, заслуживает ли package compatibility seam
отдельной правки. Полный corpus пока не запускать.

## Текущее состояние

- Rationale одобрен владельцем 2026-08-21; approval записан в
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- После approval-capture corpus содержит 182 Markdown holder без `README.md`;
  точный frozen inventory и digest обязан записать writer.
- Stock route выбран как `add-resource` → официальный LLM Wiki Skill →
  `compile`; realtime memory/plugin route исключён.
- Исходные holders остаются source evidence; будущая Wiki — derived projection.
- Graphiti не выполняется как живая pinned задача и остаётся baseline по
  артефактам существующего эксперимента.
- Retrieval denominator locked до чтения Wiki: 11 exact questions, closed gold,
  matched budget, scoring и hard failures записаны в
  `modules/return-wave-1-retrieval-contract.md`.
- Runtime pilot интегрирован commit `d57a49d`: stock Compile blocked HTTP 400
  из-за несовместимости VikingBot/SDK; disposable shim построил diagnostic Wiki
  из семи страниц, но это не stock acceptance.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Pilot runtime | ⚠️ blocked | Stock receipt + diagnostic Wiki: `d57a49d` |
| 2. Pilot audit | ⏳ | Нужны locked questions, ручная сверка и matched run |
| 3. Transition verdict | ⏳ | Нужен прямой ответ на решающий вопрос Wayfinding |
| 4. Full backfill | заблокировано | Только после положительного pilot-verdict |
| 5. Handoff | заблокировано | Только после принятого full audit |

## Активная волна

- `wave-1-runtime-pilot.md` — единственный writer runtime/experiment;
  pinned task `01a023c3-ee43-7c73-964a-08a496494398`,
  «OpenViking: собрать stock pilot»; ✅ return принят, stock gate blocked.
- `wave-1-retrieval-contract.md` — независимый read-only acceptance designer;
  pinned task `01a023c3-ee43-7c73-964a-08b22a2d1b17`,
  «OpenViking: зафиксировать retrieval-контракт»; ✅ locked return принят.
- `wave-2-diagnostic-retrieval.md` — две blind read-only руки; thread registry
  добавляется после запуска.

## Открытые вопросы владельцу

Нет. Для первого pilot принят stock English Wiki с русскими агентными ответами;
русский compile output становится отдельной развилкой только при измеренном
ухудшении.
