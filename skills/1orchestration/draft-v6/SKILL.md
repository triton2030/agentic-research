---
name: 1orchestration
description: >-
  Use before root assigns any subagent or splits cognitive work. Builds goal,
  acceptance, owner addresses, delta-only briefs and active-load verdicts;
  specialized controllers keep topology.
---

# Оркестрация

## Уникальный контекст

Оркестрация проектирует целую карту работы как выполнимые active sets всех
участников, включая root.

## Цели

- До brief прочитаны все влияющие owner-источники.
- Каждый участник получил выполнимый cognitive contract.
- Root закрыл одну evidence-backed orchestration с текущим state.

## Протокол поведения

1. Влияющие owners ещё не прочитаны → прочитай [orient](references/orient.md).
2. Owner map есть, но provisional brief не сформирован → прочитай
   [brief](references/brief.md).
3. Brief сформирован, но active-unit ledger не собран → прочитай
   [count](references/count.md).
4. Ledger есть, но verdict не вынесен → прочитай [budget](references/budget.md).
5. Любой actor получил verdict `decompose` →
   прочитай [decompose](references/decompose.md).
6. Все active sets выполнимы, но форма не выбрана → прочитай
   [shape](references/shape.md).
7. Выбрана собственная delegation topology, но launch map не готова → прочитай
   [map](references/map.md).
8. Launch map готова без живого state owner-а, а cold loss дороже переиздания →
   прочитай [carrier](references/carrier.md).
9. Собственная launch map готова, обязательные returns не получены → прочитай
   [execute](references/execute.md).
10. Обязательный return получен → прочитай [accept](references/accept.md).
11. Returns приняты либо получили terminal blocker → прочитай
   [integrate](references/integrate.md).

## Завершение

`no-delegation` или `controller-handoff` завершены после `shape`; собственная
delegation — после integration и синхронизации созданного state owner-а.
