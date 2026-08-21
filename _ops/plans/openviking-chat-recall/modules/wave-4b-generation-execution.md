---
kind: module-card
волна: 4b
роль: read-only-route-designer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — current build и reusable generation route

## Outcome

Развести два execution concern: как быстро собрать текущую библиотеку через
явно заказанные Luna Max worktree workers и какой CLI/provider adapter нужен
будущему reusable tool.

## Оркестрация

- Сначала `$1orchestration`; внутренние субагенты отдельно проектируют visible
  worker route и `codex exec` adapter/fake seam.
- Read-only; billable call, full corpus, edits и commits запрещены.

## Ответить

1. Что можно безопасно произвести file-disjoint Luna workers сейчас?
2. Какие hot files/manifests остаются у root/single writer?
3. Как fixture/fake доказывает adapter до реального sample call; какие auth,
   logging, cost и egress gates остаются?
4. Как resume/idempotency объединяет worker и future CLI outputs?

## Return

`THREAD_DONE`: две route cards, ownership map, cost/privacy gates, smoke plan,
recovery contract, UNKNOWN и максимум один transferable observation.
