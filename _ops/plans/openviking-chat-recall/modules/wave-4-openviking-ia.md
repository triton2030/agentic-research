---
kind: module-card
волна: 4
роль: read-only-upstream-analyst
модель: gpt-5.6-luna
thinking: max
---

# Модуль — официальный OpenViking prompt и IA

## Outcome

Установить точный upstream contract, который мы вправе и должны переиспользовать:
prompt sections, page types, directory index, L0/L1/L2 behavior, provenance и
лицензионная граница. Отделить это от поведения stock runtime.

## Оркестрация

- Сначала вызвать `$1orchestration`.
- Внутренние субагенты независимо проверяют upstream prompt/IA, текущую
  документацию и license/provenance; использовать только первичные источники.

## Ownership

- Репозиторий и upstream read-only; никаких правок и коммитов.
- Разрешён web для current authoritative sources.
- Любое отличие current `main` от pinned experiment version назвать явно.

## Ответить

1. Какой commit/file snapshot фиксировать и что дословно исполняет semantic
   generator?
2. Какие обязательства IA реально заданы skill, а какие создавал runtime?
3. Как именно устроены L0/L1/L2: уровень файла, директории или resource?
4. Что можно включить/адаптировать с явным attribution, а что нельзя копировать
   в локальный owner без дополнительного решения?

## Return

`THREAD_DONE` с direct URLs/commits, точными file/section addresses, reuse matrix
(`reuse`, `adapt`, `do not copy`) и минимальным provenance receipt. Inference
пометить как inference.
