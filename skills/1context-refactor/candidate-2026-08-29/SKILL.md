---
name: 1context-refactor
description: >-
  Use after recurring session errors, rework loops, needless search loops, or
  an explicit request to refactor context.
---

# Рефактор контекста

## Уникальный контекст

Повторная ошибка в длинной сессии может рождаться не в последнем действии, а в
любом уже загруженном слое: инструкции, скиле, документе, tool output, прежнем
ответе агента или словах владельца.

Это постфактум-метаскил. Предотвращение ещё не случившихся ошибок принадлежит
`1instruction-authoring`.

## Цель

Восстановить проверяемый механизм между действовавшим контекстом и повтором,
сохранить оплаченные маршруты через `1index`, а отложенные системные проблемы
через `1findings`, не расширяя полномочия автоматического вызова.

## Стадии

1. Для причинной трассы прочитай
   [типовые сигналы](references/failure-signals.md) и выпусти causal card.
2. Для доказанных результатов прочитай
   [сохранение postmortem](references/preservation.md).
3. Если исходный запрос разрешает source repair, выбери один reference:
   пересборка смыслов — [refactor](references/refactor.md); пересечения —
   [coherence](references/coherence.md); сокращение —
   [simplify](references/simplify.md); независимый аудит —
   [audit](references/audit.md).
4. После ремонта отложи его reference и отдельно примени
   [falsifying check](references/check.md) к заявленному поведенческому эффекту.

В один момент держи только тело и один reference.
