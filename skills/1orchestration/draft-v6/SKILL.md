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
Оркестратор распределяет между окнами работу и instruction load, а root
удерживает просьбу владельца, пользу для проекта, траекторию, решения
и интеграцию.

## Цели

- Найдена минимальная окупающаяся форма: работа у root, один уже
  требуемый managed-offload поток либо общая волна.
- Каждое окно владеет посильным outcome, сфокусированными инструкциями
  своего момента, write ownership и проверяемым возвратом.
- Root принимает один результат по evidence, разрешает конфликты и не теряет
  траекторию в промежуточном шуме.

## Протокол поведения

> «когда оркестратор вызывает субагента, он ему дает задачу и дает
> инструкции».
>
> «Я бы хотел бы туда добавить вывод прямо в чат, ну, как доказательство работы
> агента».

1. Форма ещё не выбрана → прочитай [admission](references/admission.md).
2. General wave допущена без живого плана, а потеря root-контекста стоит
   дороже переиздания волны → прочитай [carrier](references/wave-folder.md).
3. Форма допущена, но карта и briefs не готовы → прочитай
   [prepare](references/prepare.md).
4. Карта и briefs готовы, обязательные возвраты ещё не получены → прочитай
   [execute](references/execute.md).
5. Обязательные возвраты получены → прочитай [integrate](references/integrate.md).
6. Первый bounded wait не изменил названный return/artifact/diff или оборвалось окно
   root → прочитай [repair](references/repair.md).

## Завершение

No-wave назван либо выход выбранной стадии достигнут; иного terminal у скила нет.
