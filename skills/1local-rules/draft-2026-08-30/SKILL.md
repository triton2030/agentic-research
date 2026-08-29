---
name: 1local-rules
description: >-
  Use when creating, updating, or retiring a project-local 2* rule skill for
  one observable project action, including after project context changes.
---

# Локальные правила

## Цель

Приведи project-local rule-skill `2*` и обе его проекции к доказанно нужному
состоянию.

## Уникальный контекст

`2*` связывает выцветающее до действия правило проекта с его точным моментом и
зеркалом Claude↔Codex.

## Выбери текущий режим

Работай как конечный автомат: одно текущее состояние — один reference, а его
результат определяет следующее состояние.

1. Решается, нужен ли новый или существующий `2*`, в том числе после изменения
   цели, scope, структуры проекта или локальных правил →
   [Допуск](references/admission.md).
2. Принято желаемое состояние `present` → [Форма](references/form.md).
3. Кандидат готов к structural и trigger-проверке →
   [Проверка кандидата](references/candidate-checks.md).
4. Structural и trigger-проверка пройдены →
   [Поведенческое доказательство](references/behavior-proof.md).
5. Состояние `present` доказано → [Установка](references/install.md).
6. Принято желаемое состояние `absent` → [Снятие](references/retire.md).
