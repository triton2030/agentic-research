---
kind: module-card
волна: 2
режим: diagnostic
модель: gpt-5.6-luna
thinking: max
---

# Модуль — blind diagnostic двух pilot arms

## Outcome

Проверить, помогает ли diagnostic Wiki агенту ответить хотя бы на два exact
locked вопроса, полностью допустимых для six-holder pilot, прежде чем решать,
стоит ли чинить package compatibility seam.

Это не full matched benchmark и не stock acceptance. Остальные девять locked
вопросов требуют источников вне pilot и сейчас не запускаются.

## Общий контракт

Обе руки получают дословно одинаковые вопросы:

1. Какую задачу владелец хочет решить с помощью OpenViking для chat-recall и
   какие границы этой работы он обозначил?
2. Какой именно системный промпт stock OpenViking и какая русскоязычная
   конфигурация компиляции выбраны владельцем?

На вопрос — максимум три discovery operation, шесть evidence reads, 120 секунд,
250 слов. Query rewriting и повтор после результата запрещены.

Ответ каждой руки:

```json
{
  "answer": "...",
  "status": "current|historical|mixed|not_found|abstain",
  "claims": [{"text": "...", "sources": ["..."]}],
  "confidence": "high|medium|low|abstain",
  "gaps": [],
  "operations": []
}
```

## Wiki arm

- Видит только `experiments/openviking-chat-recall/artifacts/wiki/**`.
- Не читает source holders, plan, receipt, selection, Graphiti или gold.
- Источники в ответе — Wiki pages, которые рука реально прочитала.

## Source arm

- Видит только шесть filenames из
  `experiments/openviking-chat-recall/artifacts/pilot-selection.json`,
  раскрывая соответствующие `_ops/chat-recall/<filename>`.
- Не читает Wiki, plan, receipt, Graphiti или locked gold.
- Источники в ответе — holders, которые рука реально прочитала.

## После рук

Root оценивает ответы по already-locked gold вопросов 9 и 11. Hard failure:
уверенный ответ на вопрос 11, выдуманный source, нераскрытая страница/holder
или неспособность Wiki найти outcome, который присутствует в pilot source.

## Done evidence

- Два независимых thread finals без перекрёстного чтения.
- Exact answers, sources, gaps и operations обеих рук.
- Root verdict ограничен этими двумя вопросами и не выдаётся за full audit.
