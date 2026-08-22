---
kind: module-card
wave: "6e"
state: ready
role: blind-index-first-reader
model: gpt-5.6-luna
thinking: max
---

# Модуль — blind findability текущей Wiki

[parent: task.md](../task.md) · independent read-only reader · вопросы frozen
до чтения batch-002 draft]

## Outcome

Проверить, может ли чистый агент по одному `index.md` быстро выбрать нужную
страницу, а затем восстановить действие и границу без чтения source quotes.
Это evidence findability текущего owner-liked checkpoint, не оценка writer-а.

## Allowed surface

Только
`experiments/openviking-chat-recall/artifacts/chronological-pilot/current/wiki/**`.
Reader не читает holders, plans, batch manifests, changesets, receipts, Git
history или project knowledge. Ничего не пишет и не запускает subagents.

## Frozen questions

1. Мне нужно сохранить важные слова владельца из старого чата так, чтобы их
   потом нашли. Что обязательно записать и чего нельзя подменять пересказом?
2. Можно ли руководствоваться найденной старой репликой как актуальной
   инструкцией, если она ближе всех к вопросу?
3. Мы пишем общее правило для разных агентов, но они его не вызывают вовремя.
   Что должно быть видно до вызова и как проверить результат?
4. Векторный поиск показал два очень похожих текста. Достаточно ли этого, чтобы
   объявить их смысловыми дублями?

## Blind protocol

1. Открой только `index.md`.
2. До чтения любой knowledge page зафиксируй first-choice page для всех четырёх
   вопросов и краткий cue из index, который привёл к выбору.
3. Затем для каждого вопроса открой только выбранную page; дополнительную page
   открывай лишь при явном gap и назови причину.
4. Ответь по-русски: действие/вывод, ключевая граница, page path, число page
   reads. Не открывай Sources targets.

## Return

Один `THREAD_DONE`: четыре first choices, четыре bounded answers, wrong-first
choices, total Wiki reads, gaps и точный список открытых paths. Self-report о
findability без precommitted choices не принимается. Thread bounded и после
root-приёмки архивируется.
