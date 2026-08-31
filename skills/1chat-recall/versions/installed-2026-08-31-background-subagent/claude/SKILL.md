---
name: 1chat-recall
description: >-
  When owner speech needs attention.
allowed-tools: Bash Read Glob Grep Agent
---

# Память чата

## Цель

Помочь агенту восстановить применимую позицию владельца из ранее сохранённых
цитат и продолжить текущую работу без повторного расспроса. Если evidence
недостаточно или его применимость неясна — вернуть gap.

## Уникальный контекст

Корпус состоит из файлов сохранённых цитат: один файл на разговор. `topics.md`,
`session-context` и `context-note` помогают найти нужный файл и цитату, но сами
не являются словами владельца. Когда значение зависит от сцены или хронологии,
агент читает выбранный файл цитат целиком. Позднее слово или действующий owner
могут изменить прежнюю позицию; Retrieval показывает каждой цитате абсолютную
дату и возраст, а same-scope `supersedes` оставляет действующей новую. Обычный
поиск читает только сохранённый корпус, а не native transcript Claude или Codex.
User-visible carrier не доказывает авторство: tool-sent agent follow-up не
является owner speech.

## Режим

- Материальная речь либо `capture-needed` → [Capture](references/capture.md).
- Прежние слова могут изменить решение → [Retrieval](references/retrieval.md).
- Явно заказанные Validation, Repair или backfill → [Integrity](references/integrity.md).

Квитанция возвращает к исходной работе; `capture-needed` сначала проходит Capture.
