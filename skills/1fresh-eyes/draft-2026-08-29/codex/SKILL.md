---
name: 1fresh-eyes
description: >-
  Use when a material trajectory fork in long work needs fresh views, fresh
  eyes are requested, or the user names one specialist profile such as auditor.
  Not for unnamed local/framework-gap review.
---

# Свежие Глаза

## Уникальный контекст

Долгая работа сужает рамку main; fresh stream проверяет тот же объект без интерпретации main и собственным способом.

## Цель пользователя

- Материальная развилка получает четыре независимых отчёта; явно названная роль — один native product.
- Панель ищет другие evidence paths, а не четыре варианта объяснения main.
- Владелец выбирает next/alternative/unchanged; критика может испортить хорошую работу, поэтому source-supported unchanged полноценен.

## Протокол поведения

> «должен вызываться во время длинной работы […] когда нам надо проверить траекторию движения»; цель — «чтобы агенты дали очень разные отчеты».

> «не будем использовать в скилле свежих глаз никаких других субагентов, кроме вот этих трёх»; «У нас три агента […] и 4 агент премортем».

## Ход

1. Назови вопрос на столе.
2. Назови решение, которое изменит ответ.
3. Назови конечный результат из GOAL/Product Frames; при пробеле выведи professional outcome из доступного evidence.
4. Decision anchor → frozen packet: прочитай [packet](references/packet.md).
5. Если mode `named` и profile `premortem`, packet → terminal native outcome: прочитай [Premortem](references/premortem.md), верни outcome и останови Fresh Eyes pass.
6. Если mode `named` с другим profile, packet → terminal native product: прочитай [named](references/named.md); wrong premise исправь через [steering](references/steering.md), верни native product и останови Fresh Eyes pass.
7. Иначе frozen Premortem packet → terminal cross-family outcome: прочитай [Premortem](references/premortem.md); blocker останавливает panel pass как `panel_incomplete`.
8. Terminal Premortem report + native packets → three terminal native reports: прочитай [native panel](references/panel.md).
9. Wrong premise в panel report → repaired report: прочитай [steering](references/steering.md) и замени исходный report.
10. Four stable panel reports → decision handback: прочитай [synthesis](references/synthesis.md).
