---
kind: module-card
волна: 4
роль: independent-acceptance-designer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — full compiler acceptance

## Outcome

Расширить закрытый pilot contract до falsifying acceptance полного compiler:
coverage, exact recurrence, chronology, contradictions, unsupported claims и
реальная экономия чтений/context против holders.

## Оркестрация

- Сначала вызвать `$1orchestration`.
- Внутренние субагенты независимо проектируют deterministic, semantic и
  retrieval/cost axes; агрегатор ищет способы случайно «натренироваться» на gold.

## Ownership

- Репозиторий read-only; никаких правок и коммитов.
- Сначала читать locked Wave 1 contract и holders/gold, не будущую Wiki.
- Не менять вопросы после просмотра candidate output.

## Ответить

1. Какие executable invariants доказывают 100% addressed coverage и exact facts?
2. Как выбрать representative и held-out cases без leakage?
3. Как одинаково измерить correctness, chronology, citations, reads, tokens,
   latency и false confidence для holders и Wiki?
4. Какой pass threshold и hard failures допускают либо запрещают agent route?

## Return

`THREAD_DONE` с immutable questions/gold addresses, scoring, matched budget,
hard failures, run order и форматом machine-readable verdict. Candidate Wiki не
оценивать в этой волне.
