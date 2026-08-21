---
kind: module-card
волна: 4b
роль: read-only-architecture-reconciler
модель: gpt-5.6-luna
thinking: max
---

# Модуль — seam Wiki L2 ↔ Context Layers L0/L1

## Outcome

Свести официальные Wiki pages и Context Layers в одну минимальную local file
topology без duplicate navigation, source-by-source summaries или второго
provenance owner.

## Оркестрация

- Сначала `$1orchestration`; внутренние субагенты отдельно атакуют topology и
  validator/rebuild seam.
- Репозиторий read-only; production code и docs не писать.

## Ответить

1. Какая exact output tree позволяет `index.md`, typed page directories и
   per-directory L0/L1 сосуществовать без циклического summary input?
2. Какой build order и digest invalidation нужны bottom-up?
3. Где compact record IDs обязательны, а где допустим directory-level source
   coverage?
4. Какие files/interfaces можно отдать параллельным writers после contracts?

## Return

`THREAD_DONE`: exact tree, stage DAG, interface schemas, invalidation rules,
writer footprints, falsifying tests, UNKNOWN и transferable observation.
