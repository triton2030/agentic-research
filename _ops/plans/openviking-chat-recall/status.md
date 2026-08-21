---
эпик: "самостоятельный experiment: openviking-chat-recall"
состояние: в работе
режим: Wayfinding
обновлено: 2026-08-21
kind: status
---

# Статус — OpenViking Wiki для chat-recall

## Next

Первая волна: Luna Max writer поднимает изолированный stock runtime и получает
representative Wiki; параллельный Luna Max reviewer фиксирует retrieval-набор и
falsifying acceptance до просмотра результата. Полный corpus пока не запускать.

## Текущее состояние

- Rationale одобрен владельцем 2026-08-21; approval записан в
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- На момент планирования corpus содержит 181 Markdown holder; точный frozen
  inventory обязан пересчитать writer.
- Stock route выбран как `add-resource` → официальный LLM Wiki Skill →
  `compile`; realtime memory/plugin route исключён.
- Исходные holders остаются source evidence; будущая Wiki — derived projection.
- Graphiti не выполняется как живая pinned задача и остаётся baseline по
  артефактам существующего эксперимента.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Pilot runtime | ⏳ | Нужны runtime receipt, inventory и Wiki tree |
| 2. Pilot audit | ⏳ | Нужны locked questions, ручная сверка и matched run |
| 3. Transition verdict | ⏳ | Нужен прямой ответ на решающий вопрос Wayfinding |
| 4. Full backfill | заблокировано | Только после положительного pilot-verdict |
| 5. Handoff | заблокировано | Только после принятого full audit |

## Активная волна

- `wave-1-runtime-pilot.md` — единственный writer runtime/experiment;
  pinned task `01a023c3-ee43-7c73-964a-08a496494398`,
  «OpenViking: собрать stock pilot».
- `wave-1-retrieval-contract.md` — независимый read-only acceptance designer;
  pinned task `01a023c3-ee43-7c73-964a-08b22a2d1b17`,
  «OpenViking: зафиксировать retrieval-контракт».

## Открытые вопросы владельцу

Нет. Для первого pilot принят stock English Wiki с русскими агентными ответами;
русский compile output становится отдельной развилкой только при измеренном
ухудшении.
