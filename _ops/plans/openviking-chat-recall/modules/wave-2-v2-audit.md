---
kind: module-card
волна: 2
variant: diagnostic-v2
модель: gpt-5.6-luna
thinking: max
---

# Модуль — v2 blind retrieval и semantic audit

## Outcome

Проверить, изменил ли exact compile reason не только форму V2 Wiki, но и
семантическую корректность recurrence и текущего OpenViking outcome.

## Blind Wiki arm

- Видит только `experiments/openviking-chat-recall/artifacts/wiki-v2/**`.
- Получает exact locked вопросы 9 и 11 из предыдущей diagnostic wave с теми же
  budget, schema и запретами.
- Не читает v1, holders, selection, receipt, plan, Graphiti или gold.
- Source baseline не повторяется: принят return предыдущей source arm.

## Semantic auditor

- Видит только V2 Wiki, `pilot-selection.json` и шесть selected holders.
- Для каждой из шести canonical recurrence sections перечисляет exact records,
  вручную пересчитывает count и проверяет earliest/latest/current/contradiction.
- Ищет semantically equivalent records в остальных selected holders, которые
  V2 могла пропустить.
- Сверяет outcome page со всеми записями holder
  `2026-08-21-133152-codex-01a0236d.md`, особенно с поздними коррекциями.
- Не читает plan, receipt, v1, Graphiti, locked gold или другие holders.
- Read-only; ничего не создаёт и не коммитит.

## Gate

V2 diagnostic не заслуживает full backfill или compatibility patch, если:

- blind arm снова не находит current OpenViking outcome;
- хотя бы один count/first/latest не подтверждается exact source records;
- outcome page превращает коррекцию про документы и повторения обратно в один
  лишь retrieval/navigation aid;
- confident claim выводится из agent context вместо owner record.

Это diagnostic verdict, не full-corpus acceptance.
