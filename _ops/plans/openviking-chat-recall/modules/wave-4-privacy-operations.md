---
kind: module-card
волна: 4
роль: read-only-risk-analyst
модель: gpt-5.6-luna
thinking: max
---

# Модуль — privacy, provenance и recovery

## Outcome

Задать операционные границы полного private-corpus build: какие данные куда
попадают, что логируется, как откатывается/возобновляется run и как Wiki остаётся
удаляемой derived projection, а не второй истиной.

## Оркестрация

- Сначала вызвать `$1orchestration`.
- Внутренние субагенты раздельно проверяют privacy/data flow, provenance/license
  и failure/recovery; агрегатор собирает единый threat/operations contract.

## Ownership

- Репозиторий read-only; никаких правок и коммитов.
- Не читать и не печатать больше corpus content, чем требуется для проверки
  schema/риска; секреты никогда не выводить.

## Ответить

1. Какие классы данных есть в holders и какие из них могут покидать машину?
2. Какие artifacts/logs/checkpoints допустимо коммитить, а какие должны быть
   ignored/local-only?
3. Как provenance проходит от holder record до L2 claim и коротких L1/L0?
4. Как безопасно resume, invalidate stale output, rebuild и удалить projection?

## Return

`THREAD_DONE` с data-flow table, risk register, commit/ignore matrix,
provenance chain, recovery checklist и stop conditions. Только evidence-backed
claims; неизвестное обозначить `UNKNOWN`.
