---
kind: module-card
волна: 4b
роль: read-only-upstream-analyst
модель: gpt-5.6-luna
thinking: max
---

# Модуль — L0/L1 prompt и generation contract

## Outcome

Найти exact official source owners для L0/L1: prompt templates, input/output
schemas, token limits, bottom-up aggregation и current/pinned drift. Вернуть
минимальный reproducible snapshot contract для custom compiler.

## Оркестрация

- Сначала `$1orchestration`; минимум два внутренних субагента: prompt/code и
  docs/tests. Только primary OpenViking sources.
- Read-only; никаких edits, commits или runtime запуска.

## Ответить

1. Какие exact YAML/code files генерируют `.abstract.md` и `.overview.md`?
2. На каком уровне создаются sidecars: file, directory, session; какие inputs и
   budgets?
3. Что совпадает/дрейфует между `v0.4.16` и current main?
4. Что snapshot/reuse/adapt/do-not-copy с attribution и license boundary?

## Return

`THREAD_DONE`: primary URLs/commits/digests, prompt/schema excerpts адресами,
generation DAG, reuse matrix, UNKNOWN и максимум один transferable observation.
