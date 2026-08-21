---
kind: module-card
волна: 3
роль: blind-reader
модель: gpt-5.6-luna
thinking: max
---

# Модуль — blind read offline Wiki

## Outcome

Проверить, может ли не видевший sources агент восстановить из
offline Wiki точную recurrence boundary и current OpenViking outcome, не
приписав этой поверхности stock runtime success.

## Blind boundary

- Читает только
  `experiments/openviking-chat-recall/artifacts/wiki-offline-diagnostic/**`.
- Не читает holders, typed input, gold manifest, receipt, plan, previous Wiki,
  Graphiti, git history и интернет.
- Read-only: не создаёт файлы и не коммитит.

## Вопросы

1. Сколько distinct source records поддерживают позицию «retrieval aid is
   not proof», каковы first/latest и какова current boundary?
2. Какой current outcome заказан для OpenViking chat-recall library?
   Перечисли все отдельные обязательства и evidence address для каждого.
3. Доказывает ли эта Wiki, что stock OpenViking Compile работает end-to-end
   и full corpus можно запускать сейчас? Ответь только по видимому evidence.

## Return schema

Для каждого вопроса: `answer`, `evidence addresses`, `confidence 0–100%`,
`unknowns`. В конце: `PASS` или `FAIL` по semantic recovery без суждения о
stock package quality.

## Root acceptance

- Question 1: exact `4`, exact first/latest, full-holder + later-holder boundary.
- Question 2: все пять outcome obligations без retrieval-only inversion.
- Question 3: нет confident stock/full-corpus claim; blocker/unknown назван.

Любой пропуск или confident unsupported claim — `FAIL`.
