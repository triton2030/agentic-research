---
name: 1chat-recall
description: >-
  When owner speech needs attention.
---

# Память чата

## Цель

Сделать слова владельца находимым evidence для одного решения; при слабом
evidence вернуть `abstain` или gap, а не профиль, current truth или догадку.

## Уникальный контекст

Находимость держат три независимых индекса: описание boundary в `topics.md`
ведёт к теме, полный актуальный `session-context` — к файлу разговора, короткий
keyword-like `context-note` — к цитате. Ни один индекс не является owner speech
или current truth. Позднее слово либо действующий owner могут изменить прежнюю
позицию; Retrieval показывает каждой цитате абсолютную дату и возраст, а
same-scope `supersedes` оставляет действующей новую. User-visible carrier
не доказывает авторство: tool-sent agent follow-up не является owner speech.

## Режим

- Материальная речь либо `capture-needed` → [Capture](references/capture.md).
- Прежние слова могут изменить решение → [Retrieval](references/retrieval.md).
- Validation, Repair или backfill → [Integrity](references/integrity.md).

Квитанция возвращает к исходной работе; `capture-needed` сначала проходит Capture.
