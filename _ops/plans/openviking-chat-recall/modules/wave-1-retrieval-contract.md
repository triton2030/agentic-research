---
kind: module-card
волна: 1
роль: independent-reviewer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — locked retrieval и recurrence contract

## Outcome

До просмотра будущей Wiki зафиксировать независимый набор вопросов и ручной
эталон, который может опровергнуть полезность OpenViking для этого корпуса.

## Ownership

- Read-only ко всему репозиторию; никаких правок и коммитов.
- Не один в кодовой базе: не интерпретировать появившиеся runtime-файлы как
  собственное задание и не менять их.

## Inputs

- `_ops/plans/openviking-chat-recall/{task,status,context}.md`
- `_ops/chat-recall/**`
- существующие retrieval cases и Graphiti experiment только как evidence.
- Не читать output Wiki, пока не зафиксирован набор вопросов и gold addresses.

## Делает

1. Выбирает 8–12 вопросов, покрывающих repetition count, first/latest,
   contradiction, current position, method, preference и cross-topic synthesis.
2. Для каждого фиксирует gold holder addresses и допустимую неопределённость.
3. Задаёт одинаковый budget для source holders, Graphiti и Wiki: число
   discovery/read операций, время, tokens/context и формат ответа.
4. Задаёт scoring до run: factual correctness, provenance, chronology,
   current-vs-historical application и false confidence.
5. Возвращает self-contained locked contract в final; не оценивает ещё не
   построенную Wiki.

## Не делает

- Не улучшает запросы после просмотра результатов.
- Не считает внутренние IDs преимуществом.
- Не пишет summaries корпуса и не проектирует альтернативную Wiki.

## Done evidence

- Полный список questions + gold addresses.
- Budget и формула scoring.
- Явные failure conditions для stock pilot.
- Перечень скрытых данных, которые не должны видеть будущие руки.
