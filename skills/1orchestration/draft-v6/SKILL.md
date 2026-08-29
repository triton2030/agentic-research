---
name: 1orchestration
description: >-
  Use when a user or instruction needs root to orchestrate a general 2+
  subagent wave, or managed offload. Skip one ordinary worker/advisor/critic
  and 1fresh-eyes/1deep-agents waves.
---

# Оркестрация

## Уникальный контекст

Субагенты покупают независимость и чистоту контекста ценой координации.
Только root удерживает целую просьбу владельца, пользу для проекта,
траекторию, решения и интеграцию.

## Цели

- Выбрана минимальная окупающаяся форма.
- Каждое окно получило полный посильный контракт.
- Root собрал один доказанный результат, не отдав траекторию и решения.

## Протокол поведения

> «когда оркестратор вызывает субагента, он ему дает задачу и дает
> инструкции».
>
> «Я бы хотел бы туда добавить вывод прямо в чат, ну, как доказательство работы
> агента».

1. Форма ещё не выбрана → прочитай [admission](references/admission.md).
2. General wave допущена без живого плана, а потеря root-контекста стоит
   дороже переиздания волны → прочитай [carrier](references/carrier.md).
3. Форма допущена, но карта не готова → прочитай [map](references/map.md).
4. Карта готова, но briefs не выданы → прочитай [brief](references/brief.md).
5. Карта и briefs готовы, обязательные возвраты ещё не получены → прочитай
   [execute](references/execute.md).
6. Обязательные возвраты получены → прочитай [integrate](references/integrate.md).
7. Первый bounded wait не изменил названный return/artifact/diff → прочитай
   [repair](references/repair.md).
8. Оборвалось окно root → прочитай [recover-root](references/recover-root.md).

## Завершение

No-wave назван либо выход выбранной стадии достигнут; иного terminal у скила нет.
