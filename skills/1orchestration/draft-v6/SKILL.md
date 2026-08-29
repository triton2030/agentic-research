---
name: 1orchestration
description: >-
  Use before root assigns any subagent or splits work because cognitive load
  may be too high. Builds goal, acceptance, owner addresses and delta-only
  briefs; specialized controllers keep topology.
---

# Оркестрация

## Уникальный контекст

Оркестрация превращает работу в выполнимые когнитивные задачи, а не просто
открывает окна.
Нагрузка потока складывается из активных инструкций, ограничений, критериев и
знаний в точках решения; субъективная сложность и длина prompt-а её не заменяют.
Root видит всю owner-цепочку и интеграцию, а субагент — только свой срез.

## Цели

- До brief прочитаны все влияющие owner-источники.
- Каждый поток получил ясную цель, приёмку, адреса, невыводимую дельту и оценку
  активной нагрузки.
- Работа разделена до выполнимых потоков, а root собрал один доказанный результат.

## Протокол поведения

> «я это вижу как скилл развития когнитивной работы на более выполнимые списке
> задач».
>
> «мы не должны говорить ему что-то, что уже существует в каких-то файлах, но
> обязательно должны говорить, какие файлы ему надо прочитать».
>
> «И вот когда мы сформировали эти инструкции, следующий когнитивный шаг
> \<unk> это оценить, насколько много инструкций».

1. Для поручаемой работы нет карты влияющих owners → прочитай
   [sources](references/sources.md).
2. Карта owners есть, но provisional brief не сформирован → прочитай
   [brief](references/brief.md).
3. Brief сформирован, но его активная нагрузка не оценена → прочитай
   [budget](references/budget.md).
4. Нагрузка выше мягкого порога 20 либо работа субъективно слишком сцеплена →
   прочитай [decompose](references/decompose.md).
5. Все tasks признаны выполнимыми, но launch map не готова → прочитай
   [map](references/map.md).
6. Launch map готова, живого плана нет, а потеря root-контекста дороже
   переиздания волны → прочитай [carrier](references/carrier.md).
7. Карта и briefs готовы, обязательные возвраты ещё не получены → прочитай
   [execute](references/execute.md).
8. Обязательные возвраты получены → прочитай [accept](references/accept.md).
9. Обязательные возвраты приняты либо получили terminal blocker → прочитай
   [integrate](references/integrate.md).
10. Интеграция изменила task-file, carrier, решение или durable truth → прочитай
   [persist](references/persist.md).
11. Первый bounded wait не изменил названный return/artifact/diff → прочитай
   [repair](references/repair.md).
12. Оборвалось окно root → прочитай [recover-root](references/recover-root.md).

## Завершение

No-delegation обоснован оценённой нагрузкой либо обязательные returns приняты,
один результат интегрирован и durable state синхронизирован; terminal blocker назван.
