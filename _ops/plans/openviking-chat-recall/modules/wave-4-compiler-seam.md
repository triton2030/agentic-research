---
kind: module-card
волна: 4
роль: read-only-designer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — compiler seam и file ownership

## Outcome

Спроектировать минимальный batch pipeline вокруг существующего typed-evidence
probe: exact module seams, CLI contracts, artifact flow, tests и disjoint
writer footprints для вехи 2.

## Оркестрация

- Сначала вызвать `$1orchestration`.
- Внутренними субагентами независимо исследовать текущий код/тесты и варианты
  artifact/state topology; агрегатор обязан назвать расхождения.

## Ownership

- Репозиторий read-only; никаких правок и коммитов.
- Читает только task/plan, `experiments/openviking-chat-recall/**` и ближайшие
  experiment instructions.
- Не проектирует обобщённый framework за пределами текущего корпуса.

## Ответить

1. Что из `build_inventory.py` и `build_typed_probe.py` остаётся owner, что
   заменяется и почему?
2. Какие interfaces разделяют inventory, clustering, semantic generation,
   page rendering, validation, resume и receipts?
3. Какие exact files можно отдать параллельным writers без общего hot file?
4. Какой самый маленький representative sample и falsifying test допускает
   full build?

## Return

`THREAD_DONE` с предложенным file tree, interface/data schemas, dependency DAG,
writer cards/footprints и проверками. Не писать production code.
